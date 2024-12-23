import webbrowser

import numpy as np
import pyqtgraph as pg
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QFileDialog,
    QLabel,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)
from pyqtgraph import ImageView, InfiniteLine

from core.annotations_handler import AnnotationTool
from core.cdss_worker import CDSSWorker
from core.comparison_renderer import ComparisonRenderer
from core.image_enhancer import ImageEnhancer
from core.image_loader import ImageLoader
from core.image_processor import ImageProcessor
from core.measurements_handler import MeasurementTools
from core.volume_renderer import VolumeRenderer
from ui.denoising_dialog import DenoisingDialogUI
from ui.main_window import MainWindowUI
from ui.notification_list import NotificationListDialog
from ui.smoothing_sharpening_dialog import SmoothingAndSharpeningDialogUI
from ui.windowing_parameters_dialog import WindowingDialogUI
from utils.file_history_manager import FileHistoryManager


class DicomViewerBackend(QMainWindow, MainWindowUI):
    def __init__(self):
        super().__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        # Image Data
        self.original_image_3d = None
        self.original_spacing_info = None
        self.windowed_image = None
        self.smoothed_image = None
        self.sharpened_image = None
        self.denoised_image = None

        # Viewers and Views
        self.crosshairs = {}
        self.views = {
            "axial": self.ui.axial_view,
            "sagittal": self.ui.sagittal_view,
            "coronal": self.ui.coronal_view,
        }
        self.viewers = {
            "axial": self.ui.axial_viewer,
            "sagittal": self.ui.sagittal_viewer,
            "coronal": self.ui.coronal_viewer,
        }

        # Critical Components:
        # Objects for processing images and saving loading history
        self.image_processor = ImageProcessor()
        self.file_history_manager = FileHistoryManager(
            self.ui.menuFile, self.import_image
        )

        # For Measurement and Annotation Tools
        self._active_viewer = None
        self.measurement_handler = MeasurementTools(self)
        self.annotation_handler = AnnotationTool(self)
        self.current_active_measurement = None

        # Calling Setup Methods
        self.init_ui_connections()
        self.setup_viewer_tracking()

        # CDSS
        self.prediction = None
        self.cdss_worker = CDSSWorker()
        self.cdss_worker.prediction_signal.connect(self.get_prediction_label)

    def init_ui_connections(self):
        # File Menu
        self.ui.actionImport_Image.triggered.connect(lambda: self.import_image(None))
        self.ui.actionImport_NIFTI.triggered.connect(lambda: self.import_image("nii"))
        self.ui.actionImport_DICOM_Series.triggered.connect(
            lambda: self.import_image("series")
        )
        self.ui.actionImport_Sample_Image.triggered.connect(
            lambda: self.import_image(
                "nii", "assets/data/nifti/subject-01-flanker.nii.gz"
            )
        )
        self.ui.actionImport_png.triggered.connect(lambda: self.import_image("png"))
        self.ui.actionQuit_App.triggered.connect(self.exit_app)

        # View Menu: Measurement Tools
        self.ui.actionRuler.triggered.connect(self.start_ruler_measurement)
        self.ui.actionAngle.triggered.connect(self.start_angle_measurement)

        # Image Menu: Image Adjustments and 3D Features
        self.ui.actionWindowing.triggered.connect(self.windowing)
        self.ui.actionSmoothing.triggered.connect(
            lambda: self.smoothing_and_sharpening("Smoothing")
        )
        self.ui.actionSharpening.triggered.connect(
            lambda: self.smoothing_and_sharpening("Sharpening")
        )
        self.ui.actionDenoising.triggered.connect(self.denoising)
        self.ui.actionBuild_Surface.triggered.connect(self.build_surface)
        self.ui.actionComparison_Mode.triggered.connect(self.comparison_mode)

        # Help Menu
        self.ui.actionDocumentation.triggered.connect(self.open_docs)

        # Add new connections for measurement tools & ROI (View Menu)
        self.ui.actionRuler.triggered.connect(self.start_ruler_measurement)
        self.ui.actionAngle.triggered.connect(self.start_angle_measurement)

        # Connect Ruler toggle
        self.ui.showRuler.toggled.connect(
            lambda checked: self.measurement_handler.toggle_ruler(
                self.get_active_viewer(), checked
            )
        )
        # Connect Angle toggle
        self.ui.showAngle.toggled.connect(
            lambda checked: self.measurement_handler.toggle_angle(
                self.get_active_viewer(), checked
            )
        )

        # Annotation actions
        self.ui.actionAdd_Text_Annotation.triggered.connect(self.add_text_annotation)
        self.ui.actionSave_Text_Annotation.triggered.connect(self.save_text_annotation)
        self.ui.actionLoad_Text_Annotation.triggered.connect(self.load_text_annotation)
        self.ui.actionClear_Annotations.triggered.connect(self.clear_annotations)

        # Help Menu: Documentation
        self.ui.actionDocumentation.triggered.connect(self.open_docs)

        # Overlay Toolbar
        self.ui.contrast_slider.valueChanged.connect(self.update_contrast)

        # Ortho Toolbar
        self.ui.camera_button.clicked.connect(self.screenshot)
        self.ui.tracking_button.toggled.connect(self.setup_crosshairs)
        self.ui.reload_button.clicked.connect(
            lambda: self.display_views(self.original_image_3d)
        )
        self.ui.notification_button.clicked.connect(
            self.display_prediction_notification
        )

    ## File Menu ##
    ##===========##
    def import_image(self, image_type, path=None):
        try:
            if image_type == None:
                path = path or self.get_path(
                    "All Files (*);;NIfTI Files (*.nii *.nii.gz);;DICOM Files (*.dcm)"
                )
                if not path:
                    return

                self.original_image_3d, self.original_spacing_info = (
                    ImageLoader.load_image(path)
                )

            elif image_type == "nii":
                path = path or self.get_path("NIfTI Files (*.nii *.nii.gz)")
                if not path:
                    return

                self.original_image_3d, self.original_spacing_info = (
                    ImageLoader.load_nifti(path)
                )

            elif image_type == "series":
                path = path or QFileDialog.getExistingDirectory(
                    self, "Select DICOM Directory"
                )
                if not path:
                    return

                self.original_image_3d, self.original_spacing_info = (
                    ImageLoader.load_dicom_series(path)
                )

            elif image_type == "png":
                path = path or self.get_path("PNG Files (*.png)")
                if not path:
                    return

                self.original_image_3d, _ = ImageLoader.load_png(path)
                self.display_image(self.original_image_3d)
                return

            self.set_initial_slices(self.original_image_3d)
            self.append_image_to_history(path, image_type)

            self.display_views(self.original_image_3d)

        except Exception as e:
            self.show_error_message(str(e))

    def exit_app(self):
        self.close()

    ## Image Menu ##
    ##============##
    # Windowing
    def windowing(self):
        window_level, window_width = self.show_windowing_dialog()

        # Check if valid values were returned
        if window_level is not None and window_width is not None:
            for plane, viewer in self.viewers.items():
                target_slice = self.image_processor.get_slice(plane)

                windowed_image = ImageEnhancer.apply_window(
                    target_slice,
                    window_level,
                    window_width,
                )

                # Render the slice in the viewer
                self.render_slice(viewer, windowed_image)

    def show_windowing_dialog(self):
        windowing_dialog = WindowingDialogUI(self)
        if windowing_dialog.exec_():
            window_level, window_width = windowing_dialog.get_parameters()
            return window_level, window_width
        return None, None  # Return None if dialog is rejected

    # Smoothing and Sharpening
    def smoothing_and_sharpening(self, mode):
        if mode == "Smoothing":
            sigma, strength = self.show_smoothing_dialog()

            if sigma is not None and strength is not None:
                for plane, viewer in self.viewers.items():
                    target_slice = self.image_processor.get_slice(plane)

                    smoothed_slice = ImageEnhancer.smooth_image(
                        target_slice, sigma, strength
                    )

                    # Render the slice in the viewer
                    self.render_slice(viewer, smoothed_slice)

        elif mode == "Sharpening":
            strength = self.show_sharpening_dialog()

            if strength is not None:
                for plane, viewer in self.viewers.items():
                    target_slice = self.image_processor.get_slice(plane)

                    sharpend_image = ImageEnhancer.sharpen_image(target_slice, strength)

                    # Render the slice in the viewer
                    self.render_slice(viewer, sharpend_image)

    def show_smoothing_dialog(self):
        smoothing_dialog = SmoothingAndSharpeningDialogUI(mode="Smoothing", parent=self)
        if smoothing_dialog.exec_():
            sigma, smoothing_strength = smoothing_dialog.get_parameters("Smoothing")
            return sigma, smoothing_strength
        return None, None

    def show_sharpening_dialog(self):
        sharpening_dialog = SmoothingAndSharpeningDialogUI(
            mode="Sharpening", parent=self
        )
        if sharpening_dialog.exec_():
            sharpening_strength = sharpening_dialog.get_parameters("Sharpening")
            return sharpening_strength
        return None

    # Denoising
    def denoising(self):
        filter_type, parameters = self.show_denoising_dialog()

        if filter_type is not None and parameters is not None:
            for plane, viewer in self.viewers.items():
                target_slice = self.image_processor.get_slice(plane)

                denoised_image = ImageEnhancer.denoise(
                    target_slice,
                    filter_type,
                    parameters,
                )

                # Render the slice in the viewer
                self.render_slice(viewer, denoised_image)

    def show_denoising_dialog(self):
        denoising_dialog = DenoisingDialogUI(self)

        if denoising_dialog.exec_():
            filter_type, parameters = denoising_dialog.get_parameters()
            return filter_type, parameters
        return None

    # 3D Features
    def build_surface(self):
        self.volume_renderer = VolumeRenderer()
        render_window, render_ineractor, _ = (
            self.volume_renderer.create_volume_renderer(
                self.original_image_3d,
                self.original_spacing_info,
            )
        )
        render_window.Render()
        render_ineractor.Start()

    def comparison_mode(self):
        data_1_path = self.get_path("NIfTI Files (*.nii *.nii.gz)")
        data_2_path = self.get_path("NIfTI Files (*.nii *.nii.gz)")

        if not data_1_path or not data_2_path:
            return

        data_1, spacing_1 = ImageLoader.load_nifti(data_1_path)
        data_2, spacing_2 = ImageLoader.load_nifti(data_2_path)

        self.comparison_renderer = ComparisonRenderer()
        render_window, render_interactor = (
            self.comparison_renderer.create_comparison_mode_renderer(
                data_1, data_2, spacing_1, spacing_2
            )
        )

        render_window.Render()
        render_interactor.Start()

    ## Help Menu ##
    ##===========##
    def open_docs(self):
        webbrowser.open(
            "https://github.com/hagersamir/DICOM-Viewer-Features/blob/main/README.md"
        )

    ## Ortho Toolbar ##
    ##===============##
    def screenshot(self):
        if self.original_image_3d is None:
            self.show_error_message("No image data to capture.")
            return

        for plane, viewer in self.viewers.items():
            viewer.export(fileName=f"screenshot_{plane}.png")

    ## Viewer Feature ##
    ##================##
    def render_slice(self, image_view: ImageView, slice_data):
        rotated_slice = np.rot90(slice_data, k=2)

        image_view.setImage(
            rotated_slice.T,
            autoRange=True,
            autoLevels=True,
            autoHistogramRange=True,
        )

    def display_views(self, image_data):
        if image_data is None:
            self.show_error_message("No image data to display.")
            return

        for plane, viewer in self.viewers.items():
            slice_data = self.image_processor.get_slice(plane)
            width, height = slice_data.shape

            # Pass the loaded NIfTI image to the CDSS worker
            self.cdss_worker.set_slice(slice_data)
            self.cdss_worker.start()

            # Render the slice in the viewer
            self.render_slice(viewer, slice_data)

            # Explicitly set independent ranges for each viewer
            viewer.getView().setRange(
                xRange=(0, width),
                yRange=(0, height),
                padding=0,
            )

            if width > height:
                target = width
            else:
                target = height

            viewer.getView().setLimits(
                xMin=0,
                xMax=target,
                yMin=0,
                yMax=target,
            )

    def display_image(self, image_data):
        if image_data is None:
            self.show_error_message("No image data to display.")
            return

        width, height = image_data.shape

        # Pass the loaded NIfTI image to the CDSS worker
        self.cdss_worker.set_slice(image_data)
        self.cdss_worker.start()

        # Render the slice in the viewer
        self.render_slice(self.ui.sagittal_viewer, image_data)

        # Explicitly set independent ranges for each viewer
        self.ui.sagittal_viewer.getView().setRange(
            xRange=(0, width),
            yRange=(0, width),
            padding=0,
        )

    def update_contrast(self, value):
        try:
            # Map slider value to a contrast range
            # Example: Assuming slider range is -50 to 50
            contrast_range = 1 + value / 100.0  # Adjust as needed

            # Adjust the contrast for all viewers
            for plane, viewer in self.viewers.items():
                # Get the histogram of the current viewer
                histogram = viewer.getHistogramWidget()

                # Get current min and max intensity of the image
                image_data = self.image_processor.get_slice(plane)
                min_intensity = np.min(image_data)
                max_intensity = np.max(image_data)

                # Calculate new levels based on contrast range
                intensity_center = (min_intensity + max_intensity) / 2
                new_min = (
                    intensity_center
                    - (intensity_center - min_intensity) * contrast_range
                )
                new_max = (
                    intensity_center
                    + (max_intensity - intensity_center) * contrast_range
                )

                # Apply the levels to the histogram
                histogram.setLevels(new_min, new_max)

                # Optionally, adjust the displayed image
                viewer.getView().setLimits(
                    xMin=0, xMax=image_data.shape[1], yMin=0, yMax=image_data.shape[0]
                )
        except Exception as e:
            self.show_error_message(f"Error adjusting contrast: {str(e)}")

    ## MPR Feature ##
    ##=============##
    def setup_crosshairs(self):
        if self.ui.tracking_button.isChecked():
            # Enable crosshairs
            if self.original_image_3d is None:
                return

            width, height, _ = self.original_image_3d.shape

            for plane, view in self.views.items():
                h_line = InfiniteLine(pos=width / 2, angle=0, movable=False, pen="b")
                v_line = InfiniteLine(pos=height / 2, angle=90, movable=False, pen="b")
                view.addItem(h_line)
                view.addItem(v_line)
                self.crosshairs[plane] = {"h_line": h_line, "v_line": v_line}

            for plane, viewer in self.viewers.items():
                viewer.scene.sigMouseMoved.connect(
                    lambda event, p=plane: self.update_crosshairs(p, event)
                )
        else:
            # Disable crosshairs and reset
            for plane, view in self.views.items():
                if plane in self.crosshairs:
                    view.removeItem(self.crosshairs[plane]["h_line"])
                    view.removeItem(self.crosshairs[plane]["v_line"])
            self.crosshairs.clear()

            for viewer in self.viewers.values():
                viewer.scene.sigMouseMoved.disconnect()

    def update_crosshairs(self, plane, event):
        try:
            # Map mouse position to viewer coordinates
            mouse_point = self.viewers[plane].getView().mapSceneToView(event)
            x = int(mouse_point.x())
            y = int(mouse_point.y())

            # Ensure coordinates are within bounds
            x = max(0, min(x, self.original_image_3d.shape[2] - 1))
            y = max(0, min(y, self.original_image_3d.shape[1] - 1))

            # Determine new slice indices based on the current plane
            if plane == "axial":
                z = self.image_processor.current_slices["axial"]
                self.image_processor.update_slice("sagittal", x)
                self.image_processor.update_slice("coronal", y)
            elif plane == "sagittal":
                z = x
                x = self.image_processor.current_slices["sagittal"]
                self.image_processor.update_slice("axial", y)
                self.image_processor.update_slice("coronal", x)
            elif plane == "coronal":
                z = y
                y = self.image_processor.current_slices["coronal"]
                self.image_processor.update_slice("axial", y)
                self.image_processor.update_slice("sagittal", x)

            # Update the axial plane slice explicitly
            self.image_processor.update_slice("axial", z)

            # Update crosshairs
            for p, crosshair in self.crosshairs.items():
                if p == "axial":
                    crosshair["h_line"].setPos(
                        self.image_processor.current_slices["coronal"]
                    )
                    crosshair["v_line"].setPos(
                        self.image_processor.current_slices["sagittal"]
                    )
                elif p == "sagittal":
                    crosshair["h_line"].setPos(
                        self.image_processor.current_slices["axial"]
                    )
                    crosshair["v_line"].setPos(
                        self.image_processor.current_slices["coronal"]
                    )
                elif p == "coronal":
                    crosshair["h_line"].setPos(
                        self.image_processor.current_slices["axial"]
                    )
                    crosshair["v_line"].setPos(
                        self.image_processor.current_slices["sagittal"]
                    )

            # Update coordinate fields
            self.ui.x_value.setText(str(x))
            self.ui.y_value.setText(str(y))
            self.ui.z_value.setText(str(z))

            # Get and display the voxel value
            voxel_value = self.original_image_3d[z, y, x]
            self.ui.voxel_value.setText(str(voxel_value))

            # Refresh all viewers
            self.refresh_slices()
        except Exception as e:
            self.show_error_message(f"Error updating crosshairs: {str(e)}")

    def refresh_slices(self):
        for plane in self.viewers.keys():
            slice_data = self.image_processor.get_slice(plane)
            self.render_slice(self.viewers[plane], slice_data)

    def update_location_display(self, x, y, z):
        try:
            # Update coordinates
            self.ui.x_value.setText(str(x))
            self.ui.y_value.setText(str(y))
            self.ui.z_value.setText(str(z))

            # Get the voxel value
            voxel_value = self.image_processor.image_data[z, y, x]
            self.ui.voxel_value.setText(str(voxel_value))
        except Exception as e:
            self.show_error_message(f"Error fetching voxel data: {str(e)}")

    ## Annotation Tools ##
    ##==================##
    def add_text_annotation(self):
        """Add a text annotation to the current active viewer."""
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.annotation_handler.add_text_annotation(active_viewer)

    def save_text_annotation(self):
        """Save annotations."""
        self.annotation_handler.save_annotations()

    def load_text_annotation(self):
        """Load annotations."""
        self.annotation_handler.load_annotations()

    def clear_annotations(self):
        """Clear annotations for the current active viewer."""
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.annotation_handler.clear_annotations(active_viewer)

    ## Measurement Tools ##
    ##===================##
    def start_ruler_measurement(self):
        """
        Activate ruler measurement tool on the current active viewer.
        """
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.current_active_measurement = self.measurement_handler.create_ruler(
                active_viewer
            )

            # Ensure the "Show Ruler" checkbox is checked
            if not self.ui.showRuler.isChecked():
                self.ui.showRuler.setChecked(True)

    def start_angle_measurement(self):
        """
        Activate angle measurement tool on the current active viewer.
        """
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.current_active_measurement = (
                self.measurement_handler.create_angle_measurement(active_viewer)
            )

            # Ensure the "Show Angle" checkbox is checked
            if not self.ui.showAngle.isChecked():
                self.ui.showAngle.setChecked(True)

    ## CDSS ##
    ##======##
    def get_prediction_label(self, result):
        self.prediction = result
        self.ui.notification_button.setIcon(QIcon("./assets/icons/notification_1.png"))

    def display_prediction_notification(self):
        notification_dialog = NotificationListDialog(self)
        prediction_label = QLabel(f"The AI companion predicted:\n{self.prediction}")

        # Create a QListWidgetItem and set its size hint
        list_item = QListWidgetItem()
        list_item.setSizeHint(
            prediction_label.sizeHint() * 2
        )  # Adjust multiplier as needed

        notification_dialog.notificationList.addItem(list_item)
        notification_dialog.notificationList.setItemWidget(list_item, prediction_label)

        if notification_dialog.exec_():
            self.ui.notification_button.setIcon(
                QIcon("./assets/icons/notification.png")
            )

    ## Utils ##
    ##=======##
    def reload(self):
        self.display_views(self.original_image_3d)
        self.measurement_handler.toggle_ruler(self.get_active_viewer(), False)
        self.measurement_handler.toggle_angle(self.get_active_viewer(), False)

    def get_path(self, file_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", file_type
        )
        return file_path

    def set_initial_slices(self, image_data):
        self.image_processor.set_image_data(image_data=image_data)

    def append_image_to_history(self, image_path, image_format):
        self.file_history_manager.add_to_history(image_path, image_format)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    def closeEvent(self, event):
        for viewer in [
            self.ui.axial_viewer,
            self.ui.sagittal_viewer,
            self.ui.coronal_viewer,
        ]:
            viewer.close()
        # Explicitly accept the close event (optional)
        event.accept()

    def setup_viewer_tracking(self):
        """
        Setup mouse tracking and focus events for viewers.
        """
        for viewer in self.viewers.values():
            # Enable mouse tracking
            viewer.getView().scene().sigMouseMoved.connect(
                lambda pos, v=viewer: self.on_viewer_mouse_move(v, pos)
            )

    def on_viewer_mouse_move(self, viewer, pos):
        """
        Handle mouse movement over a viewer.
        """
        # Optionally update the active viewer when mouse moves
        self.set_active_viewer(viewer)

    def set_active_viewer(self, viewer):
        """
        Set the currently active viewer.
        """
        # Deselect previous viewer
        if self._active_viewer:
            self._active_viewer.getView().setBorder(None)

        # Set new active viewer
        self._active_viewer = viewer

        # Optionally highlight the active viewer
        viewer.getView().setBorder(pg.mkPen(color="green", width=5))

        return viewer

    def get_active_viewer(self):
        """
        Get the currently active viewer.
        Default to axial viewer if no viewer is active.
        """
        return self._active_viewer or self.ui.axial_viewer

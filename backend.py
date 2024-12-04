import webbrowser

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QDialog, QFileDialog, QMainWindow, QMessageBox
from pyqtgraph import ImageView, InfiniteLine

from core.annotations_handler import AnnotationTool
from core.comparison_renderer import ComparisonRenderer
from core.image_enhancer import ImageEnhancer
from core.image_loader import ImageLoader
from core.image_processor import ImageProcessor
from core.measurements_handler import MeasurementTools
from core.volume_renderer import VolumeRenderer
from ui.denoising_dialog import DenoisingDialogUI
from ui.main_window import MainWindowUI
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
        self.measurement_tools = MeasurementTools(self)
        self.annotation_tool = AnnotationTool(self)
        self.current_active_measurement = None

        # Calling Setup Methods
        self.init_ui_connections()
        self.setup_viewer_tracking()

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
            lambda checked: self.measurement_tools.toggle_ruler(
                self.get_active_viewer(), checked
            )
        )
        # Connect Angle toggle
        self.ui.showAngle.toggled.connect(
            lambda checked: self.measurement_tools.toggle_angle(
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
        self.ui.tracking_button.clicked.connect(self.setup_crosshairs)
        self.ui.reload_button.clicked.connect(
            lambda: self.display_views(self.original_image_3d)
        )

    def setup_viewer_tracking(self):
        """
        Setup mouse tracking and focus events for viewers.
        """
        viewers = [
            self.ui.axial_viewer,
            self.ui.sagittal_viewer,
            self.ui.coronal_viewer,
        ]

        for viewer in viewers:
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

    def start_ruler_measurement(self):
        """
        Activate ruler measurement tool on the current active viewer.
        """
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.current_active_measurement = self.measurement_tools.create_ruler(
                active_viewer
            )

    def start_angle_measurement(self):
        """
        Activate angle measurement tool on the current active viewer.
        """
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.current_active_measurement = (
                self.measurement_tools.create_angle_measurement(active_viewer)
            )

    def add_text_annotation(self):
        """Add a text annotation to the current active viewer."""
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.annotation_tool.add_text_annotation(active_viewer)

    def save_text_annotation(self):
        """Save annotations."""
        self.annotation_tool.save_annotations()

    def load_text_annotation(self):
        """Load annotations."""
        self.annotation_tool.load_annotations()

    def clear_annotations(self):
        """Clear annotations for the current active viewer."""
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.annotation_tool.clear_annotations(active_viewer)

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
            self.windowed_image = ImageEnhancer.apply_window(
                self.original_image_3d, window_level, window_width
            )
            self.display_views(self.windowed_image)

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
                self.smoothed_image = ImageEnhancer.smooth_image(
                    self.original_image_3d, sigma, strength
                )

                self.display_views(self.smoothed_image)

        elif mode == "Sharpening":
            strength = self.show_sharpening_dialog()

            if strength is not None:
                self.sharpened_image = ImageEnhancer.sharpen_image(
                    self.original_image_3d, strength
                )

                self.display_views(self.sharpened_image)

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
        if sharpening_dialog.exec_() == QDialog.accepted:
            sharpening_strength = sharpening_dialog.get_parameters("Sharpening")
            return sharpening_strength
        return None

    # Denoising
    def denoising(self):
        filter_type, parameters = self.show_denoising_dialog()

        if filter_type is not None and parameters is not None:
            self.denoised_image = ImageEnhancer.denoise(
                self.original_image_3d, filter_type, parameters
            )

            self.display_views(self.denoised_image)

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

    def update_crosshairs(self, plane, event):
        try:
            # Map mouse position to viewer coordinates
            mouse_point = self.viewers[plane].getView().mapSceneToView(event)
            x = int(mouse_point.x())
            y = int(mouse_point.y())

            # Ensure coordinates are within bounds
            x = max(0, min(x, self.original_image_3d.shape[2] - 1))
            y = max(0, min(y, self.original_image_3d.shape[1] - 1))

            # Determine z-coordinate based on the current plane
            if plane == "axial":
                z = self.image_processor.current_slices["axial"]
            elif plane == "sagittal":
                z = x
                x = self.image_processor.current_slices["sagittal"]
            elif plane == "coronal":
                z = y
                y = self.image_processor.current_slices["coronal"]

            # Update crosshairs
            self.crosshairs[plane]["h_line"].setPos(y)
            self.crosshairs[plane]["v_line"].setPos(x)

            # Update slice indices in ImageProcessor
            if plane == "axial":
                self.image_processor.update_slice("sagittal", x)
                self.image_processor.update_slice("coronal", y)
            elif plane == "sagittal":
                self.image_processor.update_slice("axial", y)
                self.image_processor.update_slice("coronal", x)
            elif plane == "coronal":
                self.image_processor.update_slice("axial", y)
                self.image_processor.update_slice("sagittal", x)

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

    ## Utils ##
    ##=======##
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

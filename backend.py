import webbrowser

import numpy as np
from PyQt5.QtWidgets import QDialog, QFileDialog, QMainWindow, QMessageBox, QInputDialog
import pyqtgraph as pg
from pyqtgraph import ROI, ImageView, InfiniteLine, ViewBox

from core.comparison_renderer import ComparisonRenderer
from core.image_enhancer import ImageEnhancer
from core.image_loader import ImageLoader
from core.image_processor import ImageProcessor
from core.volume_renderer import VolumeRenderer
from core.measurements_annotations import MeasurementTools, AnnotationTool
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

        # Initialize components
        self._active_viewer = None
        self.loaded_image_data = None
        self.spacing_info = None
        self.image_loader = ImageLoader()
        self.image_processor = ImageProcessor()
        
        self.viewers = {
            "axial": self.ui.axial_viewer,
            "sagittal": self.ui.sagittal_viewer,
            "coronal": self.ui.coronal_viewer,
        }
        self.views = {
            "axial": self.ui.axial_view,
            "sagittal": self.ui.sagittal_view,
            "coronal": self.ui.coronal_view,
        }

        # Measurement and Annotation Tools
        self.measurement_tools = MeasurementTools(self)
        self.annotation_tool = AnnotationTool(self)

        # UI Variables
        self.crosshairs = {}
        self.current_active_measurement = None

        # File history management
        self.file_history_manager = FileHistoryManager(
            self.ui.menuFile, self.import_image
        )

        # Connect UI actions
        self.init_ui_connections()

        # Setup crosshairs
        self.setup_crosshairs()
        
        # Setup mouse tracking and focus events
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

        # Image Menu
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
        
        #Annotation actions (Annotation Menu)
        self.ui.actionAdd_Text_Annotation.triggered.connect(self.add_text_annotation)
        self.ui.actionSave_Text_Annotation.triggered.connect(self.load_text_annotation)
        self.ui.actionLoad_Text_Annotation.triggered.connect(self.save_text_annotation)
        self.ui.actionDelete_Text_Annotation.triggered.connect(self.delete_text_annotation)
        self.ui.actionClear_Measurements.triggered.connect(self.clear_all)

    def setup_viewer_tracking(self):
        """
        Setup mouse tracking and focus events for viewers.
        """
        viewers = [
            self.ui.axial_viewer, 
            self.ui.sagittal_viewer, 
            self.ui.coronal_viewer
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
        viewer.getView().setBorder(pg.mkPen(color='green', width=2))
        
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
            self.current_active_measurement = self.measurement_tools.create_ruler(active_viewer)

    def start_angle_measurement(self):
        """
        Activate angle measurement tool on the current active viewer.
        """
        active_viewer = self.get_active_viewer()
        if active_viewer:
            self.current_active_measurement = self.measurement_tools.create_angle_measurement(active_viewer)

    def add_text_annotation(self):
        """
        Add a text annotation to the current active viewer.
        """
        try:
            active_viewer = self.get_active_viewer()
            if active_viewer:
                # Prompt the user for annotation text 
                annotation_text, ok = QInputDialog.getText(
                    self, 
                    "Add Text Annotation", 
                    "Enter annotation text:"
                )
                
                if ok and annotation_text:
                    # Define a default position for the annotation
                    default_position = (50, 50)  # Example coordinates

                    # Create the text annotation
                    annotation = self.annotation_tool.add_text_annotation(
                        active_viewer, 
                        annotation_text, 
                        default_position
                    )

                    # Log the action
                    print(f"Text annotation added at position {default_position} with text: '{annotation_text}'")
            else:
                self.show_error_message("No active viewer found to add the text annotation.")
        except Exception as e:
            self.show_error_message(f"Error adding text annotation: {str(e)}")
    def load_text_annotation(self):
        self.annotation_tool.load_annotations()
    def save_text_annotation(self):
        self.annotation_tool.save_annotations()
    def delete_text_annotation(self):
        self.annotation_tool.delete_annotation()
    def clear_all(self):
        """
        Clear all measurement tools and annotations from all viewers.
        """
        # List of all viewers to clear
        viewers = [self.ui.axial_viewer, self.ui.sagittal_viewer, self.ui.coronal_viewer]

        # Clear all measurements
        for viewer in viewers:
            self.measurement_tools.clear_measurements(viewer)

        # Clear all annotations
        for viewer in viewers:
            self.annotation_tool.clear_annotations(viewer)

        # Log action or show confirmation
        print("All measurements and annotations cleared.")

    def import_image(self, image_type, file_path=None):
        try:
            if image_type == None:
                file_path = file_path or self.get_path(
                    "All Files (*);;NIfTI Files (*.nii *.nii.gz);;DICOM Files (*.dcm)"
                )
                if not file_path:
                    return

                self.loaded_image_data, self.spacing_info = (
                    self.image_loader.load_image(file_path)
                )

                print(
                    self.loaded_image_data.shape,
                    self.spacing_info,
                )

                # Initialize image processor with loaded data
                self.image_processor.set_image_data(self.loaded_image_data)

                # Add to file history
                self.file_history_manager.add_to_history(file_path, image_type)

                # Display views
                self.display_views()

            elif image_type == "nii":
                file_path = file_path or self.get_path("NIfTI Files (*.nii *.nii.gz)")
                if not file_path:
                    return

                self.loaded_image_data, self.spacing_info = (
                    self.image_loader.load_nifti(file_path)
                )

                # Initialize image processor with loaded data
                self.image_processor.set_image_data(self.loaded_image_data)

                # Add to file history
                self.file_history_manager.add_to_history(file_path, image_type)

                # Display views
                self.display_views()

            elif image_type == "series":
                directory = file_path or QFileDialog.getExistingDirectory(
                    self, "Select DICOM Directory"
                )
                if not directory:
                    return

                self.loaded_image_data, self.spacing_info = (
                    self.image_loader.load_dicom_series(directory)
                )

                # Initialize image processor with loaded data
                self.image_processor.set_image_data(self.loaded_image_data)

                # Add to file history
                self.file_history_manager.add_to_history(directory, image_type)

                # Display views
                self.display_views()

        except Exception as e:
            self.show_error_message(str(e))

    def get_path(self, file_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", file_type
        )
        return file_path

    def render_slice(self, image_view: ImageView, slice_data):
        rotated_slice = np.rot90(slice_data, k=2)
        width, height = rotated_slice.shape

        image_view.setImage(
            rotated_slice.T,
            autoRange=True,
            autoLevels=True,
            autoHistogramRange=True,
            pos=[-width / 2, -height / 2],  # This centers the image
        )

    def display_views(self):
        if self.loaded_image_data is None:
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

            viewer.getView().setLimits(
                xMin=-width / 2,
                xMax=width / 2,
                yMin=-height / 2,
                yMax=height / 2,
            )

    def build_surface(self):
        self.volume_renderer = VolumeRenderer()
        render_window, render_ineractor, _ = (
            self.volume_renderer.create_volume_renderer(
                self.loaded_image_data,
                self.spacing_info,
            )
        )
        render_window.Render()
        render_ineractor.Start()

    def comparison_mode(self):
        data_1_path = self.get_path("NIfTI Files (*.nii *.nii.gz)")
        data_2_path = self.get_path("NIfTI Files (*.nii *.nii.gz)")

        if not data_1_path or not data_2_path:
            return

        data_1, spacing_1 = self.image_loader.load_nifti(data_1_path)
        data_2, spacing_2 = self.image_loader.load_nifti(data_2_path)

        self.comparison_renderer = ComparisonRenderer()
        render_window, render_interactor = (
            self.comparison_renderer.create_comparison_mode_renderer(
                data_1, data_2, spacing_1, spacing_2
            )
        )

        render_window.Render()
        render_interactor.Start()

    def setup_crosshairs(self):
        views = {
            "axial": self.ui.axial_viewer.getView(),
            "sagittal": self.ui.sagittal_viewer.getView(),
            "coronal": self.ui.coronal_viewer.getView(),
        }

        for plane, view in views.items():
            h_line = InfiniteLine(angle=0, movable=False, pen="b")
            v_line = InfiniteLine(angle=90, movable=False, pen="b")
            view.addItem(h_line)
            view.addItem(v_line)
            self.crosshairs[plane] = {
                "h_line": h_line,
                "v_line": v_line,
            }

        # Connect the crosshairs to the update_crosshairs function
        for plane, view in views.items():
            h_line = self.crosshairs[plane]["h_line"]
            v_line = self.crosshairs[plane]["v_line"]
            self.update_crosshairs(view, h_line, v_line)

    def update_crosshairs(
        self,
        view: ViewBox,
        h_line: InfiniteLine,
        v_line: InfiniteLine,
    ):
        # Get the range of the view
        x_range, y_range = view.viewRange()
        # Calculate the center of the range
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        # Set the position of the crosshairs to the center
        h_line.setPos(y_center)
        v_line.setPos(x_center)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    def exit_app(self):
        self.close()

    def closeEvent(self, event):
        for viewer in [
            self.ui.axial_viewer,
            self.ui.sagittal_viewer,
            self.ui.coronal_viewer,
        ]:
            viewer.close()
        # Explicitly accept the close event (optional)
        event.accept()

    def open_docs(self):
        webbrowser.open(
            "https://github.com/hagersamir/DICOM-Viewer-Features/blob/main/README.md"
        )

    def windowing(self):
        self.image_enhancer = ImageEnhancer()
        window_level, window_width = self.get_windowing_parameters()

        # Check if valid values were returned
        if window_level is not None and window_width is not None:
            self.loaded_image_data = self.image_enhancer.apply_window(
                self.loaded_image_data, window_level, window_width
            )
            self.display_views()

    def get_windowing_parameters(self):
        windowing_dialog = WindowingDialogUI()
        if windowing_dialog.exec_() == QDialog.accepted:
            window_level = windowing_dialog.windowLevelDoubleSpinBox.value()
            window_width = windowing_dialog.windowWidthDoubleSpinBox.value()
            return window_level, window_width
        return None, None  # Return None if dialog is rejected

    def smoothing_and_sharpening(self, mode):
        self.image_enhancer = ImageEnhancer()
        if mode == "Smoothing":
            sigma, strength = self.get_smoothing_parameters()

            if sigma is not None and strength is not None:
                self.loaded_image_data = self.image_enhancer.smooth_image(
                    self.loaded_image_data, sigma, strength
                )
                self.display_views()

        elif mode == "Sharpening":
            strength = self.get_sharpening_parameters()
            if strength is not None:
                self.loaded_image_data = self.image_enhancer.sharpen_image(
                    self.loaded_image_data, strength
                )
                self.display_views()

    def get_smoothing_parameters(self):
        smoothing_dialog = SmoothingAndSharpeningDialogUI(mode="Smoothing")
        if smoothing_dialog.exec_() == QDialog.accepted:
            sigma = smoothing_dialog.sigma_spinbox.value()
            smoothing_strength = smoothing_dialog.smoothing_strength_spinbox.value()
            return sigma, smoothing_strength
        return None, None

    def get_sharpening_parameters(self):
        sharpening_dialog = SmoothingAndSharpeningDialogUI(mode="Sharpening")
        if sharpening_dialog.exec_() == QDialog.accepted:
            sharpening_strength = sharpening_dialog.smoothing_strength_spinbox.value()
            return sharpening_strength
        return None

    def denoising(self):
        self.image_enhancer = ImageEnhancer()
        self.show_denoising_parameters_dialog()

    def show_denoising_parameters_dialog(self):
        denoising_dialog = DenoisingDialogUI()

        if denoising_dialog.exec_() == QDialog.Accepted:
            pass

    def show_denoising_parameters(self):
        pass

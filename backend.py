import webbrowser

import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QInputDialog
import pyqtgraph as pg
from pyqtgraph import ROI, ImageView, InfiniteLine, ViewBox

from core.comparison_renderer import ComparisonRenderer
from core.image_loader import ImageLoader
from core.image_processor import ImageProcessor
from core.volume_renderer import VolumeRenderer

# Import the new measurement tools
from core.measurements_annotations import MeasurementTools, AnnotationTool
from ui.main_window import MainWindowUI
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
            if image_type == "nii":
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
        """
        Renders a 2D slice in the given PyQtGraph ImageView.
        """
        # Rotate the image 90 degrees counterclockwise (to the left)
        rotated_slice = np.rot90(slice_data, k=-1)

        image_view.setImage(
            rotated_slice,
            autoRange=True,
            autoLevels=True,
            autoHistogramRange=False,
        )

    def display_views(self):
        if self.loaded_image_data is None:
            return

        views = {
            "axial": self.ui.axial_viewer,
            "sagittal": self.ui.sagittal_viewer,
            "coronal": self.ui.coronal_viewer,
        }

        for plane, widget in views.items():
            slice_data = self.image_processor.get_slice(plane)
            self.render_slice(widget, slice_data)

            # Get width and height of the slice
            width, height = slice_data.shape

            # Calculate the center of the image
            x_center = width / 2
            y_center = height / 2

            # Set the X and Y limits for the view
            widget.getView().setXRange(0, width, padding=0)
            widget.getView().setYRange(0, height, padding=0)
            # widget.getView().setLimits(
            #     xMin=0,
            #     xMax=width,
            #     yMin=0,
            #     yMax=height,
            # )

            # Center the view on the image
            widget.getView().setRange(
                xRange=(x_center - width / 2, x_center + width / 2),
                yRange=(y_center - height / 2, y_center + height / 2),
                padding=0,
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

import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox
from pyqtgraph import ImageView

from core.image_loader import ImageLoader
from core.image_processor import ImageProcessor
from ui.main_window import MainWindowUI
from utils.file_history_manager import FileHistoryManager


class DicomViewerBackend(QMainWindow, MainWindowUI):
    def __init__(self):
        super().__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        # Initialize components
        self.loaded_image_data = None
        self.image_loader = ImageLoader()
        self.image_processor = ImageProcessor()

        # File history management
        self.file_history_manager = FileHistoryManager(
            self.ui.menuFile, self.import_image
        )

        # Connect UI actions
        self.init_ui_connections()

    def init_ui_connections(self):
        # Connect menu actions
        self.ui.actionImport_NIFTI.triggered.connect(lambda: self.import_image("nii"))
        self.ui.actionImport_DICOM_Series.triggered.connect(
            lambda: self.import_image("series")
        )
        self.ui.actionImport_Sample_Image.triggered.connect(
            lambda: self.import_image("sample")
        )
        self.ui.actionQuit_App.triggered.connect(self.exit_app)

        # Setup crosshairs
        self.setup_mouse_handlers()

    def import_image(self, image_type, file_path=None):
        try:
            if image_type == "nii":
                file_path = file_path or self.get_path("NIfTI Files (*.nii *.nii.gz)")
                if not file_path:
                    return

                self.loaded_image_data = self.image_loader.load_nifti(file_path)

                # Initialize image processor with loaded data
                self.image_processor.set_image_data(self.loaded_image_data)

                # Add to file history
                self.file_history_manager.add_to_history(file_path, image_type)

                # Display views
                self.display_views()

        except Exception as e:
            self.show_error_message(str(e))

    def setup_mouse_handlers(self):
        views = {
            "axial": self.ui.axial_viewer.getView(),
            "sagittal": self.ui.sagittal_viewer.getView(),
            "coronal": self.ui.coronal_viewer.getView(),
        }

        for plane, view in views.items():
            view.scene().sigMouseMoved.connect(
                lambda pos, v=view, p=plane: self.on_mouse_moved(pos, v, p)
            )

    def on_mouse_moved(self, pos, view, plane):
        if view.sceneBoundingRect().contains(
            pos
        ):  # Check if the mouse is within the scene
            mouse_point = view.mapSceneToView(
                pos
            )  # Map the scene position to the view's coordinates
            x, y = int(mouse_point.x()), int(mouse_point.y())  # Get integer coordinates

            # Update crosshair positions
            self.ui.crosshairs[plane]["h_line"].setPos(y)
            self.ui.crosshairs[plane]["v_line"].setPos(x)

            # Update slices based on current plane
            self.update_slices_from_crosshair(plane, x, y)

    def update_slices_from_crosshair(self, current_plane, x, y):
        slice_indices = {
            "axial": {"sagittal": y, "coronal": x},
            "sagittal": {"axial": y, "coronal": x},
            "coronal": {"axial": y, "sagittal": x},
        }

        for plane, idx in slice_indices[current_plane].items():
            self.image_processor.update_slice(plane, idx)
            slice_data = self.image_processor.get_slice(plane)
            self.render_slice(getattr(self.ui, f"{plane}_viewer"), slice_data)

    def render_slice(self, image_view: ImageView, slice_data):
        """
        Renders a 2D slice in the given PyQtGraph ImageView.
        """
        # Rotate the image 90 degrees counterclockwise (to the left)
        rotated_slice = np.rot90(slice_data)

        image_view.setImage(rotated_slice.T, autoLevels=False, autoHistogramRange=False)

    def get_path(self, file_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", file_type
        )
        return file_path

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

            # Set the X and Y ranges based on the image dimensions
            x_range = (0, slice_data.shape[1])
            y_range = (0, slice_data.shape[0])
            widget.getView().setXRange(*x_range, padding=0)
            widget.getView().setYRange(*y_range, padding=0)

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

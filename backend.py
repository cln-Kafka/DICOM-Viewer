import sys

from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from core.image_loader import ImageLoader
from core.image_processor import ImageProcessor
from core.vtk_renderer import VTKRenderer
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
        self.vtk_renderer = VTKRenderer()

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
        self.ui.actionQuit_App.triggered.connect(self.exit_app)

    def import_image(self, image_type, file_path=None):
        try:
            if image_type == "nii":
                file_path = file_path or self.get_path("NIfTI Files (*.nii *.nii.gz)")
                if not file_path:
                    return

                self.loaded_image_data = self.image_loader.load_nifti(file_path)

                # Add to file history
                self.file_history_manager.add_to_history(file_path, image_type)

                # Display views
                self.display_views()

        except Exception as e:
            self.show_error_message(str(e))

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
            slice_data = self.image_processor.get_slice(self.loaded_image_data, plane)
            self.vtk_renderer.render_slice(widget, slice_data)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    def exit_app(self):
        self.close()

    def closeEvent(self, event):
        """
        Override the close event to ensure proper cleanup of VTK resources
        """
        for viewer in [
            self.ui.axial_viewer,
            self.ui.sagittal_viewer,
            self.ui.coronal_viewer,
        ]:
            viewer.GetRenderWindow().Finalize()
        event.accept()

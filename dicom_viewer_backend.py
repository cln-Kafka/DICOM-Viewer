import os
import sys

import nibabel as nib
import numpy as np
import qdarktheme
import vtk
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QMainWindow, QMessageBox
from vtkmodules.util.numpy_support import numpy_to_vtk

from dicom_viewer_ui import DicomViewerUI


class DicomViewerBackend(QMainWindow, DicomViewerUI):
    def __init__(self):
        super().__init__()
        self.ui = DicomViewerUI()
        self.ui.setupUi(self)

        # Variables #
        self.loaded_image_data = None
        # Dictionary to store paths and their types (e.g., "nii" or "series")
        self.loaded_paths_history = {}

        # UI variable setup and connections
        self.init_ui_connections()

    def init_ui_connections(self):
        ## MenuBar Actions ##
        self.ui.actionImport_NIFTI.triggered.connect(lambda: self.import_image("nii"))
        self.ui.actionImport_Sample_Image.triggered.connect(
            lambda: self.import_image("sample")
        )
        self.ui.actionImport_DICOM_Series.triggered.connect(
            lambda: self.import_image("series")
        )
        self.ui.actionQuit_App.triggered.connect(self.exit_app)

    def import_image(self, image_type, file_path=None):
        if image_type == "nii":
            if file_path is None:
                file_path = self.get_path("NIfTI Files (*.nii *.nii.gz)")
            if not file_path:
                self.show_error_message("Couldn't load file.")
                return
            try:
                nii_image = nib.load(file_path)
                # Extract the 3D array from the NIfTI file
                self.loaded_image_data = nii_image.get_fdata()
                print(f"Loaded NIfTI file: {file_path}")
                print(f"Image shape: {self.loaded_image_data.shape}")

                # Add path to history if not already present
                if file_path not in self.loaded_paths_history:
                    self.loaded_paths_history[file_path] = "nii"
                    self.update_file_menu_history()

                # Display the views
                self.display_views()

            except Exception as e:
                self.show_error_message(f"Failed to load NIfTI file: {e}")

        elif image_type == "sample":
            pass
        elif image_type == "series":
            if file_path is None:
                file_path = self.get_path("DICOM Series")

            if not file_path:
                self.show_error_message("Couldn't load file.")
                return

            # Add it to history
            if file_path not in self.loaded_paths_history:
                self.loaded_paths_history[file_path] = "series"
                self.update_file_menu_history()

            print(f"Loaded DICOM series: {file_path}")

    def get_path(self, file_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open NIfTI File", "", file_type
        )
        return file_path

    def display_views(self):
        if self.loaded_image_data is None:
            return

        # Axial view (z-axis)
        axial_slice = self.loaded_image_data[self.loaded_image_data.shape[2] // 2, :, :]
        self.render_slice_in_vtk(self.ui.axial_viewer, axial_slice)

        # Sagittal view (x-axis)
        sagittal_slice = self.loaded_image_data[
            :, self.loaded_image_data.shape[1] // 2, :
        ]
        self.render_slice_in_vtk(self.ui.sagittal_viewer, sagittal_slice)

        # Coronal view (y-axis)
        coronal_slice = self.loaded_image_data[
            :, :, self.loaded_image_data.shape[2] // 2
        ]
        self.render_slice_in_vtk(self.ui.coronal_viewer, coronal_slice)

    def render_slice_in_vtk(self, vtk_widget, slice_data):
        """
        Renders a 2D slice in the specified VTK widget.
        """
        # Convert NumPy array to vtkImageData
        vtk_data = vtk.vtkImageData()
        vtk_data.SetDimensions(slice_data.shape[1], slice_data.shape[0], 1)
        vtk_data.SetOrigin(0, 0, 0)
        vtk_data.SetSpacing(1, 1, 1)

        # Convert slice data to a flat array and assign it to vtkImageData
        flat_array = slice_data.flatten()
        vtk_array = numpy_to_vtk(flat_array, deep=True, array_type=vtk.VTK_FLOAT)
        vtk_data.GetPointData().SetScalars(vtk_array)

        # Create a mapper and actor
        mapper = vtk.vtkImageActor()
        mapper.GetMapper().SetInputData(vtk_data)  # Corrected line

        # Add the actor to the renderer and set up the view
        renderer = vtk.vtkRenderer()
        renderer.AddActor(mapper)

        # Set up the render window
        vtk_widget.GetRenderWindow().AddRenderer(renderer)
        vtk_widget.GetRenderWindow().Render()

    def closeEvent(self, event):
        """
        Override the close event to ensure proper cleanup of VTK resources.
        """
        # Clear renderers and interactor
        self.ui.axial_viewer.GetRenderWindow().Finalize()
        self.ui.sagittal_viewer.GetRenderWindow().Finalize()
        self.ui.coronal_viewer.GetRenderWindow().Finalize()

        # Call the parent close event
        event.accept()

    def update_file_menu_history(self):
        """
        Updates the file menu with actions for each loaded image in history.
        """
        # Clear previous history actions before adding new ones
        self.ui.menuFile.clear()

        # Add standard actions
        self.ui.menuFile.addAction(self.ui.actionImport_NIFTI)
        self.ui.menuFile.addAction(self.ui.actionImport_Sample_Image)
        self.ui.menuFile.addAction(self.ui.actionImport_DICOM_Series)
        self.ui.menuFile.addSeparator()

        # Add history actions showing only the file name
        for file_path, file_type in self.loaded_paths_history.items():
            file_name = os.path.basename(file_path)  # Get the file name from the path
            history_action = QAction(file_name, self)
            history_action.setData(
                (file_path, file_type)
            )  # Store path and type as user data
            history_action.triggered.connect(
                lambda checked, path=file_path, type=file_type: self.import_image(
                    type, path
                )
            )
            self.ui.menuFile.addAction(history_action)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    def exit_app(self):
        self.close()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    MainWindow = DicomViewerBackend()
    MainWindow.show()
    qdarktheme.setup_theme("dark")
    sys.exit(app.exec_())

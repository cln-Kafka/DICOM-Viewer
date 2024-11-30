import os
import numpy as np
import vtk
import SimpleITK as sitk
from vtk.util import numpy_support
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
import qdarktheme

class ComparisonRenderer(QMainWindow):
    def __init__(self, volume_data_1, volume_data_2, spacing_1, spacing_2):
        """
        Initialize the Comparison Rendering window
        
        :param volume_data_1: First 3D numpy array of image data
        :param volume_data_2: Second 3D numpy array of image data
        :param spacing_1: Voxel spacing for first image
        :param spacing_2: Voxel spacing for second image
        """
        super().__init__()
        self.setWindowTitle("Image Comparison")
        self.resize(1600, 800)
        
        # Apply dark theme
        self.setStyleSheet(qdarktheme.load_stylesheet())

        # Create a central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Create VTK rendering components
        render_window, render_interactor = self._create_comparison_renderer(
            volume_data_1, volume_data_2, spacing_1, spacing_2
        )

        # Embed VTK render window in PyQt5 window
        from PyQt5.QtWidgets import QVBoxLayout
        from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

        vtk_widget = QVTKRenderWindowInteractor(central_widget)
        vtk_widget.SetRenderWindow(render_window)
        layout.addWidget(vtk_widget)

        # Initialize the interactor
        render_interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        render_interactor.Initialize()
        render_interactor.Start()

        # Render the window
        render_window.Render()

    def _create_comparison_renderer(self, volume_data_1, volume_data_2, spacing_1, spacing_2):
        """
        Create a side-by-side volume renderer
        
        :param volume_data_1: First 3D numpy array of image data
        :param volume_data_2: Second 3D numpy array of image data
        :param spacing_1: Voxel spacing for first image
        :param spacing_2: Voxel spacing for second image
        :return: render_window, render_interactor
        """
        def create_volume_renderer(volume_data, spacing):
            """
            Helper function to create a volume renderer for a single volume
            
            :param volume_data: 3D numpy array of image data
            :param spacing: Voxel spacing information
            :return: renderer
            """
            # Convert the numpy array to a VTK image
            vtk_image = vtk.vtkImageData()
            depth_array = numpy_support.numpy_to_vtk(num_array=volume_data.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
            vtk_image.SetDimensions(volume_data.shape[::-1])
            vtk_image.GetPointData().SetScalars(depth_array)
            vtk_image.SetSpacing(spacing)

            # Create the volume mapper
            volume_mapper = vtk.vtkSmartVolumeMapper()
            volume_mapper.SetInputData(vtk_image)

            # Set the volume property
            color_transfer_function = vtk.vtkColorTransferFunction()
            opacity_transfer_function = vtk.vtkPiecewiseFunction()

            # Dynamic transfer function setup
            min_intensity = np.min(volume_data)
            max_intensity = np.max(volume_data)

            # Add color points
            color_transfer_function.AddRGBPoint(min_intensity, 0.0, 0.0, 0.0)  # Black for low intensity
            color_transfer_function.AddRGBPoint(max_intensity, 1.0, 1.0, 1.0)  # White for high intensity

            # Define opacity function
            opacity_transfer_function.AddPoint(min_intensity, 0.0)  # Fully transparent at min intensity
            opacity_transfer_function.AddPoint(max_intensity, 1.0)  # Fully opaque at max intensity

            volume_property = vtk.vtkVolumeProperty()
            volume_property.SetColor(color_transfer_function)
            volume_property.SetScalarOpacity(opacity_transfer_function)
            volume_property.ShadeOn()  # Enable shading for realism

            # Create the volume actor
            volume = vtk.vtkVolume()
            volume.SetMapper(volume_mapper)
            volume.SetProperty(volume_property)

            # Create the renderer and add the volume actor
            renderer = vtk.vtkRenderer()
            renderer.AddVolume(volume)
            renderer.SetBackground(0.1, 0.1, 0.1)  # Dark gray background
            renderer.ResetCamera()

            return renderer

        # Create renderers for both volumes
        renderer_1 = create_volume_renderer(volume_data_1, spacing_1)
        renderer_2 = create_volume_renderer(volume_data_2, spacing_2)

        # Create render window
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer_1)
        render_window.AddRenderer(renderer_2)

        # Set viewports to split the window
        renderer_1.SetViewport(0.0, 0.0, 0.5, 1.0)  # left side
        renderer_2.SetViewport(0.5, 0.0, 1.0, 1.0)  # right side

        # Set render window size
        render_window.SetSize(1600, 800)

        # Create render window interactor
        render_interactor = vtk.vtkRenderWindowInteractor()
        render_interactor.SetRenderWindow(render_window)

        return render_window, render_interactor

    @classmethod
    def load_dicom_series(cls, directory):
        """
        Load a DICOM series from a directory.
        
        :param directory: Path to DICOM series directory
        :return: volume_data, spacing
        """
        reader = sitk.ImageSeriesReader()
        dicom_files = reader.GetGDCMSeriesFileNames(directory)
        reader.SetFileNames(dicom_files)
        image = reader.Execute()
        return sitk.GetArrayFromImage(image), image.GetSpacing()

    @classmethod
    def load_nifti_file(cls, file_path):
        """
        Load a NIfTI file.
        
        :param file_path: Path to NIfTI file
        :return: volume_data, spacing
        """
        image = sitk.ReadImage(file_path)
        return sitk.GetArrayFromImage(image), image.GetSpacing()

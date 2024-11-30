import numpy as np
import qdarktheme
import vtk
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.util import numpy_support


class VolumeRenderer(QMainWindow):
    def __init__(self, volume_data, spacing):
        """
        Initialize the Volume Renderer window

        :param volume_data: 3D numpy array of image data
        :param spacing: Voxel spacing information
        """
        super().__init__()
        self.setWindowTitle("Volume Rendering")
        self.resize(1024, 768)

        # Apply dark theme
        self.setStyleSheet(qdarktheme.load_stylesheet())

        # Create a central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Create VTK rendering components
        render_window, render_interactor, renderer = self._create_volume_renderer(
            volume_data, spacing
        )

        vtk_widget = QVTKRenderWindowInteractor(central_widget)
        vtk_widget.SetRenderWindow(render_window)
        layout.addWidget(vtk_widget)

        # Initialize the interactor
        render_interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        render_interactor.Initialize()
        render_interactor.Start()

        # Render the window
        render_window.Render()

    def _create_volume_renderer(self, volume_data, spacing):
        """
        Create a volume renderer using VTK for the given 3D volume data.

        :param volume_data: 3D numpy array of image data
        :param spacing: Voxel spacing information
        :return: render_window, render_interactor, renderer
        """
        # Convert the numpy array to a VTK image
        vtk_image = vtk.vtkImageData()
        depth_array = numpy_support.numpy_to_vtk(
            num_array=volume_data.ravel(), deep=True, array_type=vtk.VTK_FLOAT
        )
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
        color_transfer_function.AddRGBPoint(
            min_intensity, 0.0, 0.0, 0.0
        )  # Black for low intensity
        color_transfer_function.AddRGBPoint(
            max_intensity, 1.0, 1.0, 1.0
        )  # White for high intensity

        # Define opacity function
        opacity_transfer_function.AddPoint(
            min_intensity, 0.0
        )  # Fully transparent at min intensity
        opacity_transfer_function.AddPoint(
            max_intensity, 1.0
        )  # Fully opaque at max intensity

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

        # Set up the render window and interactor
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(800, 600)

        render_interactor = vtk.vtkRenderWindowInteractor()
        render_interactor.SetRenderWindow(render_window)

        return render_window, render_interactor, renderer

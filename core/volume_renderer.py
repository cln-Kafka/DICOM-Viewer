import numpy as np
import qdarktheme
import vtk
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.util import numpy_support


class VolumeRenderer:
    def __init__(self):
        # Global variables to keep track of intensity values
        self.min_intensity = None
        self.max_intensity = None

    def update_transfer_functions(
        self, color_transfer_function, opacity_transfer_function
    ):
        # delete previous points
        color_transfer_function.RemoveAllPoints()
        opacity_transfer_function.RemoveAllPoints()
        # add new points for the updated intensity range
        color_transfer_function.AddRGBPoint(
            self.min_intensity, 0.0, 0.0, 0.0
        )  # Black for low intensity
        color_transfer_function.AddRGBPoint(
            self.max_intensity, 1.0, 1.0, 1.0
        )  # White for high intensity
        # Define opacity function
        opacity_transfer_function.AddPoint(
            self.min_intensity, 0.0
        )  # Fully transparent at min intensity
        opacity_transfer_function.AddPoint(
            self.max_intensity, 1.0
        )  # Fully opaque at max intensity

    def adjust_contrast(
        self,
        interactor,
        color_transfer_function,
        opacity_transfer_function,
        render_window,
    ):
        key = interactor.GetKeySym()  # trace the pressed key
        contrast_step = 0.05  # 5% step size for gradual change
        if key == "Right":
            # inc contrast (narrow the intensity range)
            self.min_intensity *= 1 - contrast_step  # dec the min intensity by 5%
            self.max_intensity *= 1 + contrast_step  # inc the max intensity by 5%
            self.update_transfer_functions(
                color_transfer_function, opacity_transfer_function
            )
            render_window.Render()  # Force update of the render window

        elif key == "Left":
            # dec contrast (widen the intensity range)
            self.min_intensity *= 1 + contrast_step  # inc the min intensity by 5%
            self.max_intensity *= 1 - contrast_step  # dec the max intensity by 5%
            self.update_transfer_functions(
                color_transfer_function, opacity_transfer_function
            )
            render_window.Render()  # Force update of the render window

    def create_volume_renderer(self, volume_data, spacing):
        """
        Create a volume renderer using VTK for the given 3D volume data.
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
        # Bind the contrast adjustment functionality
        self.min_intensity = np.min(volume_data)
        self.max_intensity = np.max(volume_data)
        render_interactor.AddObserver(
            "KeyPressEvent",
            lambda obj, event: self.adjust_contrast(
                obj,
                color_transfer_function,
                opacity_transfer_function,
                render_window,
            ),
        )

        return render_window, render_interactor, renderer

import vtk
import SimpleITK as sitk
from vtk.util import numpy_support
import numpy as np

def load_dicom_series(directory):
    reader = sitk.ImageSeriesReader()
    dicom_files = reader.GetGDCMSeriesFileNames(directory)
    reader.SetFileNames(dicom_files)
    image = reader.Execute()
    return sitk.GetArrayFromImage(image), image.GetSpacing()


def create_volume_renderer(volume_data, spacing):
    # Convert the numpy array to a VTK image
    vtk_image = vtk.vtkImageData()
    depth_array = numpy_support.numpy_to_vtk(num_array=volume_data.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
    vtk_image.SetDimensions(volume_data.shape[::-1])
    vtk_image.GetPointData().SetScalars(depth_array)
    vtk_image.SetSpacing(spacing)

    # Create the volume mapper
    volume_mapper = vtk.vtkSmartVolumeMapper()
    volume_mapper.SetInputData(vtk_image)

    # Create dynamic transfer functions
    color_transfer_function = vtk.vtkColorTransferFunction()
    opacity_transfer_function = vtk.vtkPiecewiseFunction()

    # Set the volume property
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
    min_intensity = np.min(volume_data)
    max_intensity = np.max(volume_data)
    # Bind the contrast adjustment functionality
    render_interactor.AddObserver("KeyPressEvent", lambda obj, event: adjust_contrast(obj, volume_data, volume_property, color_transfer_function, opacity_transfer_function,min_intensity,max_intensity,render_window))

    return render_window, render_interactor

def adjust_contrast(interactor, volume_data, volume_property, color_transfer_function, opacity_transfer_function,min_intensity,max_intensity,render_window):   
    # For simplicity, adjust contrast using a key press for now
    key = interactor.GetKeySym() #trace the pressed key 
    if key == 'Right':
        # Increase contrast (narrow the intensity range)
        range_factor = 0.2
        min_intensity *= range_factor
        max_intensity /= range_factor
        color_transfer_function.RemoveAllPoints()
        opacity_transfer_function.RemoveAllPoints()
        color_transfer_function.AddRGBPoint(min_intensity, 0.0, 0.0, 0.0)
        color_transfer_function.AddRGBPoint(max_intensity, 1.0, 1.0, 1.0)
        opacity_transfer_function.AddPoint(min_intensity, 0.0)
        opacity_transfer_function.AddPoint(max_intensity, 1.0)
        volume_property.SetColor(color_transfer_function)
        volume_property.SetScalarOpacity(opacity_transfer_function)
        render_window.Render()  # Force update of the render window
    elif key == 'left':
        # Decrease contrast (widen the intensity range)
        range_factor = 2
        min_intensity /= range_factor
        max_intensity *= range_factor
        color_transfer_function.RemoveAllPoints()
        opacity_transfer_function.RemoveAllPoints()
        color_transfer_function.AddRGBPoint(min_intensity, 0.0, 0.0, 0.0)
        color_transfer_function.AddRGBPoint(max_intensity, 1.0, 1.0, 1.0)
        opacity_transfer_function.AddPoint(min_intensity, 0.0)
        opacity_transfer_function.AddPoint(max_intensity, 0.5)  # Semi-transparent
        volume_property.SetColor(color_transfer_function)
        volume_property.SetScalarOpacity(opacity_transfer_function)
        render_window.Render()  # Force update of the render window

def main():
    dicom_directory = r"./series-000001"
    volume_data, spacing = load_dicom_series(dicom_directory)
    render_window, render_interactor = create_volume_renderer(volume_data, spacing)
    render_window.Render()
    render_interactor.Start()

if __name__ == "__main__":
    main()

import numpy as np
import vtk
from vtkmodules.util.numpy_support import numpy_to_vtk


class VTKRenderer:
    @staticmethod
    def render_slice(vtk_widget, slice_data):
        """
        Renders a 2D slice in the specified VTK widget
        """
        slice_data = np.rot90(slice_data, k=3)

        vtk_data = vtk.vtkImageData()
        vtk_data.SetDimensions(slice_data.shape[1], slice_data.shape[0], 1)
        vtk_data.SetOrigin(0, 0, 0)
        vtk_data.SetSpacing(1, 1, 1)

        flat_array = slice_data.flatten()
        vtk_array = numpy_to_vtk(flat_array, deep=True, array_type=vtk.VTK_FLOAT)
        vtk_data.GetPointData().SetScalars(vtk_array)

        mapper = vtk.vtkImageActor()
        mapper.GetMapper().SetInputData(vtk_data)

        renderer = vtk.vtkRenderer()
        renderer.AddActor(mapper)

        vtk_widget.GetRenderWindow().AddRenderer(renderer)
        vtk_widget.GetRenderWindow().Render()

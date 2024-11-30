import vtk

from core.volume_renderer import VolumeRenderer


class ComparisonRenderer:
    def __init__(self):
        self.volume_renderer = VolumeRenderer()

    def create_comparison_mode_renderer(
        self, volume_data_1, volume_data_2, spacing_1, spacing_2
    ):
        _, _, renderer_1 = self.volume_renderer.create_volume_renderer(
            volume_data_1,
            spacing_1,
        )
        _, _, renderer_2 = self.volume_renderer.create_volume_renderer(
            volume_data_2,
            spacing_2,
        )
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer_1)
        render_window.AddRenderer(renderer_2)
        renderer_1.SetViewport(0.0, 0.0, 0.5, 1.0)  # left side
        renderer_2.SetViewport(0.5, 0.0, 1.0, 1.0)  # right side
        render_window.SetSize(1600, 800)
        render_interactor = vtk.vtkRenderWindowInteractor()
        render_interactor.SetRenderWindow(render_window)

        return render_window, render_interactor

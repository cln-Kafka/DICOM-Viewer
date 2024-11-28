import vtk


# Custom interactor style class to disable rotation
class NoRotationInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        super().__init__()

    def OnMouseMove(self):
        # Override the mouse move event to prevent rotation
        pass

    def OnLeftButtonDown(self):
        # Override the left button down event to prevent rotation
        pass

    def OnLeftButtonUp(self):
        # Override the left button up event to prevent rotation
        pass

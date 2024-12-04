import math

from pyqtgraph import LineROI, TextItem


class RulerROI(LineROI):
    def __init__(self, viewer, pos1=(100, 100), pos2=[200, 200], parent=None):
        super().__init__(pos1, pos2, width=1, parent=parent)
        self.viewer = viewer

        # Distance text
        self.distance_text = TextItem("", anchor=(0, 0))
        viewer.getView().addItem(self.distance_text)

        # Connect signal
        self.sigRegionChanged.connect(self.update_measurement)

    def update_measurement(self):
        """
        Calculate and display the distance between ROI handles.
        """
        handles = self.getHandles()
        if len(handles) < 2:
            return

        pos1 = handles[0].pos()
        pos2 = handles[1].pos()
        length = math.sqrt((pos2.x() - pos1.x()) ** 2 + (pos2.y() - pos1.y()) ** 2)

        # Position the text near the center of the ROI
        center_x = (pos1.x() + pos2.x()) / 2
        center_y = (pos1.y() + pos2.y()) / 2

        self.distance_text.setText(f"Length: {length:.2f}")
        self.distance_text.setPos(center_x, center_y)

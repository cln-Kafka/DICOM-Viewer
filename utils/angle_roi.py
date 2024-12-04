import math

from pyqtgraph import Point, PolyLineROI, TextItem


class AngleROI(PolyLineROI):
    def __init__(self, viewer, parent=None):
        points = [(100, 200), (200, 150), (190, 100)]
        super().__init__(points, closed=False, movable=True, parent=parent)
        self.viewer = viewer

        # Angle text
        self.angle_text = TextItem("", anchor=(0, 0))
        viewer.getView().addItem(self.angle_text)

        # Connect signal
        self.sigRegionChanged.connect(self.update_angle_measurement)

    def update_angle_measurement(self):
        """
        Calculate and display the angle between three points.
        """
        points = self.getLocalHandlePositions()

        if len(points) < 3:
            self.angle_text.setText("Insufficient points")
            return

        p1, p2, p3 = points[0][1], points[1][1], points[2][1]

        # Vectors of the segments
        v1 = Point(p2.x() - p1.x(), p2.y() - p1.y())
        v2 = Point(p3.x() - p2.x(), p3.y() - p2.y())

        # Calculate the angle using the dot product formula
        dot_product = v1.x() * v2.x() + v1.y() * v2.y()
        mag_v1 = math.sqrt(v1.x() ** 2 + v1.y() ** 2)
        mag_v2 = math.sqrt(v2.x() ** 2 + v2.y() ** 2)

        if mag_v1 == 0 or mag_v2 == 0:
            self.angle_text.setText("Invalid geometry")
            return

        angle_radians = math.acos(dot_product / (mag_v1 * mag_v2))
        angle_degrees = math.degrees(angle_radians)

        self.angle_text.setText(f"Angle: {angle_degrees:.2f}°")

        # Position the text near the vertex point (p2)
        self.angle_text.setPos(p2.x(), p2.y())

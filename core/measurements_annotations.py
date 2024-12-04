import math
import json
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QInputDialog, QMenu
from pyqtgraph import LineROI, PolyLineROI, TextItem, Point

class MeasurementTools:
    def __init__(self, backend):
        self.backend = backend
        self.active_measurements = {}  # Dictionary to track active measurements per viewer
        self.hidden_measurements = {}  # Dictionary to track hidden measurements per viewer

    def create_ruler(self, viewer):
        """Create a ruler measurement tool."""
        ruler_roi = RulerROI(viewer)
        viewer.getView().addItem(ruler_roi)

        if viewer not in self.active_measurements:
            self.active_measurements[viewer] = []
        self.active_measurements[viewer].append(ruler_roi)

        return ruler_roi

    def create_angle_measurement(self, viewer):
        """Create an angle measurement tool."""
        angle_roi = AngleROI(viewer)
        viewer.getView().addItem(angle_roi)

        if viewer not in self.active_measurements:
            self.active_measurements[viewer] = []
        self.active_measurements[viewer].append(angle_roi)

        return angle_roi

    def toggle_ruler(self, viewer, checked):
        """Toggle the visibility of ruler measurements for the active viewer."""
        if viewer not in self.hidden_measurements:
            self.hidden_measurements[viewer] = []
        if viewer not in self.active_measurements:
            self.active_measurements[viewer] = []

        if checked:
            # Restore hidden rulers for the active viewer
            to_restore = [
                m for m in self.hidden_measurements[viewer] if isinstance(m, RulerROI)
            ]
            for measurement in to_restore:
                viewer.getView().addItem(measurement)
                viewer.getView().addItem(measurement.distance_text)
                self.active_measurements[viewer].append(measurement)
            self.hidden_measurements[viewer] = [
                m for m in self.hidden_measurements[viewer] if not isinstance(m, RulerROI)
            ]
        else:
            # Hide active rulers for the active viewer
            to_hide = [
                m for m in self.active_measurements[viewer] if isinstance(m, RulerROI)
            ]
            for measurement in to_hide:
                viewer.getView().removeItem(measurement)
                viewer.getView().removeItem(measurement.distance_text)
                self.hidden_measurements[viewer].append(measurement)
            self.active_measurements[viewer] = [
                m for m in self.active_measurements[viewer] if not isinstance(m, RulerROI)
            ]

    def toggle_angle(self, viewer, checked):
        """Toggle the visibility of angle measurements for the active viewer."""
        if viewer not in self.hidden_measurements:
            self.hidden_measurements[viewer] = []
        if viewer not in self.active_measurements:
            self.active_measurements[viewer] = []

        if checked:
            # Restore hidden angles for the active viewer
            to_restore = [
                m for m in self.hidden_measurements[viewer] if isinstance(m, AngleROI)
            ]
            for measurement in to_restore:
                viewer.getView().addItem(measurement)
                viewer.getView().addItem(measurement.angle_text)
                self.active_measurements[viewer].append(measurement)
            self.hidden_measurements[viewer] = [
                m for m in self.hidden_measurements[viewer] if not isinstance(m, AngleROI)
            ]
        else:
            # Hide active angles for the active viewer
            to_hide = [
                m for m in self.active_measurements[viewer] if isinstance(m, AngleROI)
            ]
            for measurement in to_hide:
                viewer.getView().removeItem(measurement)
                viewer.getView().removeItem(measurement.angle_text)
                self.hidden_measurements[viewer].append(measurement)
            self.active_measurements[viewer] = [
                m for m in self.active_measurements[viewer] if not isinstance(m, AngleROI)
            ]

class RulerROI(LineROI):
    def __init__(self, viewer, pos1=(100, 100), pos2=[200,200], parent=None):
        super().__init__(pos1,pos2, width=1 , parent=parent)
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
        length = math.sqrt((pos2.x() - pos1.x())**2 + (pos2.y() - pos1.y())**2)
        
        # Position the text near the center of the ROI
        center_x = (pos1.x() + pos2.x()) / 2
        center_y = (pos1.y() + pos2.y()) / 2
        
        self.distance_text.setText(f"Length: {length:.2f}")
        self.distance_text.setPos(center_x, center_y)

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
        mag_v1 = math.sqrt(v1.x()**2 + v1.y()**2)
        mag_v2 = math.sqrt(v2.x()**2 + v2.y()**2)
        
        if mag_v1 == 0 or mag_v2 == 0:
            self.angle_text.setText("Invalid geometry")
            return
        
        angle_radians = math.acos(dot_product / (mag_v1 * mag_v2))
        angle_degrees = math.degrees(angle_radians)
        
        self.angle_text.setText(f"Angle: {angle_degrees:.2f}°")
        
        # Position the text near the vertex point (p2)
        self.angle_text.setPos(p2.x(), p2.y())

class AnnotationTool:
    def __init__(self, backend, annotations_file='annotations.json'):
        """
        Initialize the AnnotationTool.

        Args:
            backend: The application backend for accessing viewers and other components.
            annotations_file: Path to the annotations JSON file.
        """
        self.backend = backend
        self.annotations = []  # To store all annotations
        self.annotations_file = annotations_file
        self.text_annotations = {}  # {viewer_name: [TextAnnotation objects]}
        self.is_loading = False  # Flag to prevent recursion

    def load_annotations(self):
        """Load annotations from a JSON file."""
        if os.path.exists(self.annotations_file):
            try:
                with open(self.annotations_file, "r") as f:
                    loaded_annotations = json.load(f)

                # Clear existing annotations
                for viewer_name, text_items in self.text_annotations.items():
                    viewer = self.backend.viewers.get(viewer_name)
                    if viewer:
                        for text_item in text_items:
                            viewer.getView().removeItem(text_item)
                self.text_annotations = {viewer: [] for viewer in self.backend.viewers}
                self.annotations = []

                # Add loaded annotations
                for ann in loaded_annotations:
                    viewer_name = ann.get("viewer", "axial")  # Default to "axial"
                    if viewer_name in self.backend.viewers:
                        viewer = self.backend.viewers[viewer_name]
                        self.add_text_annotation(
                            viewer, ann["text"], tuple(ann["position"]), save=False
                        )
                    else:
                        print(f"Warning: Viewer '{viewer_name}' not found for annotation '{ann}'")

                print(f"Annotations loaded from {self.annotations_file}")

            except json.JSONDecodeError:
                print(f"Warning: The annotations file '{self.annotations_file}' is empty or corrupted.")
        else:
            print(f"No annotations file found at {self.annotations_file}")


    def save_annotations(self):
        """Save all annotations to the JSON file."""
        with open(self.annotations_file, 'w') as f:
            json.dump(self.annotations, f, indent=4)
        print(f"Annotations saved to {self.annotations_file}")

    def add_text_annotation(self, viewer, text=None, position=(50, 50), save=True):
        """
        Add a text annotation to a specific viewer.

        Args:
            viewer: PyQtGraph viewer.
            text: Annotation text.
            position: Annotation position (default is (50, 50)).
            save: Whether to save annotations to the JSON file (default is True).
        """
        # If loading, do not save
        if self.is_loading:
            save = False

        # If no text is provided, prompt the user
        if text is None:
            text, ok = QInputDialog.getText(
                None,
                "Add Annotation",
                "Enter annotation text:"
            )
            if not ok or not text:
                return None

        # Create text annotation item
        text_item = TextAnnotation(text, position)
        viewer.getView().addItem(text_item)

        # Determine the viewer's name
        viewer_name = next((name for name, v in self.backend.viewers.items() if v == viewer), None)

        if viewer_name:
            # Store annotation details
            annotation = {
                "viewer": viewer_name,
                "text": text,
                "position": list(position)
            }
            self.annotations.append(annotation)
            if viewer_name not in self.text_annotations:
                self.text_annotations[viewer_name] = []
            self.text_annotations[viewer_name].append(text_item)

            # # Save if required
            # if save:
            #     self.save_annotations()

            # print(f"Annotation '{text}' added at {position} in viewer '{viewer_name}'")
        else:
            print("Failed to identify viewer for annotation.")
        return text_item

    def clear_annotations(self, viewer=None):
        """
        Clear annotations from a specific viewer or all viewers if none is specified.

        Args:
            viewer: The PyQtGraph viewer to clear annotations from. If None, clear all viewers.
        """
        if viewer:
            # Clear annotations for the specified viewer
            viewer_name = next((name for name, v in self.backend.viewers.items() if v == viewer), None)
            if viewer_name and viewer_name in self.text_annotations:
                for text_item in self.text_annotations[viewer_name]:
                    viewer.getView().removeItem(text_item)
                self.text_annotations[viewer_name] = []
                self.annotations = [
                    ann for ann in self.annotations if ann["viewer"] != viewer_name
                ]
                print(f"Annotations cleared for viewer '{viewer_name}'")
        else:
            # Clear annotations for all viewers
            for viewer_name, text_items in self.text_annotations.items():
                viewer = self.backend.viewers.get(viewer_name)
                if viewer:
                    for text_item in text_items:
                        viewer.getView().removeItem(text_item)
            self.text_annotations = {viewer: [] for viewer in self.backend.viewers}
            self.annotations = []
            print("All annotations cleared!")




class TextAnnotation(QGraphicsTextItem):
    def __init__(self, text, position, color=Qt.red):
        super().__init__(text)
        
        # Styling
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
        self.setDefaultTextColor(color)
        
        # Make draggable and selectable
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        
        # Context menu
        self.setAcceptDrops(True)
        
        # Position
        self.setPos(*position)
    
    def contextMenuEvent(self, event):
        """
        Override context menu to provide delete option.
        """
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec_(event.screenPos())
        
        if action == delete_action:
            # Assumes a reference to the annotation tool is available
            if hasattr(self, 'annotation_tool'):
                self.annotation_tool.delete_annotation(self)
    def __init__(self, text, position, color=Qt.red):
        super().__init__(text)
        
        # Styling
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.setDefaultTextColor(color)
        
        # Make draggable
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        
        # Position
        self.setPos(*position)
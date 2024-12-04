import math
import json
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from pyqtgraph import LineROI, PolyLineROI, TextItem, Point

class MeasurementTools:
    def __init__(self, backend):
        self.backend = backend
        self.active_measurement = None
        self.measurement_items = []

    def create_ruler(self, viewer):
        """
        Create a ruler measurement tool for precise distance measurement.
        """
        ruler_roi = RulerROI(viewer)
        viewer.getView().addItem(ruler_roi)
        self.measurement_items.append(ruler_roi)
        return ruler_roi

    def create_angle_measurement(self, viewer):
        """
        Create an angle measurement tool.
        """
        angle_roi = AngleROI(viewer)
        viewer.getView().addItem(angle_roi)
        self.measurement_items.append(angle_roi)
        return angle_roi

    def clear_measurements(self, viewer):
        """
        Clear all measurement items from the viewer.
        """
        for item in self.measurement_items:
            viewer.getView().removeItem(item)
        self.measurement_items.clear()

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
        self.backend = backend
        self.annotations = []
        self.annotations_file = annotations_file
        self.load_annotations()
        
    def load_annotations(self):
        """Load annotations from JSON file."""
        if os.path.exists(self.annotations_file):
            try:
                with open(self.annotations_file, 'r') as f:
                    self.annotations = json.load(f)
            except json.JSONDecodeError:
                # Handle empty or corrupted file
                print(f"Warning: The annotations file '{self.annotations_file}' is empty or corrupted. Initializing empty annotations.")
                self.annotations = []
        else:
            self.annotations = []

        
    def save_annotations(self):
        """Save annotations to JSON file."""
        with open(self.annotations_file, 'w') as f:
            json.dump(self.annotations, f, indent=4)
        
    def add_text_annotation(self, viewer, text, position, metadata=None):
        """
        Add a text annotation and save to file.
        
        Args:
            viewer: Viewer object
            text: Annotation text
            position: Annotation position
            metadata: Optional additional information
        """
        annotation = {
            'text': text,
            'position': position,
            'metadata': metadata or {}
        }
        
        # Add to local list and save to file
        self.annotations.append(annotation)
        self.save_annotations()
        
        # Create visual annotation
        text_item = TextAnnotation(text, position)
        viewer.getView().addItem(text_item)
        return text_item
    
    def delete_annotation(self, annotation_text):
        """
        Delete an annotation by its text.
        
        Args:
            annotation_text: Text of annotation to delete
        """
        self.annotations = [
            ann for ann in self.annotations 
            if ann['text'] != annotation_text
        ]
        self.save_annotations()
    
    def clear_annotations(self, viewer):
        """
        Clear all annotations from viewer and JSON file.
        
        Args:
            viewer: Viewer object
        """
        # Remove visual annotations
        for annotation in self.annotations:
            # Assuming you have a way to remove text items from the viewer
            viewer.getView().removeItem(annotation)
        
        # Clear local list and file
        self.annotations.clear()
        self.save_annotations()

class TextAnnotation(QGraphicsTextItem):
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
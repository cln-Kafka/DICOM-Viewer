import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QInputDialog, QMenu


class AnnotationTool:
    def __init__(self, backend, annotations_file="annotations.json"):
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
                        print(
                            f"Warning: Viewer '{viewer_name}' not found for annotation '{ann}'"
                        )

                print(f"Annotations loaded from {self.annotations_file}")

            except json.JSONDecodeError:
                print(
                    f"Warning: The annotations file '{self.annotations_file}' is empty or corrupted."
                )
        else:
            print(f"No annotations file found at {self.annotations_file}")

    def save_annotations(self):
        """Save all annotations to the JSON file."""
        with open(self.annotations_file, "w") as f:
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
                None, "Add Annotation", "Enter annotation text:"
            )
            if not ok or not text:
                return None

        # Create text annotation item
        text_item = TextAnnotation(text, position)
        viewer.getView().addItem(text_item)

        # Determine the viewer's name
        viewer_name = next(
            (name for name, v in self.backend.viewers.items() if v == viewer), None
        )

        if viewer_name:
            # Store annotation details
            annotation = {
                "viewer": viewer_name,
                "text": text,
                "position": list(position),
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
            viewer_name = next(
                (name for name, v in self.backend.viewers.items() if v == viewer), None
            )
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
            if hasattr(self, "annotation_tool"):
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

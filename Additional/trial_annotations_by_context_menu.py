import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import json
import os


class AnnotationTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Menu bar
        self.menu_bar = QtWidgets.QMenuBar()
        self.layout.setMenuBar(self.menu_bar)

        # Annotations menu
        self.annotations_menu = self.menu_bar.addMenu("Annotations")
        save_action = self.annotations_menu.addAction("Save")
        load_action = self.annotations_menu.addAction("Load")

        save_action.triggered.connect(self.save_annotations)
        load_action.triggered.connect(self.load_annotations)

        # Create a PyQtGraph plot
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.plot = self.plot_widget.getPlotItem()

        # List to store added items
        self.annotations = []

        # Enable mouse interactions
        self.plot_widget.scene().sigMouseClicked.connect(self.on_mouse_clicked)

        # JSON file for saving/loading annotations
        self.annotations_file = "annotations.json"

    def add_annotation(self, text, position):
        """Add a text annotation to the plot."""
        text_item = pg.TextItem(text, anchor=(0.5, 0.5))
        text_item.setPos(*position)

        # Enable custom context menu for the text item
        text_item.setFlag(pg.TextItem.ItemIsSelectable, True)
        text_item.mousePressEvent = lambda event: self.show_context_menu(event, text_item)

        self.plot.addItem(text_item)
        self.annotations.append({"text": text, "position": position})

    def show_context_menu(self, event, text_item=None):
        """Show a context menu."""
        if event.button() == QtCore.Qt.RightButton:
            menu = QtWidgets.QMenu()

            if text_item:
                # Options for an existing annotation
                delete_action = menu.addAction("Delete Annotation")
                remove_action = menu.addAction("Remove Annotation")
            else:
                # Option for adding a new annotation
                add_action = menu.addAction("Add Annotation")

            # Convert QPointF to QPoint for the menu
            action = menu.exec_(QtCore.QPoint(int(event.screenPos().x()), int(event.screenPos().y())))

            if text_item:
                if action == delete_action:
                    self.delete_annotation(text_item)
                elif action == remove_action:
                    self.remove_annotation_visual(text_item)
            elif not text_item and action == add_action:
                self.add_annotation_dialog(event)

    def delete_annotation(self, text_item):
        """Remove the annotation from the plot and JSON file."""
        self.plot.removeItem(text_item)
        self.annotations = [
            ann for ann in self.annotations
            if ann["text"] != text_item.toPlainText()
        ]
        self.save_annotations()
        print(f"Annotation '{text_item.toPlainText()}' deleted!")

    def remove_annotation_visual(self, text_item):
        """Remove the annotation from the plot but keep it in the JSON file."""
        self.plot.removeItem(text_item)
        print(f"Annotation '{text_item.toPlainText()}' removed visually!")

    def add_annotation_dialog(self, event):
        """Show a dialog to add an annotation."""
        # Get the position of the right-click in data coordinates
        pos = self.plot_widget.plotItem.vb.mapSceneToView(event.scenePos())
        x, y = pos.x(), pos.y()

        # Create input dialog to get annotation text
        text, ok = QtWidgets.QInputDialog.getText(self, "Add Annotation", "Enter annotation text:")
        if ok and text:
            self.add_annotation(text, (x, y))
            print(f"Annotation '{text}' added at ({x:.2f}, {y:.2f})")

    def on_mouse_clicked(self, event):
        """Handle mouse clicks on the plot."""
        if event.button() == QtCore.Qt.RightButton:
            # Show context menu when right-clicking on the plot
            self.show_context_menu(event)

    def save_annotations(self):
        """Save annotations to a JSON file."""
        with open(self.annotations_file, "w") as f:
            json.dump(self.annotations, f, indent=4)
        print(f"Annotations saved to {self.annotations_file}")

    def load_annotations(self):
        """Load annotations from a JSON file."""
        if os.path.exists(self.annotations_file):
            with open(self.annotations_file, "r") as f:
                loaded_annotations = json.load(f)

            # Clear existing annotations
            for text_item in self.annotations:
                self.plot.removeItem(text_item)
            self.annotations = []

            # Add loaded annotations
            for ann in loaded_annotations:
                self.add_annotation(ann["text"], tuple(ann["position"]))
            print(f"Annotations loaded from {self.annotations_file}")
        else:
            print(f"No saved annotations found at {self.annotations_file}")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = AnnotationTool()
    window.show()

    app.exec_()

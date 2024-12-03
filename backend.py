import webbrowser

import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox
from pyqtgraph import ROI, ImageView, InfiniteLine, ViewBox

from core.comparison_renderer import ComparisonRenderer
from core.image_enhancer import ImageEnhancer
from core.image_loader import ImageLoader
from core.image_processor import ImageProcessor
from core.volume_renderer import VolumeRenderer
from ui.main_window import MainWindowUI
from ui.windowing_parameters_dialog import WindowingDialogUI
from utils.file_history_manager import FileHistoryManager


class DicomViewerBackend(QMainWindow, MainWindowUI):
    def __init__(self):
        super().__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        # Initialize components
        self.loaded_image_data = None
        self.spacing_info = None
        self.image_loader = ImageLoader()
        self.image_processor = ImageProcessor()

        # UI Variables
        self.crosshairs = {}

        # File history management
        self.file_history_manager = FileHistoryManager(
            self.ui.menuFile, self.import_image
        )

        # Connect UI actions
        self.init_ui_connections()

        # Setup crosshairs
        self.setup_crosshairs()

    def init_ui_connections(self):
        # File Menu
        self.ui.actionImport_NIFTI.triggered.connect(lambda: self.import_image("nii"))
        self.ui.actionImport_DICOM_Series.triggered.connect(
            lambda: self.import_image("series")
        )
        self.ui.actionImport_Sample_Image.triggered.connect(
            lambda: self.import_image(
                "nii", "assets/data/nifti/subject-01-flanker.nii.gz"
            )
        )
        self.ui.actionQuit_App.triggered.connect(self.exit_app)

        # View Menu
        self.ui.actionRuler.triggered.connect(lambda: self.ruler(self.ui.axial_viewer))
        self.ui.actionAngle.triggered.connect(self.angle)

        # Image Menu
        self.ui.actionWindowing.triggered.connect(self.windowing)
        self.ui.actionGuassian.triggered.connect(self.guassian_filter)
        self.ui.actionLaplacian.triggered.connect(self.laplacian_filter)
        self.ui.actionMedianFilter.triggered.connect(self.median_filter)
        self.ui.actionBilateralFilter.triggered.connect(self.bilateral_filter)
        self.ui.actionBuild_Surface.triggered.connect(self.build_surface)
        self.ui.actionComparison_Mode.triggered.connect(self.comparison_mode)

        # Help Menu
        self.ui.actionDocumentation.triggered.connect(self.open_docs)

    def import_image(self, image_type, file_path=None):
        try:
            if image_type == "nii":
                file_path = file_path or self.get_path("NIfTI Files (*.nii *.nii.gz)")
                if not file_path:
                    return

                self.loaded_image_data, self.spacing_info = (
                    self.image_loader.load_nifti(file_path)
                )

                # Initialize image processor with loaded data
                self.image_processor.set_image_data(self.loaded_image_data)

                # Add to file history
                self.file_history_manager.add_to_history(file_path, image_type)

                # Display views
                self.display_views()

            elif image_type == "series":
                directory = file_path or QFileDialog.getExistingDirectory(
                    self, "Select DICOM Directory"
                )
                if not directory:
                    return

                self.loaded_image_data, self.spacing_info = (
                    self.image_loader.load_dicom_series(directory)
                )

                # Initialize image processor with loaded data
                self.image_processor.set_image_data(self.loaded_image_data)

                # Add to file history
                self.file_history_manager.add_to_history(directory, image_type)

                # Display views
                self.display_views()

        except Exception as e:
            self.show_error_message(str(e))

    def get_path(self, file_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", file_type
        )
        return file_path

    def render_slice(self, image_view: ImageView, slice_data):
        """
        Renders a 2D slice in the given PyQtGraph ImageView.
        """
        # Rotate the image 90 degrees counterclockwise (to the left)
        rotated_slice = np.rot90(slice_data, k=-1)

        image_view.setImage(
            rotated_slice,
            autoRange=True,
            autoLevels=True,
            autoHistogramRange=False,
        )

    def display_views(self):
        if self.loaded_image_data is None:
            return

        views = {
            "axial": self.ui.axial_viewer,
            "sagittal": self.ui.sagittal_viewer,
            "coronal": self.ui.coronal_viewer,
        }

        for plane, widget in views.items():
            slice_data = self.image_processor.get_slice(plane)
            self.render_slice(widget, slice_data)

            # Get width and height of the slice
            width, height = slice_data.shape

            # Calculate the center of the image
            x_center = width / 2
            y_center = height / 2

            # Set the X and Y limits for the view
            widget.getView().setXRange(0, width, padding=0)
            widget.getView().setYRange(0, height, padding=0)
            # widget.getView().setLimits(
            #     xMin=0,
            #     xMax=width,
            #     yMin=0,
            #     yMax=height,
            # )

            # Center the view on the image
            widget.getView().setRange(
                xRange=(x_center - width / 2, x_center + width / 2),
                yRange=(y_center - height / 2, y_center + height / 2),
                padding=0,
            )

    def ruler(self, viewer: ImageView):
        viewer.addItem(ROI(viewer, [0, 0], [1, 1]))
        # viewer.ui.roiBtn.click()

    def angle(self):
        pass

    def build_surface(self):
        self.volume_renderer = VolumeRenderer()
        render_window, render_ineractor, _ = (
            self.volume_renderer.create_volume_renderer(
                self.loaded_image_data,
                self.spacing_info,
            )
        )
        render_window.Render()
        render_ineractor.Start()

    def comparison_mode(self):
        data_1_path = self.get_path("NIfTI Files (*.nii *.nii.gz)")
        data_2_path = self.get_path("NIfTI Files (*.nii *.nii.gz)")

        if not data_1_path or not data_2_path:
            return

        data_1, spacing_1 = self.image_loader.load_nifti(data_1_path)
        data_2, spacing_2 = self.image_loader.load_nifti(data_2_path)

        self.comparison_renderer = ComparisonRenderer()
        render_window, render_interactor = (
            self.comparison_renderer.create_comparison_mode_renderer(
                data_1, data_2, spacing_1, spacing_2
            )
        )

        render_window.Render()
        render_interactor.Start()

    def setup_crosshairs(self):
        views = {
            "axial": self.ui.axial_viewer.getView(),
            "sagittal": self.ui.sagittal_viewer.getView(),
            "coronal": self.ui.coronal_viewer.getView(),
        }

        for plane, view in views.items():
            h_line = InfiniteLine(angle=0, movable=False, pen="b")
            v_line = InfiniteLine(angle=90, movable=False, pen="b")
            view.addItem(h_line)
            view.addItem(v_line)
            self.crosshairs[plane] = {
                "h_line": h_line,
                "v_line": v_line,
            }

        # Connect the crosshairs to the update_crosshairs function
        for plane, view in views.items():
            h_line = self.crosshairs[plane]["h_line"]
            v_line = self.crosshairs[plane]["v_line"]
            self.update_crosshairs(view, h_line, v_line)

    def update_crosshairs(
        self,
        view: ViewBox,
        h_line: InfiniteLine,
        v_line: InfiniteLine,
    ):
        # Get the range of the view
        x_range, y_range = view.viewRange()
        # Calculate the center of the range
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        # Set the position of the crosshairs to the center
        h_line.setPos(y_center)
        v_line.setPos(x_center)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    def exit_app(self):
        self.close()

    def closeEvent(self, event):
        for viewer in [
            self.ui.axial_viewer,
            self.ui.sagittal_viewer,
            self.ui.coronal_viewer,
        ]:
            viewer.close()
        # Explicitly accept the close event (optional)
        event.accept()

    def open_docs(self):
        webbrowser.open(
            "https://github.com/hagersamir/DICOM-Viewer-Features/blob/main/README.md"
        )

    def windowing(self):
        self.image_enhancer = ImageEnhancer()
        window_level, window_width = self.get_windowing_parameters()
        self.loaded_image_data = self.image_enhancer.apply_window(
            self.loaded_image_data, window_level, window_width
        )
        self.display_views()

    def get_windowing_parameters(self):
        dialog = WindowingDialogUI()
        dialog.exec_()
        window_level = dialog.windowLevelDoubleSpinBox.value()
        window_width = dialog.windowWidthDoubleSpinBox.value()
        return window_level, window_width

    def guassian_filter(self):
        pass

    def laplacian_filter(self):
        pass

    def median_filter(self):
        pass

    def bilateral_filter(self):
        pass

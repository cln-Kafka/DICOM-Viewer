import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import ImageView, InfiniteLine


class MainWindowUI(object):
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        MainWindow.setObjectName("dicom_viewer_main_window")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.setEnabled(True)
        MainWindow.resize(1280, 720)
        MainWindow.setMinimumSize(QtCore.QSize(1280, 720))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777213))
        MainWindow.setWindowIcon(QtGui.QIcon("assets/icons/logo.png"))
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(9)
        MainWindow.setFont(font)
        MainWindow.setMouseTracking(False)
        MainWindow.setAcceptDrops(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Variables
        self.crosshairs = {}

        self.setup_viewers()
        self.setup_menu_bar(MainWindow)
        self.setup_status_bar(MainWindow)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    from pyqtgraph import ImageView

    def setup_viewers(self):
        # A layout to hold the viewer ports
        self.viewers_grid_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.main_layout.addLayout(self.viewers_grid_layout)

        # Adding 3 PyQtGraph ImageViews
        self.axial_viewer = ImageView(self.centralwidget)
        self.sagittal_viewer = ImageView(self.centralwidget)
        self.coronal_viewer = ImageView(self.centralwidget)

        # Place them in the grid layout
        self.viewers_grid_layout.addWidget(self.axial_viewer, 0, 0)
        self.viewers_grid_layout.addWidget(self.sagittal_viewer, 0, 1)
        self.viewers_grid_layout.addWidget(self.coronal_viewer, 0, 2)

        # Sync the viewers
        self.axial_viewer.getView().setXLink(self.sagittal_viewer.getView())
        self.axial_viewer.getView().setYLink(self.coronal_viewer.getView())
        self.sagittal_viewer.getView().setXLink(self.axial_viewer.getView())
        self.sagittal_viewer.getView().setYLink(self.coronal_viewer.getView())
        self.coronal_viewer.getView().setXLink(self.axial_viewer.getView())
        self.coronal_viewer.getView().setYLink(self.sagittal_viewer.getView())

        # Customize initial settings if needed
        self.setup_image_viewer(self.axial_viewer)
        self.setup_image_viewer(self.sagittal_viewer)
        self.setup_image_viewer(self.coronal_viewer)

        self.setup_crosshairs()

    def setup_image_viewer(self, viewer: ImageView):
        """
        Configure default settings for a PyQtGraph ImageView.

        :param viewer: Instance of pyqtgraph.ImageView to configure.
        """
        viewer.ui.histogram.hide()  # Hide histogram for simplicity (optional)
        viewer.ui.roiBtn.hide()  # Hide ROI button
        viewer.ui.menuBtn.hide()  # Hide menu button
        viewer.getView().setAspectLocked(True)  # Lock aspect ratio

    def setup_crosshairs(self):
        views = {
            "axial": self.axial_viewer.getView(),
            "sagittal": self.sagittal_viewer.getView(),
            "coronal": self.coronal_viewer.getView(),
        }

        for plane, view in views.items():
            h_line = InfiniteLine(angle=0, movable=False, pen="b")
            v_line = InfiniteLine(angle=90, movable=False, pen="b")
            view.addItem(h_line)
            view.addItem(v_line)
            self.crosshairs[plane] = {"h_line": h_line, "v_line": v_line}

    def setup_tools(self):
        self.tools_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.tools_widget = QtWidgets.QWidget(self.centralwidget)

        self.main_layout.addWidget(self.tools_widget)

    def setup_menu_bar(self, MainWindow: QtWidgets.QMainWindow):
        ## Menubar ##
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 28))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        ### File Menu ###
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menubar.addAction(self.menuFile.menuAction())

        #### File Menu Actions ####
        self.actionImport_NIFTI = QtWidgets.QAction(MainWindow)
        self.actionImport_NIFTI.setObjectName("actionImport_NIFTI")
        self.actionImport_NIFTI.setShortcut("Ctrl+I")
        self.actionImport_Sample_Image = QtWidgets.QAction(MainWindow)
        self.actionImport_Sample_Image.setObjectName("actionImport_Sample_Image")
        self.actionImport_DICOM_Series = QtWidgets.QAction(MainWindow)
        self.actionImport_DICOM_Series.setObjectName("actionImport_DICOM_Series")
        self.actionQuit_App = QtWidgets.QAction(MainWindow)
        self.actionQuit_App.setObjectName("actionQuit_App")
        self.actionQuit_App.setShortcut("Ctrl+Q")

        self.menuFile.addAction(self.actionImport_NIFTI)
        self.menuFile.addAction(self.actionImport_Sample_Image)
        self.menuFile.addAction(self.actionImport_DICOM_Series)
        self.menuFile.addAction(self.actionQuit_App)
        self.menuFile.addSeparator()

        ### Help Menu ###
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menubar.addAction(self.menuHelp.menuAction())

        #### Help Menu Actions ####
        self.actionDocumentation = QtWidgets.QAction(MainWindow)
        self.actionDocumentation.setObjectName("acitonDocumentation")
        self.actionDocumentation.setShortcut("Ctrl+D")
        self.menuHelp.addAction(self.actionDocumentation)

    def setup_status_bar(self, MainWindow: QtWidgets.QMainWindow):
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

    def open_docs(self):
        webbrowser.open(
            "https://github.com/hagersamir/DICOM-Viewer-Features/blob/main/README.md"
        )

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dicom Viewer"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionImport_NIFTI.setText(_translate("MainWindow", "Import NIFTI"))
        self.actionImport_Sample_Image.setText(
            _translate("MainWindow", "Import Sample Image")
        )
        self.actionImport_DICOM_Series.setText(
            _translate("MainWindow", "Import DICOM Series")
        )
        self.actionQuit_App.setText(_translate("MainWindow", "Quit App"))
        self.actionDocumentation.setText(_translate("MainWindow", "Documentation"))

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import HistogramLUTItem, ImageView, InfiniteLine


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

        self.setup_viewers()
        self.setup_tools()
        self.setup_toolbars(MainWindow)
        self.setup_menu_bar(MainWindow)
        self.setup_status_bar(MainWindow)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    from pyqtgraph import ImageView

    def setup_viewers(self):
        # A layout to hold the viewer ports
        self.ortho_view_layout = QtWidgets.QGridLayout()
        # Remove the space between the viewers
        self.ortho_view_layout.setSpacing(0)
        self.ortho_view_layout.setContentsMargins(0, 0, 0, 0)
        # Add the layout to the main layout
        self.main_layout.addLayout(self.ortho_view_layout)

        # Adding 3 PyQtGraph ImageViews
        self.axial_viewer = ImageView(self.centralwidget)
        self.sagittal_viewer = ImageView(self.centralwidget)
        self.coronal_viewer = ImageView(self.centralwidget)

        # Place them in the grid layout
        self.ortho_view_layout.addWidget(self.axial_viewer, 0, 0)
        self.ortho_view_layout.addWidget(self.sagittal_viewer, 0, 1)
        self.ortho_view_layout.addWidget(self.coronal_viewer, 0, 2)

        # Sync the viewers
        # self.sync_viewers()

        # Customize initial settings if needed
        self.setup_image_viewer(self.axial_viewer)
        self.setup_image_viewer(self.sagittal_viewer)
        self.setup_image_viewer(self.coronal_viewer)

    def sync_viewers(self):
        self.axial_viewer.getView().setXLink(self.sagittal_viewer.getView())
        self.axial_viewer.getView().setYLink(self.coronal_viewer.getView())
        self.sagittal_viewer.getView().setXLink(self.axial_viewer.getView())
        self.sagittal_viewer.getView().setYLink(self.coronal_viewer.getView())
        self.coronal_viewer.getView().setXLink(self.axial_viewer.getView())
        self.coronal_viewer.getView().setYLink(self.sagittal_viewer.getView())

    def setup_image_viewer(self, viewer: ImageView):
        """
        Configure default settings for a PyQtGraph ImageView.

        :param viewer: Instance of pyqtgraph.ImageView to configure.
        """
        # viewer.ui.histogram.hide()  # Hide histogram for simplicity (optional)
        viewer.ui.roiBtn.hide()  # Hide ROI button
        viewer.ui.menuBtn.hide()  # Hide menu button
        viewer.getView().setAspectLocked(True)  # Lock aspect ratio

    def setup_tools(self):
        # Main tools layout (already exists)
        self.tools_layout = QtWidgets.QVBoxLayout()
        self.tools_layout.setObjectName("tools_layout")

        # Frame to hold tools and split views (new frame)
        self.tools_frame = QtWidgets.QFrame(self.centralwidget)
        self.tools_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.tools_frame.setObjectName("tools_frame")
        self.tools_frame.setLayout(self.tools_layout)

        # QSplitter for resizable sections
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("main_splitter")

        # Setup overlay list and location panel
        self.setup_overlay_list()
        self.setup_location_panel()

        # Add the splitter to the tools layout
        self.tools_layout.addWidget(self.splitter)

        # Add the frame to the main layout
        self.main_layout.addWidget(self.tools_frame)

    def setup_overlay_list(self):
        # Left panel: Overlay List
        self.overlay_list = QtWidgets.QListWidget()
        self.overlay_list.setObjectName("overlay_list")
        self.overlay_list.addItems(
            ["Overlay 1", "Overlay 2", "Overlay 3"]
        )  # Example items
        self.splitter.addWidget(self.overlay_list)

        self.overlay_list_toolbar = QtWidgets.QToolBar("Overlay List Toolbar")
        self.overlay_list_toolbar.setObjectName("overlay_list_toolbar")
        self.overlay_list_toolbar.setMovable(False)
        self.overlay_list_toolbar.setOrientation(QtCore.Qt.Vertical)

    def setup_location_panel(self):
        # Right panel: Location Panel
        self.location_panel = QtWidgets.QFrame()
        self.location_panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.location_panel.setObjectName("location_panel")

        # Layout for the location panel
        self.location_layout = QtWidgets.QVBoxLayout(self.location_panel)
        self.location_layout.setObjectName("location_layout")

        # Coordinates section
        self.coord_label = QtWidgets.QLabel("Coordinates")
        self.location_layout.addWidget(self.coord_label)

        self.coord_grid_layout = QtWidgets.QGridLayout()

        self.x_label = QtWidgets.QLabel("X")
        self.x_value = QtWidgets.QLineEdit()
        self.x_value.setReadOnly(True)
        self.x_value.setText("-74.997")  # Example data
        self.coord_grid_layout.addWidget(self.x_label, 0, 0)
        self.coord_grid_layout.addWidget(self.x_value, 0, 1)

        self.y_label = QtWidgets.QLabel("Y")
        self.y_value = QtWidgets.QLineEdit()
        self.y_value.setReadOnly(True)
        self.y_value.setText("17.250")  # Example data
        self.coord_grid_layout.addWidget(self.y_label, 1, 0)
        self.coord_grid_layout.addWidget(self.y_value, 1, 1)

        self.z_label = QtWidgets.QLabel("Z")
        self.z_value = QtWidgets.QLineEdit()
        self.z_value.setReadOnly(True)
        self.z_value.setText("18.749")  # Example data
        self.coord_grid_layout.addWidget(self.z_label, 2, 0)
        self.coord_grid_layout.addWidget(self.z_value, 2, 1)

        self.location_layout.addLayout(self.coord_grid_layout)

        # Voxel Location section
        self.voxel_label = QtWidgets.QLabel("Voxel Value")
        self.voxel_value = QtWidgets.QLineEdit()
        self.voxel_value.setReadOnly(True)
        self.voxel_value.setText("181")  # Example data
        self.location_layout.addWidget(self.voxel_label)
        self.location_layout.addWidget(self.voxel_value)

        # Add the location panel to the splitter
        self.splitter.addWidget(self.location_panel)

    def setup_toolbars(self, MainWindow: QtWidgets.QMainWindow):
        self.setup_overlay_toolbar(MainWindow)
        # Break between toolbars
        MainWindow.addToolBarBreak(QtCore.Qt.TopToolBarArea)
        self.setup_ortho_toolbar(MainWindow)

    def setup_overlay_toolbar(self, MainWindow: QtWidgets.QMainWindow):
        # Overlay Toolbar
        self.overlay_toolbar = QtWidgets.QToolBar("Overlay Toolbar")
        self.overlay_toolbar.setObjectName("overlay_toolbar")
        self.overlay_toolbar.setMovable(False)
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.overlay_toolbar)

        # Add widgets to the Overlay Toolbar
        self.opacity_label = QtWidgets.QLabel("Opacity")
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)  # Default value
        self.overlay_toolbar.addWidget(self.opacity_label)
        self.overlay_toolbar.addWidget(self.opacity_slider)

        self.brightness_label = QtWidgets.QLabel("Brightness")
        self.brightness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.brightness_slider.setRange(-50, 50)
        self.brightness_slider.setValue(0)
        self.overlay_toolbar.addWidget(self.brightness_label)
        self.overlay_toolbar.addWidget(self.brightness_slider)

        self.contrast_label = QtWidgets.QLabel("Contrast")
        self.contrast_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.contrast_slider.setRange(-50, 50)
        self.contrast_slider.setValue(0)
        self.overlay_toolbar.addWidget(self.contrast_label)
        self.overlay_toolbar.addWidget(self.contrast_slider)

    def setup_ortho_toolbar(self, MainWindow: QtWidgets.QMainWindow):
        # Ortho Toolbar
        self.ortho_toolbar = QtWidgets.QToolBar("Ortho Toolbar")
        self.ortho_toolbar.setObjectName("ortho_toolbar")
        self.ortho_toolbar.setMovable(False)  # Disable dragging if needed
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.ortho_toolbar)

        # Add widgets to the Ortho Toolbar
        self.zoom_label = QtWidgets.QLabel("Zoom:")
        self.zoom_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.zoom_slider.setRange(10, 200)
        self.zoom_slider.setValue(100)
        self.ortho_toolbar.addWidget(self.zoom_label)
        self.ortho_toolbar.addWidget(self.zoom_slider)

        # Add buttons for other orthogonal view options
        self.ortho_button = QtWidgets.QPushButton("Reset View")
        self.ortho_toolbar.addWidget(self.ortho_button)

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

        ### View Menu ###
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menubar.addAction(self.menuView.menuAction())

        #### View Menu Actions ####
        self.actionRuler = QtWidgets.QAction(MainWindow)
        self.actionRuler.setObjectName("actionRuler")
        self.menuView.addAction(self.actionRuler)
        self.actionAngle = QtWidgets.QAction(MainWindow)
        self.actionAngle.setObjectName("actionAngle")
        self.menuView.addAction(self.actionAngle)

        ### Image Menu ###
        self.menuImage = QtWidgets.QMenu(self.menubar)
        self.menuImage.setObjectName("menuImage")
        self.menubar.addAction(self.menuImage.menuAction())

        #### Image Menu Actions ####
        self.actionBuild_Surface = QtWidgets.QAction(MainWindow)
        self.actionBuild_Surface.setObjectName("actionBuild_Surface")
        self.menuImage.addAction(self.actionBuild_Surface)
        self.actionComparison_Mode = QtWidgets.QAction(MainWindow)
        self.actionComparison_Mode.setObjectName("actionComparison_Mode")
        self.menuImage.addAction(self.actionComparison_Mode)

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

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dicom Viewer"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuImage.setTitle(_translate("MainWindow", "Image"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionImport_NIFTI.setText(_translate("MainWindow", "Import NIFTI"))
        self.actionImport_Sample_Image.setText(
            _translate("MainWindow", "Import Sample Image")
        )
        self.actionImport_DICOM_Series.setText(
            _translate("MainWindow", "Import DICOM Series")
        )
        self.actionQuit_App.setText(_translate("MainWindow", "Quit App"))
        self.actionRuler.setText(_translate("MainWindow", "Ruler"))
        self.actionAngle.setText(_translate("MainWindow", "Angle"))
        self.actionBuild_Surface.setText(_translate("MainWindow", "Build Surface"))
        self.actionComparison_Mode.setText(_translate("MainWindow", "Comparison Mode"))
        self.actionDocumentation.setText(_translate("MainWindow", "Documentation"))

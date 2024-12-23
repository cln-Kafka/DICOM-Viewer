from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import HistogramLUTItem, ImageView, InfiniteLine, ViewBox


class MainWindowUI(object):
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        MainWindow.setObjectName("dicom_viewer_main_window")
        # Not to block interactions with other windows of the app
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.setEnabled(True)
        MainWindow.resize(1280, 720)
        MainWindow.setMinimumSize(QtCore.QSize(1280, 720))
        # Commented the maximum size to allow resizing
        # MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777213))
        MainWindow.setWindowIcon(QtGui.QIcon("assets/icons/logo.png"))
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

        # Apply the font to all widgets
        self.apply_font_to_all_widgets(
            QtGui.QFont(
                "Poppins",
                9,
            ),
        )

    def setup_viewers(self):
        # A layout to hold the viewer ports
        self.ortho_view_layout = QtWidgets.QGridLayout()

        # Remove the space between the viewers
        self.ortho_view_layout.setSpacing(0)
        self.ortho_view_layout.setContentsMargins(0, 0, 0, 0)

        # Add the layout to the main layout of the app
        self.main_layout.addLayout(self.ortho_view_layout)

        # Adding 3 PyQtGraph ViewBoxes, ImageViews
        self.axial_view = ViewBox()
        self.axial_view.setObjectName("axial_view")
        self.sagittal_view = ViewBox()
        self.sagittal_view.setObjectName("sagittal_view")
        self.coronal_view = ViewBox()
        self.coronal_view.setObjectName("coronal_view")

        self.remove_global_views_link()

        self.axial_viewer = ImageView(self.centralwidget, view=self.axial_view)
        self.sagittal_viewer = ImageView(self.centralwidget, view=self.sagittal_view)
        self.coronal_viewer = ImageView(self.centralwidget, view=self.coronal_view)

        # Place them in the grid layout
        self.ortho_view_layout.addWidget(self.axial_viewer, 0, 0)
        self.ortho_view_layout.addWidget(self.sagittal_viewer, 0, 1)
        self.ortho_view_layout.addWidget(self.coronal_viewer, 0, 2)

        # Customize initial settings if needed
        self.setup_image_viewer(self.axial_viewer)
        self.setup_image_viewer(self.sagittal_viewer)
        self.setup_image_viewer(self.coronal_viewer)

    def remove_global_views_link(self):
        # Disable aspect ratio locking for all views
        self.axial_view.setAspectLocked(False)
        self.sagittal_view.setAspectLocked(False)
        self.coronal_view.setAspectLocked(False)
        # Unregister the global views
        self.axial_view.unregister()
        self.sagittal_view.unregister()
        self.coronal_view.unregister()
        # Remove the global view links
        self.axial_view.linkView(ViewBox.XAxis, None)
        self.axial_view.linkView(ViewBox.YAxis, None)
        self.sagittal_view.linkView(ViewBox.XAxis, None)
        self.sagittal_view.linkView(ViewBox.YAxis, None)
        self.coronal_view.linkView(ViewBox.XAxis, None)
        self.coronal_view.linkView(ViewBox.YAxis, None)

    def setup_image_viewer(self, viewer: ImageView):
        """
        Configure default settings for a PyQtGraph ImageView.

        :param viewer: Instance of pyqtgraph.ImageView to configure.
        """
        # viewer.ui.histogram.hide()
        viewer.ui.roiBtn.hide()
        viewer.ui.menuBtn.hide()
        viewer.getHistogramWidget().autoHistogramRange = False
        # viewer.getView().setAspectLocked(True)

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

        self.contrast_label = QtWidgets.QLabel("Contrast")
        self.contrast_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.contrast_slider.setRange(-50, 50)
        self.contrast_slider.setValue(0)
        self.overlay_toolbar.addWidget(self.contrast_label)
        self.overlay_toolbar.addWidget(self.contrast_slider)

        # Spacer
        spacer2 = QtWidgets.QWidget()
        spacer2.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        self.overlay_toolbar.addWidget(spacer2)

    def setup_ortho_toolbar(self, MainWindow: QtWidgets.QMainWindow):
        # Ortho Toolbar
        self.ortho_toolbar = QtWidgets.QToolBar("Ortho Toolbar")
        self.ortho_toolbar.setObjectName("ortho_toolbar")
        self.ortho_toolbar.setMovable(False)  # Disable dragging if needed
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.ortho_toolbar)

        # Add widgets to the Ortho Toolbar
        self.camera_button = QtWidgets.QPushButton()
        self.camera_button.setIcon(QtGui.QIcon("assets/icons/camera.png"))
        self.camera_button.setIconSize(QtCore.QSize(24, 24))
        self.ortho_toolbar.addWidget(self.camera_button)

        self.tracking_button = QtWidgets.QPushButton()
        self.tracking_button.setIcon(QtGui.QIcon("assets/icons/tracking.png"))
        self.tracking_button.setIconSize(QtCore.QSize(24, 24))
        self.tracking_button.setCheckable(True)
        self.tracking_button.setShortcut("Ctrl+X")
        self.ortho_toolbar.addWidget(self.tracking_button)

        self.reload_button = QtWidgets.QPushButton()
        self.reload_button.setIcon(QtGui.QIcon("assets/icons/reload.png"))
        self.reload_button.setIconSize(QtCore.QSize(24, 24))
        self.ortho_toolbar.addWidget(self.reload_button)

        # Add a horizontal spacer
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        self.ortho_toolbar.addWidget(spacer)

        # Add a notification button
        self.notification_button = QtWidgets.QPushButton()
        self.notification_button.setIcon(QtGui.QIcon("assets/icons/notification.png"))
        self.notification_button.setIconSize(QtCore.QSize(24, 24))
        self.ortho_toolbar.addWidget(self.notification_button)

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
        self.actionImport_Image = QtWidgets.QAction(MainWindow)
        self.actionImport_Image.setObjectName("actionImport_Image")
        self.actionImport_Image.setShortcut("Ctrl+I")
        self.actionImport_NIFTI = QtWidgets.QAction(MainWindow)
        self.actionImport_NIFTI.setObjectName("actionImport_NIFTI")
        self.actionImport_Sample_Image = QtWidgets.QAction(MainWindow)
        self.actionImport_Sample_Image.setObjectName("actionImport_Sample_Image")
        self.actionImport_DICOM_Series = QtWidgets.QAction(MainWindow)
        self.actionImport_DICOM_Series.setObjectName("actionImport_DICOM_Series")
        self.actionQuit_App = QtWidgets.QAction(MainWindow)
        self.actionImport_png = QtWidgets.QAction(MainWindow)
        self.actionImport_png.setObjectName("actionImport_png")
        self.actionImport_png.setShortcut("Ctrl+I")
        self.actionQuit_App.setObjectName("actionQuit_App")
        self.actionQuit_App.setShortcut("Ctrl+Q")

        self.menuFile.addAction(self.actionImport_Image)
        self.menuFile.addAction(self.actionImport_NIFTI)
        self.menuFile.addAction(self.actionImport_Sample_Image)
        self.menuFile.addAction(self.actionImport_DICOM_Series)
        self.menuFile.addAction(self.actionImport_png)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit_App)

        ### View Menu ###
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menubar.addAction(self.menuView.menuAction())

        #### View Menu Actions ####
        self.actionRuler = QtWidgets.QAction(MainWindow)
        self.actionRuler.setObjectName("actionRuler")
        self.actionRuler.setCheckable(True)
        self.menuView.addAction(self.actionRuler)
        self.showRuler = QtWidgets.QAction(MainWindow)
        self.showRuler.setObjectName("showRuler")
        self.showRuler.setCheckable(True)
        self.menuView.addAction(self.showRuler)
        self.actionAngle = QtWidgets.QAction(MainWindow)
        self.actionAngle.setObjectName("actionAngle")
        self.actionAngle.setCheckable(True)
        self.menuView.addAction(self.actionAngle)
        self.showAngle = QtWidgets.QAction(MainWindow)
        self.showAngle.setObjectName("showAngle")
        self.showAngle.setCheckable(True)
        self.menuView.addAction(self.showAngle)

        ### Annotation Menu ###
        self.menuAnnotations = QtWidgets.QMenu(self.menubar)
        self.menuAnnotations.setObjectName("menuAnnotations")
        self.menubar.addAction(self.menuAnnotations.menuAction())

        #### Annotation Menu Actions ####
        self.actionAdd_Text_Annotation = QtWidgets.QAction(
            MainWindow
        )  # Added action for text annotation
        self.actionAdd_Text_Annotation.setObjectName("actionAdd_Text_Annotation")
        self.menuAnnotations.addAction(self.actionAdd_Text_Annotation)
        self.actionClear_Annotations = QtWidgets.QAction(
            MainWindow
        )  # Added action for text annotation
        self.actionClear_Annotations.setObjectName("actionClear_Annotations")
        self.menuAnnotations.addAction(self.actionClear_Annotations)

        self.actionSave_Text_Annotation = QtWidgets.QAction(
            MainWindow
        )  # Added action for text annotation
        self.actionSave_Text_Annotation.setObjectName("actionSave_Text_Annotation")
        self.menuAnnotations.addAction(self.actionSave_Text_Annotation)

        self.actionLoad_Text_Annotation = QtWidgets.QAction(
            MainWindow
        )  # Added action for text annotation
        self.actionLoad_Text_Annotation.setObjectName("actionLoad_Text_Annotation")
        self.menuAnnotations.addAction(self.actionLoad_Text_Annotation)

        ### Image Menu ###
        self.menuImage = QtWidgets.QMenu(self.menubar)
        self.menuImage.setObjectName("menuImage")
        self.menubar.addAction(self.menuImage.menuAction())

        #### Image Menu Actions ####
        self.actionWindowing = QtWidgets.QAction(MainWindow)
        self.actionWindowing.setObjectName("actionWindowing")
        self.menuImage.addAction(self.actionWindowing)
        # Filters menu inside Image menu
        self.subMenuFilters = QtWidgets.QMenu(self.menuImage)
        self.subMenuFilters.setObjectName("subMenuFilters")
        self.menuImage.addMenu(
            self.subMenuFilters
        )  # Correct method for adding a submenu

        # Filters actions
        self.actionSmoothing = QtWidgets.QAction(MainWindow)
        self.actionSmoothing.setObjectName("actionSmoothing")
        self.subMenuFilters.addAction(self.actionSmoothing)

        self.actionSharpening = QtWidgets.QAction(MainWindow)
        self.actionSharpening.setObjectName("actionSharpening")
        self.subMenuFilters.addAction(self.actionSharpening)

        self.actionDenoising = QtWidgets.QAction(MainWindow)
        self.actionDenoising.setObjectName("actionDenoising")
        self.subMenuFilters.addAction(self.actionDenoising)

        # Add a separator between filters and other actions
        self.menuImage.addSeparator()

        # Additional actions inside the Image menu
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

    def apply_font_to_all_widgets(self, font):
        app = QtWidgets.QApplication.instance()
        for widget in app.allWidgets():
            widget.setFont(font)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dicom Viewer"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuAnnotations.setTitle(_translate("MainWindow", "Annotations"))
        self.menuImage.setTitle(_translate("MainWindow", "Image"))
        self.subMenuFilters.setTitle(_translate("MainWindow", "Filters"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionImport_Image.setText(_translate("MainWindow", "Import Image"))
        self.actionImport_NIFTI.setText(_translate("MainWindow", "Import NIFTI"))
        self.actionImport_Sample_Image.setText(
            _translate("MainWindow", "Import Sample Image")
        )
        self.actionImport_DICOM_Series.setText(
            _translate("MainWindow", "Import DICOM Series")
        )
        self.actionImport_png.setText(_translate("MainWindow", "Import PNG/JPG"))
        self.actionQuit_App.setText(_translate("MainWindow", "Quit App"))
        self.actionRuler.setText(_translate("MainWindow", "Ruler"))
        self.showRuler.setText(_translate("MainWindow", "Show Ruler"))
        self.actionAngle.setText(_translate("MainWindow", "Angle"))
        self.showAngle.setText(_translate("MainWindow", "Show Angle"))
        self.actionWindowing.setText(_translate("MainWindow", "Windowing"))
        self.actionSmoothing.setText(_translate("MainWindow", "Smoothing"))
        self.actionSharpening.setText(_translate("MainWindow", "Sharpening"))
        self.actionDenoising.setText(_translate("MainWindow", "Denoising"))

        # Add translations for new annotation actions
        self.actionAdd_Text_Annotation.setText(
            _translate("MainWindow", "Add Annotations")
        )
        self.actionClear_Annotations.setText(
            _translate("MainWindow", "Clear Annotations")
        )
        self.actionSave_Text_Annotation.setText(
            _translate("MainWindow", "Save Annotations")
        )
        self.actionLoad_Text_Annotation.setText(
            _translate("MainWindow", "Load Annotations")
        )

        self.actionBuild_Surface.setText(_translate("MainWindow", "Build Surface"))
        self.actionComparison_Mode.setText(_translate("MainWindow", "Comparison Mode"))
        self.actionDocumentation.setText(_translate("MainWindow", "Documentation"))

from PyQt5 import QtCore, QtGui, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from utils.interactor_styles import NoRotationInteractorStyle


class MainWindowUI(object):
    def setupUi(self, MainWindow):
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

        self.setup_viewers()
        self.setup_menu_bar(MainWindow)
        self.setup_status_bar(MainWindow)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setup_viewers(self):
        # A layout to hold the viewer ports
        self.viewers_grid_layout = QtWidgets.QGridLayout(self.centralwidget)
        # Adding 3 VTK render window interactors
        self.axial_viewer = QVTKRenderWindowInteractor(self.centralwidget)
        self.sagittal_viewer = QVTKRenderWindowInteractor(self.centralwidget)
        self.coronal_viewer = QVTKRenderWindowInteractor(self.centralwidget)
        # Place them in the grid layout
        self.viewers_grid_layout.addWidget(self.axial_viewer, 0, 0)
        self.viewers_grid_layout.addWidget(self.sagittal_viewer, 0, 1)
        self.viewers_grid_layout.addWidget(self.coronal_viewer, 0, 2)

        # Create a custom interactor style instance
        no_rotation_style = NoRotationInteractorStyle()

        # Set the custom style for each VTK viewer to disable the rotation
        self.axial_viewer.GetRenderWindow().GetInteractor().SetInteractorStyle(
            no_rotation_style
        )
        self.sagittal_viewer.GetRenderWindow().GetInteractor().SetInteractorStyle(
            no_rotation_style
        )
        self.coronal_viewer.GetRenderWindow().GetInteractor().SetInteractorStyle(
            no_rotation_style
        )

    def setup_menu_bar(self, MainWindow):
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
        self.actionImport_Sample_Image = QtWidgets.QAction(MainWindow)
        self.actionImport_Sample_Image.setObjectName("actionImport_Sample_Image")
        self.actionImport_DICOM_Series = QtWidgets.QAction(MainWindow)
        self.actionImport_DICOM_Series.setObjectName("actionImport_DICOM_Series")
        self.actionQuit_App = QtWidgets.QAction(MainWindow)
        self.actionQuit_App.setObjectName("actionQuit_App")

        self.menuFile.addAction(self.actionImport_NIFTI)
        self.menuFile.addAction(self.actionImport_Sample_Image)
        self.menuFile.addAction(self.actionImport_DICOM_Series)
        self.menuFile.addAction(self.actionQuit_App)
        self.menuFile.addSeparator()

        ### Help Menu ###
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menubar.addAction(self.menuHelp.menuAction())

        #### File Menu Actions ####
        self.actionDocumentation = QtWidgets.QAction(MainWindow)
        self.actionDocumentation.setObjectName("acitonDocumentation")
        self.menuHelp.addAction(self.actionDocumentation)

    def setup_status_bar(self, MainWindow):
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

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

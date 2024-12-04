from PyQt5 import QtCore, QtGui, QtWidgets


class WindowingDialogUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WindowingDialog):
        WindowingDialog.setObjectName("WindowingDialog")
        WindowingDialog.resize(295, 122)
        self.setWindowIcon(QtGui.QIcon("assets/icons/logo.png"))
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(9)
        WindowingDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(WindowingDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.controls_hlayout = QtWidgets.QHBoxLayout()
        self.controls_hlayout.setObjectName("controls_hlayout")
        self.parametersLabels_vlayout = QtWidgets.QVBoxLayout()
        self.parametersLabels_vlayout.setObjectName("parametersLabels_vlayout")
        self.windowLevel = QtWidgets.QLabel(WindowingDialog)
        self.windowLevel.setObjectName("windowLevel")
        self.parametersLabels_vlayout.addWidget(self.windowLevel)
        self.windowWidth = QtWidgets.QLabel(WindowingDialog)
        self.windowWidth.setObjectName("windowWidth")
        self.parametersLabels_vlayout.addWidget(self.windowWidth)
        self.controls_hlayout.addLayout(self.parametersLabels_vlayout)
        self.parametersSpinBoxes_vlayout = QtWidgets.QVBoxLayout()
        self.parametersSpinBoxes_vlayout.setObjectName("parametersSpinBoxes_vlayout")
        self.windowLevelDoubleSpinBox = QtWidgets.QDoubleSpinBox(WindowingDialog)
        self.windowLevelDoubleSpinBox.setObjectName("windowLevelDoubleSpinBox")
        self.windowLevelDoubleSpinBox.setValue(2000)
        self.windowLevelDoubleSpinBox.setMinimum(1.0)
        self.windowLevelDoubleSpinBox.setMaximum(10000.0)
        self.parametersSpinBoxes_vlayout.addWidget(self.windowLevelDoubleSpinBox)
        self.windowWidthDoubleSpinBox = QtWidgets.QDoubleSpinBox(WindowingDialog)
        self.windowWidthDoubleSpinBox.setObjectName("windowWidthDoubleSpinBox")
        self.windowWidthDoubleSpinBox.setValue(2000)
        self.windowWidthDoubleSpinBox.setMinimum(1.0)
        self.windowWidthDoubleSpinBox.setMaximum(10000.0)
        self.parametersSpinBoxes_vlayout.addWidget(self.windowWidthDoubleSpinBox)
        self.controls_hlayout.addLayout(self.parametersSpinBoxes_vlayout)
        self.verticalLayout.addLayout(self.controls_hlayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.applyWindowingButton = QtWidgets.QPushButton(WindowingDialog)
        self.applyWindowingButton.setObjectName("applyWindowingButton")
        self.horizontalLayout.addWidget(self.applyWindowingButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WindowingDialog)
        QtCore.QMetaObject.connectSlotsByName(WindowingDialog)

        # Connect the apply button to accept the dialog
        self.applyWindowingButton.clicked.connect(self.accept)

    def get_parameters(self):
        return (
            self.windowLevelDoubleSpinBox.value(),
            self.windowWidthDoubleSpinBox.value(),
        )

    def retranslateUi(self, WindowingDialog):
        _translate = QtCore.QCoreApplication.translate
        WindowingDialog.setWindowTitle(
            _translate("WindowingDialog", "Windowing Parameters")
        )
        self.windowLevel.setText(_translate("WindowingDialog", "Window Level"))
        self.windowWidth.setText(_translate("WindowingDialog", "Window Width"))
        self.applyWindowingButton.setText(_translate("WindowingDialog", "Apply"))

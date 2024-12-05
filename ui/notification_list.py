from PyQt5 import QtCore, QtGui, QtWidgets


class NotificationListDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, NotificationDialog):
        NotificationDialog.setObjectName("NotificationDialog")
        NotificationDialog.resize(295, 122)
        self.setWindowIcon(QtGui.QIcon("assets/icons/logo.png"))
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(9)
        NotificationDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(NotificationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.notificationList = QtWidgets.QListWidget(NotificationDialog)
        self.notificationList.setObjectName("notificationList")
        self.verticalLayout.addWidget(self.notificationList)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.okButton = QtWidgets.QPushButton(NotificationDialog)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(NotificationDialog)
        QtCore.QMetaObject.connectSlotsByName(NotificationDialog)

        # Connect the apply button to accept the dialog
        self.okButton.clicked.connect(self.accept)

    def retranslateUi(self, WindowingDialog):
        _translate = QtCore.QCoreApplication.translate
        WindowingDialog.setWindowTitle(_translate("WindowingDialog", "Notifications"))
        self.okButton.setText(_translate("WindowingDialog", "Ok"))

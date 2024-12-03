from PyQt5.QtCore import QCoreApplication, QMetaObject
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
)


class SmoothingAndSharpeningDialogUI(QDialog):
    def __init__(self, mode, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setupUi(self)

    def setupUi(self, SmoothingSharpeningDialog):
        SmoothingSharpeningDialog.resize(295, 122)
        self.setWindowIcon(QIcon("assets/icons/logo.png"))

        # Apply the font to the dialog
        font = QFont("Poppins", 9)
        self.setFont(font)

        self.mainLayout = QVBoxLayout(SmoothingSharpeningDialog)
        self.mainLayout.setObjectName("mainLayout")

        if self.mode == "Smoothing":
            SmoothingSharpeningDialog.setObjectName("Smoothing")
            self.setup_smoothing()
        elif self.mode == "Sharpening":
            SmoothingSharpeningDialog.setObjectName("Sharpening")
            self.setup_sharpening()

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.applyWindowingButton = QPushButton(SmoothingSharpeningDialog)
        self.applyWindowingButton.setObjectName("applyWindowingButton")
        self.horizontalLayout.addWidget(self.applyWindowingButton)

        self.mainLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SmoothingSharpeningDialog)
        QMetaObject.connectSlotsByName(SmoothingSharpeningDialog)

        # Connect signals
        self.applyWindowingButton.clicked.connect(self.accept)

    def setup_smoothing(self):
        # Sigma
        self.sigma_layout = QHBoxLayout()
        self.sigma_label = QLabel("Sigma")
        self.sigma_spinbox = QDoubleSpinBox()
        self.sigma_spinbox.setMinimum(0.1)
        self.sigma_spinbox.setMaximum(10)
        self.sigma_spinbox.setValue(1)
        self.sigma_layout.addWidget(self.sigma_label)
        self.sigma_layout.addWidget(self.sigma_spinbox)

        self.mainLayout.addLayout(self.sigma_layout)

        # Strength
        self.smoothing_strength_layout = QHBoxLayout()
        self.smoothing_strength_label = QLabel("Strength")
        self.smoothing_strength_spinbox = QDoubleSpinBox()
        self.smoothing_strength_spinbox.setMinimum(0.1)
        self.smoothing_strength_spinbox.setMaximum(3)
        self.smoothing_strength_spinbox.setValue(2)
        self.smoothing_strength_layout.addWidget(self.smoothing_strength_label)
        self.smoothing_strength_layout.addWidget(self.smoothing_strength_spinbox)

        self.mainLayout.addLayout(self.smoothing_strength_layout)

    def setup_sharpening(self):
        # Strength
        self.sharpening_strength_layout = QHBoxLayout()
        self.sharpening_strength_label = QLabel("Strength")
        self.sharpening_strength_spinbox = QDoubleSpinBox()
        self.sharpening_strength_spinbox.setMinimum(0.1)
        self.sharpening_strength_spinbox.setMaximum(3)
        self.sharpening_strength_spinbox.setValue(0.8)
        self.sharpening_strength_layout.addWidget(self.sharpening_strength_label)
        self.sharpening_strength_layout.addWidget(self.sharpening_strength_spinbox)

        self.mainLayout.addLayout(self.sharpening_strength_layout)

    def retranslateUi(self, SmoothingSharpeningDialog):
        _translate = QCoreApplication.translate
        if self.mode == "Smoothing":
            SmoothingSharpeningDialog.setWindowTitle(
                _translate("SmoothingAndSharpeningDialog", "Smoothing")
            )
        elif self.mode == "Sharpening":
            SmoothingSharpeningDialog.setWindowTitle(
                _translate("SmoothingAndSharpeningDialog", "Sharpening")
            )
        self.applyWindowingButton.setText(
            _translate("SmoothingAndSharpeningDialog", "Apply")
        )

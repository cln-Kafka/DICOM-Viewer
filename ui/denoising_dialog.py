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


class DenoisingDialogUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, DenoisingDialog):
        DenoisingDialog.setObjectName("FilteringDialog")
        DenoisingDialog.resize(295, 150)
        self.setWindowIcon(QIcon("assets/icons/logo.png"))

        # Apply the font to the dialog
        font = QFont("Poppins", 9)
        self.setFont(font)

        self.mainLayout = QVBoxLayout(DenoisingDialog)
        self.mainLayout.setObjectName("mainLayout")

        self.filterType_hlayout = QHBoxLayout()
        self.filterType_hlayout.setObjectName("filterType_hlayout")

        self.setupt_filters_types(DenoisingDialog)

        self.mainLayout.addLayout(self.filterType_hlayout)

        self.parameter_layout = QVBoxLayout()  # Layout for filter-specific parameters
        self.mainLayout.addLayout(self.parameter_layout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.applyWindowingButton = QPushButton(DenoisingDialog)
        self.applyWindowingButton.setObjectName("applyWindowingButton")
        self.horizontalLayout.addWidget(self.applyWindowingButton)

        self.mainLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DenoisingDialog)
        QMetaObject.connectSlotsByName(DenoisingDialog)

        # Connect signals
        self.applyWindowingButton.clicked.connect(self.accept)
        self.filtersComboBox.currentIndexChanged.connect(self.update_parameters)

        # Initialize with the first filter type
        self.update_parameters()

    def setupt_filters_types(self, FilteringDialog):
        self.filterType = QLabel(FilteringDialog)
        self.filterType.setObjectName("filterType")

        self.filtersComboBox = QComboBox(FilteringDialog)
        self.filtersComboBox.setObjectName("filtersComboBox")
        self.filtersComboBox.addItems(
            [
                "Median",
                "Bilateral",
            ],
        )
        self.filtersComboBox.setCurrentIndex(0)
        self.filterType_hlayout.addWidget(self.filterType)
        self.filterType_hlayout.addWidget(self.filtersComboBox)

    def median_parameters(self):
        # Median filter parameters
        kernel_layout = QHBoxLayout()
        kernel_label = QLabel("Kernel Size")
        kernel_spinbox = QSpinBox()
        kernel_spinbox.setMinimum(1)
        kernel_spinbox.setMaximum(11)
        kernel_spinbox.setValue(3)
        kernel_layout.addWidget(kernel_label)
        kernel_layout.addWidget(kernel_spinbox)
        return kernel_layout

    def bilateral_parameters(self):
        # Bilateral filter parameters
        bilateral_layout = QVBoxLayout()

        # Sigma Color
        sigma_color_layout = QHBoxLayout()
        sigma_color_label = QLabel("Sigma Color")
        sigma_color_spinbox = QDoubleSpinBox()
        sigma_color_spinbox.setMinimum(0.1)
        sigma_color_spinbox.setMaximum(10)
        sigma_color_spinbox.setValue(0.5)
        sigma_color_layout.addWidget(sigma_color_label)
        sigma_color_layout.addWidget(sigma_color_spinbox)

        # Sigma Spatial
        sigma_spatial_layout = QHBoxLayout()
        sigma_spatial_label = QLabel("Sigma Spatial")
        sigma_spatial_spinbox = QDoubleSpinBox()
        sigma_spatial_spinbox.setMinimum(1.0)
        sigma_spatial_spinbox.setMaximum(50)
        sigma_spatial_spinbox.setValue(15)
        sigma_spatial_layout.addWidget(sigma_spatial_label)
        sigma_spatial_layout.addWidget(sigma_spatial_spinbox)

        bilateral_layout.addLayout(sigma_color_layout)
        bilateral_layout.addLayout(sigma_spatial_layout)
        return bilateral_layout

    def update_parameters(self):

        # Clear the existing parameter layout
        while self.parameter_layout.count():
            child = self.parameter_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

        # Add the corresponding parameters based on the current filter type
        current_filter = self.filtersComboBox.currentText()
        if current_filter == "Median":
            self.parameter_layout.addLayout(self.median_parameters())
        elif current_filter == "Bilateral":
            self.parameter_layout.addLayout(self.bilateral_parameters())

    def clear_layout(self, layout):
        """Recursively clears all items in the given layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
        layout.deleteLater()

    def retranslateUi(self, DenoisingDialog):
        _translate = QCoreApplication.translate
        DenoisingDialog.setWindowTitle(
            _translate("FilteringDialog", "Filtering Parameters")
        )
        self.filterType.setText(_translate("FilteringDialog", "Filter Type"))
        self.applyWindowingButton.setText(_translate("FilteringDialog", "Apply"))

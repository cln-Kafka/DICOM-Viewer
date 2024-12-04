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

# class DenoisingDialogUI(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setupUi(self)

#     def setupUi(self, DenoisingDialog):
#         DenoisingDialog.setObjectName("FilteringDialog")
#         DenoisingDialog.resize(295, 150)
#         self.setWindowIcon(QIcon("assets/icons/logo.png"))

#         # Apply the font to the dialog
#         self.font = QFont("Poppins", 9)
#         self.setFont(self.font)

#         self.mainLayout = QVBoxLayout(DenoisingDialog)
#         self.mainLayout.setObjectName("mainLayout")

#         self.filterType_hlayout = QHBoxLayout()
#         self.filterType_hlayout.setObjectName("filterType_hlayout")

#         self.setup_filters_types_combo_box(DenoisingDialog)

#         self.mainLayout.addLayout(self.filterType_hlayout)

#         self.parameter_layout = QVBoxLayout()  # Layout for filter-specific parameters
#         self.mainLayout.addLayout(self.parameter_layout)

#         self.horizontalLayout = QHBoxLayout()
#         self.horizontalLayout.setObjectName("horizontalLayout")
#         spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
#         self.horizontalLayout.addItem(spacerItem)
#         self.applyWindowingButton = QPushButton(DenoisingDialog)
#         self.applyWindowingButton.setObjectName("applyWindowingButton")
#         self.horizontalLayout.addWidget(self.applyWindowingButton)

#         self.mainLayout.addLayout(self.horizontalLayout)

#         self.retranslateUi(DenoisingDialog)
#         QMetaObject.connectSlotsByName(DenoisingDialog)

#         # Connect signals
#         self.applyWindowingButton.clicked.connect(self.accept)
#         self.filtersComboBox.currentIndexChanged.connect(self.update_parameters)

#         # Initialize with the first filter type
#         self.update_parameters()

#     def setup_filters_types_combo_box(self, FilteringDialog):
#         self.filterType = QLabel(FilteringDialog)
#         self.filterType.setObjectName("filterType")

#         self.filtersComboBox = QComboBox(FilteringDialog)
#         self.filtersComboBox.setObjectName("filtersComboBox")
#         self.filtersComboBox.addItems(
#             [
#                 "Median",
#                 "Bilateral",
#             ],
#         )
#         self.filtersComboBox.setCurrentIndex(0)
#         self.filterType_hlayout.addWidget(self.filterType)
#         self.filterType_hlayout.addWidget(self.filtersComboBox)

#     def median_parameters(self):
#         # Median filter parameters
#         kernel_layout = QHBoxLayout()
#         kernel_label = QLabel("Kernel Size")
#         kernel_label.setFont(self.font)
#         kernel_spinbox = QSpinBox()
#         kernel_spinbox.setMinimum(1)
#         kernel_spinbox.setMaximum(11)
#         kernel_spinbox.setValue(3)
#         kernel_layout.addWidget(kernel_label)
#         kernel_layout.addWidget(kernel_spinbox)
#         return kernel_layout

#     def bilateral_parameters(self):
#         # Bilateral filter parameters
#         bilateral_layout = QVBoxLayout()

#         # Sigma Color
#         sigma_color_layout = QHBoxLayout()
#         sigma_color_label = QLabel("Sigma Color")
#         sigma_color_label.setFont(self.font)
#         sigma_color_spinbox = QDoubleSpinBox()
#         sigma_color_spinbox.setMinimum(0.1)
#         sigma_color_spinbox.setMaximum(10)
#         sigma_color_spinbox.setValue(0.5)
#         sigma_color_layout.addWidget(sigma_color_label)
#         sigma_color_layout.addWidget(sigma_color_spinbox)

#         # Sigma Spatial
#         sigma_spatial_layout = QHBoxLayout()
#         sigma_spatial_label = QLabel("Sigma Spatial")
#         sigma_spatial_label.setFont(self.font)
#         sigma_spatial_spinbox = QDoubleSpinBox()
#         sigma_spatial_spinbox.setMinimum(1.0)
#         sigma_spatial_spinbox.setMaximum(50)
#         sigma_spatial_spinbox.setValue(15)
#         sigma_spatial_layout.addWidget(sigma_spatial_label)
#         sigma_spatial_layout.addWidget(sigma_spatial_spinbox)

#         bilateral_layout.addLayout(sigma_color_layout)
#         bilateral_layout.addLayout(sigma_spatial_layout)
#         return bilateral_layout

#     def update_parameters(self):

#         # Clear the existing parameter layout
#         while self.parameter_layout.count():
#             child = self.parameter_layout.takeAt(0)
#             if child.widget():
#                 child.widget().deleteLater()
#             elif child.layout():
#                 self.clear_layout(child.layout())

#         # Add the corresponding parameters based on the current filter type
#         current_filter = self.filtersComboBox.currentText()
#         if current_filter == "Median":
#             self.parameter_layout.addLayout(self.median_parameters())
#         elif current_filter == "Bilateral":
#             self.parameter_layout.addLayout(self.bilateral_parameters())

#     def clear_layout(self, layout):
#         """Recursively clears all items in the given layout."""
#         while layout.count():
#             child = layout.takeAt(0)
#             if child.widget():
#                 child.widget().deleteLater()
#             elif child.layout():
#                 self.clear_layout(child.layout())
#         layout.deleteLater()

#     def get_parameters(self):
#         current_filter = self.filtersComboBox.currentText()
#         if current_filter == "Median":
#             kernel_size = None
#             return current_filter, [kernel_size]
#         elif current_filter == "Bilateral":
#             sigma_color = None
#             sigma_spatial = None
#             return current_filter, [sigma_color, sigma_spatial]

#     def retranslateUi(self, DenoisingDialog):
#         _translate = QCoreApplication.translate
#         DenoisingDialog.setWindowTitle(
#             _translate("FilteringDialog", "Filtering Parameters")
#         )
#         self.filterType.setText(_translate("FilteringDialog", "Filter Type"))
#         self.applyWindowingButton.setText(_translate("FilteringDialog", "Apply"))


class DenoisingDialogUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, DenoisingDialog):
        DenoisingDialog.setObjectName("FilteringDialog")
        DenoisingDialog.resize(295, 200)
        self.setWindowIcon(QIcon("assets/icons/logo.png"))

        # Apply the font to the dialog
        self.font = QFont("Poppins", 9)
        self.setFont(self.font)

        self.mainLayout = QVBoxLayout(DenoisingDialog)
        self.mainLayout.setObjectName("mainLayout")

        # Filter type selection
        self.filterType_hlayout = QHBoxLayout()
        self.filterType_hlayout.setObjectName("filterType_hlayout")
        self.setup_filters_types_combo_box(DenoisingDialog)
        self.mainLayout.addLayout(self.filterType_hlayout)

        # Kernel size parameter (for Median filter)
        self.kernel_layout = QHBoxLayout()
        self.kernel_label = QLabel("Kernel Size")
        self.kernel_label.setFont(self.font)
        self.kernel_spinbox = QSpinBox()
        self.kernel_spinbox.setMinimum(1)
        self.kernel_spinbox.setMaximum(11)
        self.kernel_spinbox.setValue(3)
        self.kernel_layout.addWidget(self.kernel_label)
        self.kernel_layout.addWidget(self.kernel_spinbox)
        self.mainLayout.addLayout(self.kernel_layout)

        # Sigma Color parameter (for Bilateral filter)
        self.sigma_color_layout = QHBoxLayout()
        self.sigma_color_label = QLabel("Sigma Color")
        self.sigma_color_label.setFont(self.font)
        self.sigma_color_spinbox = QDoubleSpinBox()
        self.sigma_color_spinbox.setMinimum(0.1)
        self.sigma_color_spinbox.setMaximum(10)
        self.sigma_color_spinbox.setValue(0.5)
        self.sigma_color_layout.addWidget(self.sigma_color_label)
        self.sigma_color_layout.addWidget(self.sigma_color_spinbox)
        self.mainLayout.addLayout(self.sigma_color_layout)

        # Sigma Spatial parameter (for Bilateral filter)
        self.sigma_spatial_layout = QHBoxLayout()
        self.sigma_spatial_label = QLabel("Sigma Spatial")
        self.sigma_spatial_label.setFont(self.font)
        self.sigma_spatial_spinbox = QDoubleSpinBox()
        self.sigma_spatial_spinbox.setMinimum(1.0)
        self.sigma_spatial_spinbox.setMaximum(50)
        self.sigma_spatial_spinbox.setValue(15)
        self.sigma_spatial_layout.addWidget(self.sigma_spatial_label)
        self.sigma_spatial_layout.addWidget(self.sigma_spatial_spinbox)
        self.mainLayout.addLayout(self.sigma_spatial_layout)

        # Buttons
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

        # Initialize visibility
        self.update_parameters()

    def setup_filters_types_combo_box(self, FilteringDialog):
        self.filterType = QLabel(FilteringDialog)
        self.filterType.setObjectName("filterType")

        self.filtersComboBox = QComboBox(FilteringDialog)
        self.filtersComboBox.setObjectName("filtersComboBox")
        self.filtersComboBox.addItems(["Median", "Bilateral"])
        self.filtersComboBox.setCurrentIndex(0)
        self.filterType_hlayout.addWidget(self.filterType)
        self.filterType_hlayout.addWidget(self.filtersComboBox)

    def update_parameters(self):
        # Show/Hide parameters based on the selected filter
        current_filter = self.filtersComboBox.currentText()
        if current_filter == "Median":
            self.kernel_label.show()
            self.kernel_spinbox.show()
            self.sigma_color_label.hide()
            self.sigma_color_spinbox.hide()
            self.sigma_spatial_label.hide()
            self.sigma_spatial_spinbox.hide()
        elif current_filter == "Bilateral":
            self.kernel_label.hide()
            self.kernel_spinbox.hide()
            self.sigma_color_label.show()
            self.sigma_color_spinbox.show()
            self.sigma_spatial_label.show()
            self.sigma_spatial_spinbox.show()

    def get_parameters(self):
        """
        Get the current filter parameters.

        Returns:
            Tuple[str, list]: Filter name and corresponding parameters.
        """
        current_filter = self.filtersComboBox.currentText()
        if current_filter == "Median":
            kernel_size = self.kernel_spinbox.value()
            return current_filter, [kernel_size]
        elif current_filter == "Bilateral":
            sigma_color = self.sigma_color_spinbox.value()
            sigma_spatial = self.sigma_spatial_spinbox.value()
            return current_filter, [sigma_color, sigma_spatial]

    def retranslateUi(self, DenoisingDialog):
        _translate = QCoreApplication.translate
        DenoisingDialog.setWindowTitle(
            _translate("FilteringDialog", "Filtering Parameters")
        )
        self.filterType.setText(_translate("FilteringDialog", "Filter Type"))
        self.applyWindowingButton.setText(_translate("FilteringDialog", "Apply"))

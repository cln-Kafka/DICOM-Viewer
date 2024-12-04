import sys

import qdarktheme
from PyQt5.QtWidgets import QApplication

from backend import DicomViewerBackend


def main():
    app = QApplication(sys.argv)
    main_window = DicomViewerBackend()
    main_window.show()
    qdarktheme.setup_theme("light")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

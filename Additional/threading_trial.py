import sys
import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget


class WorkerThread(QThread):
    # Define a signal to communicate with the GUI
    progress = pyqtSignal(str)

    def run(self):
        for i in range(5):
            time.sleep(1)  # Simulate a time-consuming task
            self.progress.emit(f"Step {i + 1}/5 completed")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.label = QLabel("Press the button to start a task")
        self.button = QPushButton("Start Task")
        self.button.clicked.connect(self.start_thread)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.worker = WorkerThread()
        self.worker.progress.connect(self.update_label)

    def start_thread(self):
        self.button.setEnabled(False)  # Disable button during processing
        self.worker.start()

    def update_label(self, message):
        self.label.setText(message)
        if "completed" in message and "Step 5" in message:
            self.button.setEnabled(True)  # Re-enable button after task ends


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

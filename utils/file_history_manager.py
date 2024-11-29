import os

from PyQt5.QtWidgets import QAction


class FileHistoryManager:
    def __init__(self, menu, import_callback):
        self.menu = menu
        self.import_callback = import_callback
        self.loaded_paths_history = {}

    def add_to_history(self, file_path, file_type):
        if file_path not in self.loaded_paths_history:
            self.loaded_paths_history[file_path] = file_type
            self._update_menu()

    def _update_menu(self):
        # Clear previous history actions
        for action in self.menu.actions():
            if not action.objectName():
                self.menu.removeAction(action)

        self.menu.addSeparator()

        # Add history actions
        for file_path, file_type in self.loaded_paths_history.items():
            file_name = os.path.basename(file_path)
            history_action = QAction(file_name, self.menu.parent())
            history_action.setData((file_path, file_type))
            history_action.triggered.connect(
                lambda checked, path=file_path, type=file_type: self.import_callback(
                    type, path
                )
            )
            self.menu.addAction(history_action)

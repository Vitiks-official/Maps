from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt


class MyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            self.parent().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

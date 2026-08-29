from typing import Optional
from PySide6.QtWidgets import QFileDialog, QWidget

class FileManager(QFileDialog):
    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)

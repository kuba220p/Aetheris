import os
from typing import Optional
from PySide6.QtWidgets import QWidget, QComboBox
from PySide6.QtCore import Slot


class ComboBox(QComboBox):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

    @Slot(str)
    def add_file(self, file_path: str) -> None:
        name = os.path.basename(file_path)
        self.addItem(name, file_path)
        self.setCurrentText(name)

    @Slot(list)
    def set_items(self, items: list[str]) -> None:
        self.clear()
        self.addItems(items)

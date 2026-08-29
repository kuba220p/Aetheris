from typing import Optional
from collections.abc import Callable
from PySide6.QtWidgets import QPushButton, QWidget

class Button(QPushButton):
    def __init__(
            self, 
            text: str, 
            min_width: int,
            min_height: int,
            max_width: Optional[int]=None,
            max_height: Optional[int]=None,
            parent: Optional[QWidget]=None
        ) -> None:

        super().__init__(text, parent)

        self.setText(text)

        self.setMinimumWidth(min_width)
        self.setMinimumHeight(min_height)

        if max_width:
            self.setMaximumWidth(max_width)
        if max_height:
            self.setMaximumHeight(max_height)

    def add_action(self, func: Callable) -> None:
        self.clicked.connect(func)

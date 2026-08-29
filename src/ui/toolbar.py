from typing import Optional
from collections.abc import Callable
from PySide6.QtWidgets import QToolBar, QWidget, QMenu, QToolButton
from PySide6.QtGui import QAction
from PySide6.QtCore import QSize, Qt

class ToolBar(QToolBar):
    def __init__(
            self, 
            parent: Optional[QWidget] = None
        ) -> None:

        super().__init__(parent)

        self.setIconSize(QSize(20, 20))
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)


    def add_action(self, func: Callable, action: str, tooltip: Optional[str]=None) -> QAction:
        act = QAction(action, self)
        if tooltip:
            act.setToolTip(tooltip)
        act.triggered.connect(func)
        self.addAction(act)
        return act

    def add_menu(self, title: str, options: dict[str, Callable]) -> QToolButton:
        btn = QToolButton(self)
        btn.setText(title)
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu(btn)
        for label, callback in options.items():
            act = menu.addAction(label)
            act.triggered.connect(callback)

        btn.setMenu(menu)
        self.addWidget(btn)
        return btn
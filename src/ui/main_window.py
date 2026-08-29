from src.GEELoader import gee_loader
from src.ui.button import Button
from src.ui.canvas import MapCanvas
from src.ui.toolbar import ToolBar

from PySide6.QtWidgets import QMainWindow, QGridLayout, QWidget
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, project_id: str) -> None:
        super().__init__()
        self.setWindowTitle("Aetheris")
        self.resize(1280, 800)

        self.loader = gee_loader.Loader(project_id)
        self._create_toolbar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout(central_widget)

        right_layout = QGridLayout()
        left_layout = QGridLayout()


        self.canvas = MapCanvas()

        left_layout.addWidget(self.canvas)

        layout.addLayout(left_layout, 0, 0)
        layout.addLayout(right_layout, 0, 1)

    def _create_toolbar(self) -> None:
        self.toolbar = ToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.toolbar.add_menu(
            title="File",
            options={
                "Open": self.open_file,
                "Export": self.export_file,
            })

    def open_file(self) -> None:
        print("opening file...")

    def export_file(self) -> None:
        print("exporting file...")
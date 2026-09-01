from src.GEELoader import gee_loader
from src.ui.canvas import MapCanvas
from src.ui.toolbar import ToolBar
from src.FileManager import file_manager
from src.ui.combo import ComboBox
from src.ui.download_dialog import DownloadDialog
from src.EEWorker import ee_worker

from PySide6.QtWidgets import QMainWindow, QGridLayout, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Slot

class MainWindow(QMainWindow):
    def __init__(self, project_id: str) -> None:
        super().__init__()
        self.setWindowTitle("Aetheris")
        self.resize(1280, 800)
        self.canvas = MapCanvas()
        self.loader = gee_loader.Loader(project_id)
        self.download_dialog = DownloadDialog(self)

        self.download_dialog.downloadRequested.connect(self.handle_download_request)

        self._create_file_manager()
        self._create_toolbar()
        

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout(central_widget)

        right_layout = QGridLayout()
        left_layout = QGridLayout()

        self.file_selection_combo = ComboBox(self)
        self.band_selection_combo = ComboBox(self)

        combo_layout = QHBoxLayout()
        combo_layout.addWidget(self.file_selection_combo)
        combo_layout.addWidget(self.band_selection_combo)       

        left_layout.addLayout(combo_layout, 0, 0)
        left_layout.addWidget(self.canvas)

        layout.addLayout(left_layout, 0, 0)
        layout.addLayout(right_layout, 0, 1)

        self.canvas_connections()
        self.combo_connections()

    def _create_toolbar(self) -> None:
        self.toolbar = ToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.toolbar.add_menu(
            title="File",
            options={
                "Open": self.file_manager.open,
                "Export": self.export_file,
                "Download": self.download_dialog.show
            })

    @Slot(dict)
    def handle_download_request(self, request: dict) -> None:
        request["max_cloud"] = 10.0
        self.worker = ee_worker.Worker(self.loader, request)
        self.worker.finished.connect(self._download_finished)
        self.worker.error.connect(self._download_error)

        self.worker.start()

    def _download_finished(self, previews: dict) -> None:
        print(previews)

    def _download_error(self, error: str) -> None:
        print(error)

    def combo_connections(self) -> None:
        self.band_selection_combo.currentIndexChanged.connect(self.on_band_selection_changed)
        self.file_selection_combo.currentIndexChanged.connect(self.on_file_selection_changed)

    def canvas_connections(self) -> None:
        self.canvas.signals.fileLoaded.connect(self.file_selection_combo.add_file)
        self.canvas.signals.bandsLoaded.connect(self.band_selection_combo.set_items)

    def _create_file_manager(self) -> None:
        self.file_manager = file_manager.FileManager()
        self.file_manager.fileSelected.connect(self.canvas.load_img_bands)

    def export_file(self) -> None:
        print("exporting file...")

    def on_file_selection_changed(self, index: int) -> None:
        self.canvas.change_file(self.file_selection_combo.itemData(index))

    def on_band_selection_changed(self, index: int) -> None:
        band_name = self.band_selection_combo.itemText(index)
        file_path = self.file_selection_combo.currentData()
        self.canvas.change_band(file_path, band_name)
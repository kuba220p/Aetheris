from PySide6.QtCore import QThread, Signal
from src.GEELoader import gee_loader

class Worker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, loader: gee_loader.Loader, request: dict) -> None:
        super().__init__()
        self.loader = loader
        self.request = request

    def run(self) -> None:
        try:
            previews = self.loader.fetch_previews(**self.request)
            self.finised.emit(previews)
        except Exception as e:
            self.error.emit(str(e))

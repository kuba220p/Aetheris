from typing import Optional
import rasterio
import numpy as np
import re

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QWidget
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt, Signal, QObject

class CanvasSignals(QObject):
    fileLoaded = Signal(str)
    bandsLoaded = Signal(object)

class MapCanvas(QGraphicsView):
    def __init__(
            self, 
            parent: Optional[QWidget]=None
        ) -> None:

        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.signals = CanvasSignals()
        self._images: dict[str, dict[str, QImage]] = {}

    def load_img_bands(self, img_path: str) -> None:
        print(img_path)
        img: rasterio.DatasetReader
        with rasterio.open(img_path, mode="r") as img:
            self._images[img_path] = {}
            for index, desc in enumerate(img.descriptions, start=1):
                self.add_band(img_path, desc, self.make_qimage(img.read(index)))

            self.show_img(self.get_band(img_path, img.descriptions[0]))

        self.emit_file(img_path)

    def emit_file(self, img_path: str) -> None:
        bands = list(self._images.get(img_path, {}).keys())
        self.signals.fileLoaded.emit(img_path)
        self.signals.bandsLoaded.emit(bands)

    def show_img(self, qimage: QImage) -> None:
        if not qimage:
            raise ValueError("Attempt to open empty Image!")
        self.pixmap_item.setPixmap(QPixmap.fromImage(qimage))
  
    def add_band(self, filename: str, band: str, qimage: QImage) -> None:
        self._images[filename].update({band: qimage})

    def get_band(self, filename: str, band: str) -> QImage | None:
        return self._images.get(filename, {}).get(band, None)

    def make_qimage(self, array: np.array) -> QImage:
        arr_min = float(np.nanmin(array))
        arr_max = float(np.nanmax(array))

        if arr_max > arr_min:
            arr_8bit = ((array - arr_min) / (arr_max - arr_min) * 255.0).astype(np.uint8)
        else:
            arr_8bit = np.zeros(array.shape, dtype=np.uint8)

        arr_contigous = np.ascontiguousarray(arr_8bit)
        h, w = arr_contigous.shape
        return QImage(arr_contigous.data, w, h, w, QImage.Format.Format_Grayscale8).copy()

    def change_file(self, filename: str) -> None:
        bands = list(self._images.get(filename, {}).keys())
        if bands:
            self.show_img(self.get_band(filename, bands[0]))
            self.signals.bandsLoaded.emit(bands)

    def change_band(self, filename: str, band: str) -> None:
        qimage = self.get_band(filename, band)
        if qimage is not None:
            self.show_img(qimage)
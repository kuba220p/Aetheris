from typing import Optional
import ee
from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QPushButton, QLineEdit, QCalendarWidget, QCheckBox
from PySide6.QtCore import Signal

class DownloadDialog(QDialog):
    downloadRequested = Signal(dict)

    def __init__(self, parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Download Data")
        self.setModal(False)

        layout = QFormLayout(self)

        self.start_date_input = QCalendarWidget()
        layout.addRow(QLabel("Start Date:"))
        layout.addRow(self.start_date_input)

        self.end_date_input = QCalendarWidget()
        layout.addRow(QLabel("End Date:"))
        layout.addRow(self.end_date_input)

        self.min_latitude_input = QLineEdit()
        self.max_latitude_input = QLineEdit()

        self.min_longitude_input = QLineEdit()
        self.max_longitude_input = QLineEdit()

        layout.addRow(QLabel("Latitude:"))
        layout.addRow(QLabel("Min:"), self.min_latitude_input)
        layout.addRow(QLabel("Max:"), self.max_latitude_input)

        layout.addRow(QLabel("Longitude:"))
        layout.addRow(QLabel("Min:"), self.min_longitude_input)
        layout.addRow(QLabel("Max:"), self.max_longitude_input)

        layout.addRow(QLabel("Select Data Sources:"))
        self.download_sentinel_2 = QCheckBox("Sentinel-2")
        self.download_sentinel_1 = QCheckBox("Sentinel-1")

        layout.addRow(self.download_sentinel_2, self.download_sentinel_1)

        self.download_button = QPushButton("Download")
        self.download_button.setEnabled(False)
        layout.addRow(self.download_button)

        self.min_latitude_input.textChanged.connect(self._validate)
        self.max_latitude_input.textChanged.connect(self._validate)
        self.min_longitude_input.textChanged.connect(self._validate)
        self.max_longitude_input.textChanged.connect(self._validate)

        self.download_sentinel_1.toggled.connect(self._validate)
        self.download_sentinel_2.toggled.connect(self._validate)

        self.start_date_input.selectionChanged.connect(self._validate)
        self.end_date_input.selectionChanged.connect(self._validate)

        self.download_button.clicked.connect(self._download)

    def _validate(self) -> None: self.download_button.setEnabled(self._valid_coords() and self._valid_sources() and self._valid_dates())

    def _valid_sources(self) -> bool: return self.download_sentinel_1.isChecked() or self.download_sentinel_2.isChecked()

    def _valid_coords(self) -> bool:
        try:
            min_lat = float(self.min_latitude_input.text())
            max_lat = float(self.max_latitude_input.text())
            min_lon = float(self.min_longitude_input.text())
            max_lon = float(self.max_longitude_input.text())

            return (-90.0 <= min_lat < max_lat <= 90.0) and \
                   (-180.0 <= min_lon < max_lon <= 180.0)

        except ValueError:
            return False

    def _valid_dates(self) -> bool:
        start_date = self.start_date_input.selectedDate()
        end_date = self.end_date_input.selectedDate()

        return start_date.isValid() and end_date.isValid() and start_date <= end_date

    def _download(self) -> None:
        aoi = ee.Geometry.Rectangle([
            float(self.min_longitude_input.text()),
            float(self.min_latitude_input.text()),
            float(self.max_longitude_input.text()),
            float(self.max_latitude_input.text())
        ])

        data = {
            "start_date": self.start_date_input.selectedDate().toString("yyyy-MM-dd"),
            "end_date": self.end_date_input.selectedDate().toString("yyyy-MM-dd"),
            "aoi": aoi,
            "source": []
        }

        if self.download_sentinel_1.isChecked():
            data["source"].append("Sentinel-1")
        if self.download_sentinel_2.isChecked():
            data["source"].append("Sentinel-2")

        self.downloadRequested.emit(data)
        self.accept()

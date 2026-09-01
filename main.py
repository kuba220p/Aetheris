from src.GEELoader import gee_loader
from PySide6.QtWidgets import QApplication
import ee
from dotenv import load_dotenv
import os
import sys
from src.ui import main_window

def main():
    load_dotenv()
    app = QApplication(sys.argv)
    win = main_window.MainWindow(os.getenv("PROJECT_ID"))
    win.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
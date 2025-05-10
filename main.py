# gcs/main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from newDesign import Ui_MainWindow  # Qt Designer çıkışı
from ui.main_window_controller import MainWindowController


def main():
    """
    Uygulamanın giriş noktası.
    Qt arayüzünü başlatır ve MainWindowController ile bağlantıyı kurar.
    """
    app = QApplication(sys.argv)

    # Ana pencereyi oluştur
    main_window = QMainWindow()

    # Arayüzü başlat
    ui = Ui_MainWindow()
    ui.setupUi(main_window)

    # Kontrolcüyü başlat (UI eventlerini bağlar)
    controller = MainWindowController(ui)

    # Buton olaylarını bağla
    ui.exit_pushButton.clicked.connect(main_window.close)
    ui.minimize_pushButton.clicked.connect(main_window.showMinimized)

    # Pencereyi göster
    main_window.show()

    # Event loop başlat
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

# login_logic.py

import os
import subprocess
import time
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QMessageBox

class LoginHandler(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.login_disabled = False

    @pyqtSlot(str, str)
    def kullanici_dogrula(self, kullanici, sifre):
        if self.login_disabled:
            return
        self.login_disabled = True

        dogru_bilgiler = {
            "ilayda": "boncuk",
            "sude": "baykuş"
        }

        if kullanici in dogru_bilgiler and dogru_bilgiler[kullanici] == sifre:
            self.uygulamayi_baslat()
        else:
            QMessageBox.warning(None, "Hatalı Giriş", "Kullanıcı adı veya şifre yanlış.")
            self.login_disabled = False  # hatalıysa tekrar girişe izin ver

    def uygulamayi_baslat(self):
        try:
            main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
            subprocess.Popen([
                "python", main_path
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            time.sleep(3.5)
            self.window.close()
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"main.py çalıştırılamadı:\n{str(e)}")
            self.login_disabled = False

# login_ui.py

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoginWindow(object):
    def setupUi(self, MainWindow, handler):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setStyleSheet("")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.background = QtWidgets.QLabel(self.centralwidget)
        self.background.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.background.setPixmap(QtGui.QPixmap("Login_Screen.png"))
        self.background.setObjectName("background")

        self.giris_yap = QtWidgets.QPushButton(self.centralwidget)
        self.giris_yap.setGeometry(QtCore.QRect(870, 770, 121, 28))
        self.giris_yap.setObjectName("giris_yap")
        self.giris_yap.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
                color: white;
            }
        """)

        self.cikis_yap = QtWidgets.QPushButton(self.centralwidget)
        self.cikis_yap.setGeometry(QtCore.QRect(1860, 20, 31, 28))
        self.cikis_yap.setObjectName("cikis_yap")
        self.cikis_yap.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
                color: white;
            }
        """)
        self.cikis_yap.clicked.connect(QtWidgets.qApp.quit)

        self.mini = QtWidgets.QPushButton(self.centralwidget)
        self.mini.setGeometry(QtCore.QRect(1820, 20, 31, 28))
        self.mini.setObjectName("mini")
        self.mini.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
                color: white;
            }
        """)
        self.mini.setText("")
        self.mini.clicked.connect(MainWindow.showMinimized)

        self.sifre = QtWidgets.QLineEdit(self.centralwidget)
        self.sifre.setGeometry(QtCore.QRect(810, 683, 261, 22))
        self.sifre.setEchoMode(QtWidgets.QLineEdit.Password)
        self.sifre.setObjectName("sifre")
        self.sifre.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0);
            }
        """)

        self.isim = QtWidgets.QLineEdit(self.centralwidget)
        self.isim.setGeometry(QtCore.QRect(810, 614, 261, 22))
        self.isim.setObjectName("isim")
        self.isim.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0);
            }
        """)

        self.giris_yap.clicked.connect(lambda: handler.kullanici_dogrula(self.isim.text(), self.sifre.text()))

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Giriş Ekranı"))

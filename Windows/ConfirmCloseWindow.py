from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QPushButton

class ConfirmCloseWindow(QWidget):
    def __init__(self, parent=None):
        super(ConfirmCloseWindow, self).__init__(parent)

        self.setWindowTitle('Выход')
        self.setGeometry(500, 500, 1000, 1000)
        self.exitButton = QPushButton('Выйти'.upper(), self)
        self.back2lobbyButton = QPushButton('Назад'.upper(), self)
        self.exitButton.setGeometry(0, 0, 100, 50)
        self.back2lobbyButton.setGeometry(100, 0, 100, 50)
        self.back2lobbyButton.setFont(QFont("Times New Roman", 12))
        self.exitButton.setFont(QFont("Times New Roman", 12))
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QPushButton

class LobbyWindow(QWidget):
    def __init__(self, parent=None):
        super(LobbyWindow, self).__init__(parent)
        self.buttonStart = QPushButton(self)
        self.buttonStat = QPushButton(self)
        self.buttonExit = QPushButton(self)
        self.gameName = QLabel(self)


        self.gameName.setText("ГЛЯДЕЛКИ")
        self.gameName.setFont(QFont("Arial BLACK", 72))
        self.gameName.setGeometry(695, 180, 350, 100)
        self.gameName.adjustSize()
        self.gameName.setAlignment(Qt.AlignCenter)


        self.buttonStat.setText("Статистика".upper())
        self.buttonStat.maximumSize()
        self.buttonStat.move(100, 100)
        self.buttonStat.setGeometry(810, 500, 350, 100)
        self.buttonStat.setFont(QFont("Times New Roman", 32))


        self.buttonStart.setText("Начать игру".upper())
        self.buttonStart.move(100, 100)
        self.buttonStart.setGeometry(810, 390, 350, 100)
        self.buttonStart.maximumSize()
        self.buttonStart.setFont(QFont("Times New Roman", 32))


        self.buttonExit.setText("Выйти из игры".upper())
        self.buttonExit.maximumSize()
        self.buttonExit.move(100, 100)
        self.buttonExit.setGeometry(810, 610, 350, 100)
        self.buttonExit.setFont(QFont("Times New Roman", 32))
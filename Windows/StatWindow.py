from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QPushButton


class StatWindow(QWidget):
    def __init__(self, parent=None):
        super(StatWindow, self).__init__(parent)
        self.back2lobbyButton = QPushButton('Назад'.upper(), self)
        self.back2lobbyButton.maximumSize()
        self.back2lobbyButton.move(100, 100)
        self.back2lobbyButton.setGeometry(810, 780, 350, 100)
        self.back2lobbyButton.setFont(QFont("Times New Roman", 32))
        self.gameName = QLabel(self)


        self.gameName.setText("СТАТИСТИКА")
        self.gameName.setFont(QFont("Arial BLACK", 72))
        self.gameName.setGeometry(600, 50, 350, 100)
        self.gameName.adjustSize()
        self.gameName.setAlignment(Qt.AlignCenter)

        self.checkStat = QListWidget(self)
        self.checkStat.show()
        count = 1

        with open('stat.txt', 'r', encoding='utf-8') as file:
            for s in file.readlines():
                self.checkStat.addItem(f'{count}) {s}')
                count += 1
        self.checkStat.setGeometry(745, 200, 480, 500)
        self.checkStat.setFont(QFont('Arial BLACK', 18))

import cv2
import sys
from Windows import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.showMaximized()
        self.startLobbyWindow()


    def startLobbyWindow(self):
        self.ToolTab = LobbyWindow(self)
        self.setWindowTitle("Гляделки")
        self.setCentralWidget(self.ToolTab)
        self.ToolTab.buttonStart.clicked.connect(self.startGameWindow)
        self.ToolTab.buttonStat.clicked.connect(self.startStatWindow)
        self.ToolTab.buttonExit.clicked.connect(self.startConfirmCloseWindow)
        self.showMaximized()


    def startGameWindow(self):
        self.Window = BlinkWindow()
        self.setWindowTitle("Гляделки")
        self.setCentralWidget(self.Window)

        self.Window.back2lobbyButton.clicked.connect(self.startLobbyWindow)
        self.showMaximized()


    def startStatWindow(self):
        self.Window = StatWindow(self)
        self.setWindowTitle("Гляделки")
        self.setCentralWidget(self.Window)
        self.Window.back2lobbyButton.clicked.connect(self.startLobbyWindow)
        self.showMaximized()


    def closeWindow(self):
        self.close()


    def startConfirmCloseWindow(self):
        self.Window = ConfirmCloseWindow(self)
        self.setCentralWidget(self.Window)
        self.showNormal()
        self.Window.back2lobbyButton.clicked.connect(self.startLobbyWindow)
        self.Window.exitButton.clicked.connect(self.closeWindow)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
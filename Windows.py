import cv2
import dlib
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QPushButton
from scipy.spatial import distance

class Game(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(733, 532)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.startBlinkButton = QPushButton(self.centralwidget)
        self.startBlinkButton.setGeometry(QRect(180, 389, 398, 86))
        self.startBlinkButton.setObjectName("pushButton")
        self.labelTimer = QLabel(self.centralwidget)
        self.labelTimer.setGeometry(QRect(680, 50, 600, 300))
        self.labelTimer.maximumSize()
        font = QFont('Arial BLACK', 36)
        font.setStyleStrategy(QFont.PreferAntialias)
        self.labelTimer.setFont(font)
        self.labelTimer.setAlignment(Qt.AlignCenter)
        self.labelTimer.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        QMetaObject.connectSlotsByName(MainWindow)

        self.exitLabel = QLabel(self.centralwidget)
        self.exitLabel.setGeometry(50, 480, 1000, 600)
        self.exitLabel.setText('Для окончания игры моргни')
        self.exitLabel.setFont(QFont('Arial Black', 36))

class BlinkWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()


        self.count = 0
        self.flag = False


        self.startBlinkButton.setText("НАЧАТЬ ИГРУ")
        self.startBlinkButton.setFont(QFont("Times New Roman", 32))
        self.startBlinkButton.clicked.connect(self.click_button)
        self.startBlinkButton.setGeometry(810, 480, 350, 100)


        self.back2lobbyButton = QPushButton('Назад'.upper(), self)
        self.back2lobbyButton.setGeometry(810, 600, 350, 100)
        self.back2lobbyButton.setFont(QFont("Times New Roman", 32))
        self.back2lobbyButton.hide()


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.exitLabel.hide()


        self.cameraLabel = QLabel(self)
        self.cameraLabel.setGeometry(760, 0, 400, 250)  # Размеры для показа видео
        self.cameraLabel.hide()


        self.loopedVideoLabel = QLabel(self)
        self.loopedVideoLabel.setGeometry(0, 0, 1920, 1080)  # Размеры для показа зацикленного видео
        self.loopedVideoLabel.hide()


        self.loopedVideoPath = "video.mp4"
        self.loopedVideoCap = None
        self.loopedVideoTimer = QTimer(self)



        self.cap = None
        self.videoTimer = QTimer(self)

        # Детектор лиц и предсказатель точек лица
        self.hog_face_detector = dlib.get_frontal_face_detector()
        self.dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(733, 532)


        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)


        self.startBlinkButton = QPushButton(self.centralwidget)
        self.startBlinkButton.setGeometry(QRect(180, 389, 398, 86))


        self.labelTimer = QLabel(self.centralwidget)
        self.labelTimer.setGeometry(QRect(680, 50, 600, 300))
        font = QFont('Arial BLACK', 36)
        font.setStyleStrategy(QFont.PreferAntialias)
        self.labelTimer.setFont(font)
        self.labelTimer.setAlignment(Qt.AlignCenter)
        self.labelTimer.setObjectName("label")


        self.exitLabel = QLabel(self.centralwidget)
        self.exitLabel.setGeometry(QRect(50, 480, 1000, 600))
        self.exitLabel.setText('Для окончания игры моргни')
        self.exitLabel.setFont(QFont('Arial Black', 36))

        QMetaObject.connectSlotsByName(self)

    def click_button(self):
        self.Start()
        self.startBlinkButton.hide()
        self.exitLabel.show()
        self.back2lobbyButton.show()


        self.cap = cv2.VideoCapture(0)
        self.cameraLabel.show()

        if self.cap.isOpened():
            self.videoTimer.timeout.connect(self.update_frame)
            self.videoTimer.start(30)


        self.loopedVideoCap = cv2.VideoCapture(self.loopedVideoPath)
        self.loopedVideoLabel.show()

        if self.loopedVideoCap.isOpened():
            self.loopedVideoTimer.timeout.connect(self.update_looped_video)
            self.loopedVideoTimer.start(30)

        self.cameraLabel.raise_()

    def calculate_EAR(self, eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear_aspect_ratio = (A + B) / (2.0 * C)
        return ear_aspect_ratio

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.hog_face_detector(gray)

            for face in faces:
                landmarks = self.dlib_facelandmark(gray, face)

                leftEye = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)]
                rightEye = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)]

                # Обводка левого глаза
                for i in range(6):
                    cv2.line(frame, leftEye[i], leftEye[(i + 1) % 6], (0, 255, 0), 1)

                # Обводка правого глаза
                for i in range(6):
                    cv2.line(frame, rightEye[i], rightEye[(i + 1) % 6], (0, 255, 0), 1)


                # left_ear = self.calculate_EAR(leftEye)
                # right_ear = self.calculate_EAR(rightEye)
                # EAR = (left_ear + right_ear) / 2
                #
                # if EAR < 0.26:
                #     cv2.putText(frame, "BLINK", (20, 100),
                #                 cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 4)


            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            qt_image = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            self.cameraLabel.setPixmap(QPixmap.fromImage(qt_image))

    def update_looped_video(self):
        ret, frame = self.loopedVideoCap.read()
        if not ret:
            self.loopedVideoCap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.loopedVideoCap.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytesPerLine = ch * w
        qt_image = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.loopedVideoLabel.setPixmap(QPixmap.fromImage(qt_image))


    def showTime(self):
        if self.flag:
            self.count += 1
        text = str(self.count / 10)
        self.labelTimer.setText(text)
        self.labelTimer.setFont(QFont("Arial BLACK", 140))

    def Start(self):
        self.flag = True
        self.timer.start(100)

    def Pause(self):
        self.flag = False
        self.timer.stop()

    def closeEvent(self, event):
        if self.cap:
            self.videoTimer.stop()
            self.cap.release()
        event.accept()


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

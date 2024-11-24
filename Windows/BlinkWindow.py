import cv2
import dlib
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QPushButton
from scipy.spatial import distance
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class BlinkWindow(QMainWindow):
    time_updated = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setupUi()


        # Счетчик времени
        self.count = 0
        # Флаг для отслеживания состояния моргания
        self.blinking = False


        self.startBlinkButton.setText("НАЧАТЬ ИГРУ")
        self.startBlinkButton.setFont(QFont("Times New Roman", 32))
        self.startBlinkButton.clicked.connect(self.click_button)
        self.startBlinkButton.setGeometry(810, 480, 350, 100)


        self.back2lobbyButton = QPushButton('Назад'.upper(), self)
        self.back2lobbyButton.setGeometry(810, 600, 350, 100)
        self.back2lobbyButton.setFont(QFont("Times New Roman", 32))
        # self.back2lobbyButton.hide()
        self.back2lobbyButton.raise_()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        # self.timer.raise_()
        self.exitLabel.hide()


        self.cameraLabel = QLabel(self)
        self.cameraLabel.setGeometry(760, 0, 400, 250)  # Размеры для показа видео
        self.cameraLabel.hide()

        # Добавьте QLabel для затемнения

        self.overlayLabel = QLabel(self)
        self.overlayLabel.setGeometry(0, 0, 1920, 1080)
        self.overlayLabel.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # прозрачный черный
        self.overlayLabel.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.overlayLabel.raise_()

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


        # Лейбл для отображения таймера
        # self.labelTimer = QLabel(self.centralwidget)
        # self.labelTimer.setGeometry(QRect(680, 50, 600, 300))
        # font = QFont('Arial BLACK', 36)
        # font.setStyleStrategy(QFont.PreferAntialias)
        # self.labelTimer.setFont(font)
        # self.labelTimer.setAlignment(Qt.AlignCenter)
        # self.labelTimer.setObjectName("label")
        # self.labelTimer.setStyleSheet("background-color: rgba(255, 255, 255, 150); color: black;")
        # self.labelTimer.raise_()


        self.exitLabel = QLabel(self.centralwidget)
        self.exitLabel.setGeometry(QRect(50, 480, 1000, 600))
        self.exitLabel.setText('Для окончания игры моргни')
        self.exitLabel.setFont(QFont('Arial Black', 36))

        QMetaObject.connectSlotsByName(self)

    def click_button(self):
        self.startBlinking()
        self.startBlinkButton.hide()
        # self.exitLabel.show()
        # self.back2lobbyButton.show()
        # self.labelTimer.show()
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
        # self.labelTimer.raise_()

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


                left_ear = self.calculate_EAR(leftEye)
                right_ear = self.calculate_EAR(rightEye)
                EAR = (left_ear + right_ear) / 2

                if EAR < 0.26:
                    if not self.blinking:
                        self.blinking = True
                        self.count = 0  # Сброс счетчика
                        self.timer.start(100)  # Запуск таймера
                else:
                    if self.blinking:
                        self.blinking = False
                        # print(self.labelTimer.text())
                        self.timer.stop()  # Остановка таймера


            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            qt_image = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            self.cameraLabel.setPixmap(QPixmap.fromImage(qt_image))
            self.overlayLabel.show()
            self.overlayLabel.raise_()
            # self.labelTimer.show()
            # self.labelTimer.raise_()

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
        # self.labelTimer.show()
        # self.labelTimer.raise_()


    def showTime(self):
        if self.blinking:
            self.count += 1
        else:
            self.count = 0
        text = str(self.count / 10)
        # self.labelTimer.setText(text)
        # self.labelTimer.setFont(QFont("Arial BLACK", 140))
        # Обновляем уровень затемнения в зависимости от времени
        max_time = 5  # Максимальное время для полного затемнения
        opacity = min(self.count / (max_time * 10), 1) if self.blinking else 0  # Рассчитываем степень затемнения (0 до 1)
        alpha = int(opacity * 255)

        # Динамически обновляем background-color для overlayLabel
        self.overlayLabel.setStyleSheet(f"background-color: rgba(0, 0, 0, {alpha});")
        # self.time_updated.emit(opacity)
        # self.opacity_effect.setOpacity(opacity)


    def startBlinking(self):
        self.timer.start(100)


    def closeEvent(self, event):
        if self.cap:
            self.videoTimer.stop()
            self.cap.release()
        event.accept()
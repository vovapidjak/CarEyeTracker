import cv2
import dlib
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QPushButton
from scipy.spatial import distance
from datetime import datetime

class BlinkWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.dark_souls_triggered = None
        self.darkSoulsLabel = None
        self.darkSoulsTimer = None
        self.darkSoulsCap = None
        self.setupUi()

        self.dark_souls_triggered = False  # Флаг для предотвращения повторного запуска

        self.face_detected = False  # Флаг для проверки, выполнено ли обнаружение лица
        self.face_coords = None  # Координаты обнаруженного лица
        # Счетчик времени
        self.count = 0
        # Флаг для отслеживания состояния моргания
        self.blinking = False

        self.total_time = 0  # Общее время, пока opacity < 1
        self.recording_time = False  # Флаг для отслеживания записи времени
        self.stat_timer = QTimer(self)  # Таймер для увеличения общего времени
        self.stat_timer.timeout.connect(self.increment_total_time)

        self.startBlinkButton.setText("НАЧАТЬ ИГРУ")
        self.startBlinkButton.setFont(QFont("Times New Roman", 32))
        self.startBlinkButton.clicked.connect(self.click_button)
        self.startBlinkButton.setGeometry(810, 480, 350, 100)


        # self.back2lobbyButton = QPushButton('Назад'.upper(), self)
        # self.back2lobbyButton.setGeometry(810, 600, 350, 100)
        # self.back2lobbyButton.setFont(QFont("Times New Roman", 32))
        # self.back2lobbyButton.raise_()


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.exitLabel.hide()


        self.cameraLabel = QLabel(self)
        self.cameraLabel.setGeometry(760, 0, 400, 250)  # Размеры для показа видео
        self.cameraLabel.hide()


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

        self.exitLabel = QLabel(self.centralwidget)
        self.exitLabel.setGeometry(QRect(50, 480, 1000, 600))
        self.exitLabel.setText('Для окончания игры моргни')
        self.exitLabel.setFont(QFont('Arial Black', 36))

        QMetaObject.connectSlotsByName(self)

    def click_button(self):
        self.startBlinking()
        self.startBlinkButton.hide()
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

            if not self.face_detected:
                # Выполняем обнаружение лица
                faces = self.detect_faces(frame)
                if faces:
                    face = faces[0]
                    x, y, w, h = (face.left(), face.top(), face.width(), face.height())
                    x, y = max(0, x), max(0, y)

                    # Сохраняем координаты и выставляем флаг
                    self.face_coords = (x, y, w, h)
                    self.face_detected = True

            if self.face_detected and self.face_coords:
                # Используем сохраненные координаты для обрезки
                x, y, w, h = self.face_coords
                cropped_face = frame[y:y + h, x:x + w].copy()  # Обрезаем область лица

                # Пересчитываем координаты глаз относительно cropped_face
                for face in faces:
                    landmarks = self.dlib_facelandmark(gray, face)

                    leftEye = [(landmarks.part(n).x - x, landmarks.part(n).y - y) for n in range(36, 42)]
                    rightEye = [(landmarks.part(n).x - x, landmarks.part(n).y - y) for n in range(42, 48)]

                    # Обводка левого глаза
                    for i in range(6):
                        cv2.line(cropped_face, leftEye[i], leftEye[(i + 1) % 6], (0, 255, 0), 1)

                    # Обводка правого глаза
                    for i in range(6):
                        cv2.line(cropped_face, rightEye[i], rightEye[(i + 1) % 6], (0, 255, 0), 1)

                # Конвертируем и отображаем обрезанное лицо с обводкой
                cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                h, w, ch = cropped_face.shape
                bytesPerLine = ch * w
                qt_image = QImage(cropped_face.data, w, h, bytesPerLine, QImage.Format_RGB888)
                self.cameraLabel.setPixmap(QPixmap.fromImage(qt_image))
                self.cameraLabel.show()
            else:
                # Если лицо не обнаружено, показываем исходное изображение
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytesPerLine = ch * w
                qt_image = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
                self.cameraLabel.setPixmap(QPixmap.fromImage(qt_image))
                self.cameraLabel.show()


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

            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # h, w, ch = frame.shape
            # bytesPerLine = ch * w
            # qt_image = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            # self.cameraLabel.setPixmap(QPixmap.fromImage(qt_image))
            # self.cameraLabel.setGeometry()
            self.overlayLabel.show()
            self.overlayLabel.raise_()


    def detect_faces(self, frame):
        # Пример использования Dlib для обнаружения лиц
        detector = dlib.get_frontal_face_detector()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        return faces


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


    def increment_total_time(self):
        if self.recording_time:
            self.total_time += 1


    def showTime(self):
        if self.blinking:
            self.count += 1
        else:
            self.count = 0
        # Обновляем уровень затемнения в зависимости от времени
        max_time = 5  # Максимальное время для полного затемнения
        opacity = min(self.count / (max_time * 10), 1) if self.blinking else 0  # Рассчитываем степень затемнения (0 до 1)
        alpha = int(opacity * 255)

        # Динамически обновляем background-color для overlayLabel
        self.overlayLabel.setStyleSheet(f"background-color: rgba(0, 0, 0, {alpha});")

        if opacity < 1:
            if not self.recording_time:
                self.recording_time = True
                self.stat_timer.start(100)  # Обновляем каждые 1 секунду
        else:
            if self.recording_time:
                self.recording_time = False
                self.stat_timer.stop()

                # Записываем общее время в статистику
                total_time_seconds = self.total_time / 10
                self.write_stat(total_time_seconds)
                self.total_time = 0  # Сброс времени

        if opacity == 1 and not self.dark_souls_triggered:
            self.dark_souls_triggered = True
            self.overlayLabel.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Сбрасываем затемнение

            # Останавливаем видео
            self.stop_camera_video()
            self.stop_main_video()

            # Запускаем воспроизведение darksouls.mp4
            self.play_dark_souls_video()

    def write_stat(self, total_time):
        # Получаем текущую дату и время
        current_time = datetime.now().strftime("%d:%m:%Y %H:%M:%S")

        # Форматируем запись
        record = f"{current_time}\t\t{total_time}с\n"

        # Записываем в файл
        with open("stat.txt", "a", encoding="utf-8") as file:
            file.write(record)


    def stop_camera_video(self):
        """Останавливает видео с камеры."""
        if self.cap.isOpened():
            self.cap.release()
        self.cameraLabel.hide()
        self.videoTimer.stop()

    def stop_main_video(self):
        """Останавливает основное видео."""
        if self.loopedVideoCap.isOpened():
            self.loopedVideoCap.release()
        self.loopedVideoLabel.hide()
        self.loopedVideoTimer.stop()

    def play_dark_souls_video(self):
        """Воспроизводит видео darksouls.mp4 и возвращает в LobbyWindow."""
        self.darkSoulsCap = cv2.VideoCapture("darksouls.mp4")
        self.darkSoulsTimer = QTimer(self)
        self.darkSoulsLabel = QLabel(self)
        self.darkSoulsLabel.setGeometry(0, 0, self.width(), self.height())
        self.darkSoulsLabel.show()

        def update_dark_souls_frame():
            ret, frame = self.darkSoulsCap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytesPerLine = ch * w
                qt_image = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
                self.darkSoulsLabel.setPixmap(QPixmap.fromImage(qt_image))
            else:
                # Останавливаем воспроизведение после завершения видео
                self.darkSoulsTimer.stop()
                self.darkSoulsCap.release()
                self.darkSoulsLabel.hide()
                self.return_to_lobby()

        self.darkSoulsTimer.timeout.connect(update_dark_souls_frame)
        self.darkSoulsTimer.start(30)

    def return_to_lobby(self):
        """Возвращает в LobbyWindow."""
        main_window = self.parent()  # Предполагается, что BlinkWindow — центральный виджет MainWindow
        if main_window:
            main_window.startLobbyWindow()

    def startBlinking(self):
        self.timer.start(100)


    def closeEvent(self, event):
        if self.cap:
            self.videoTimer.stop()
            self.cap.release()
        event.accept()
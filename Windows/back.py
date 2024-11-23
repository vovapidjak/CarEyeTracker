from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt

class DarkOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.opacity = 0  # Изначальная прозрачность

        # Настройка окна
        self.setGeometry(0, 0, 1920, 1080)  # Замените на разрешение вашего экрана
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_opacity(self, opacity):
        """Устанавливает уровень прозрачности."""
        self.opacity = int(opacity * 255)  # Преобразуем в значение от 0 до 255
        self.update()  # Обновляем отрисовку

    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor(0, 0, 0, self.opacity)  # Черный цвет с уровнем прозрачности
        painter.fillRect(self.rect(), color)

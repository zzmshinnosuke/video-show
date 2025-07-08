import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class VideoPlayerApp(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("手机视频播放模拟器")
        self.setGeometry(100, 100, 400, 600)
        self.video_path = video_path
        self.init_ui()
        self.init_video()
        self.start_video_timer()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 视频播放区域
        self.video_label = QLabel("加载视频中...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        main_layout.addWidget(self.video_label)

        # 输入区域
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入文字...")
        self.input_box.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_box)

        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        # 聊天记录区域
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.chat_box.setStyleSheet("background-color: #f0f0f0;")
        main_layout.addWidget(self.chat_box)

        self.setLayout(main_layout)

    def init_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            self.video_label.setText("无法打开视频文件！")
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30  # 默认 30 FPS
        self.timer_interval = int(1000 / self.fps)

    def start_video_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(self.timer_interval)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 循环播放
            return

        # OpenCV BGR 转 RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 调整图像尺寸以适应 QLabel
        height, width = frame.shape[:2]
        pixmap = self.convert_frame_to_pixmap(frame, width, height)
        self.video_label.setPixmap(pixmap)

    def convert_frame_to_pixmap(self, frame, width, height):
        image = QImage(frame.data, width, height, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(image).scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio
        )

    def send_message(self):
        message = self.input_box.text().strip()
        if not message:
            return

        self.input_box.clear()
        self.display_message("我", message)
        response = self.generate_response(message)
        self.display_message("AI", response)

    def display_message(self, sender, message):
        self.chat_box.append(f"{sender}: {message}")
        self.chat_box.verticalScrollBar().setValue(self.chat_box.verticalScrollBar().maximum())

    def generate_response(self, message):
        responses = {
            "你好": "你好！有什么可以帮助你吗？",
            "谢谢": "不客气！",
            "再见": "再见！欢迎再次使用"
        }
        return responses.get(message, f"收到你的消息：{message}")

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayerApp("video/2_720p.mkv")  # 替换为你的视频路径
    window.show()
    sys.exit(app.exec())
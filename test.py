import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QSlider, QLabel,
    QFileDialog, QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QTime


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 视频播放器")
        self.setGeometry(200, 200, 800, 600)

        # 初始化媒体播放器
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # 视频显示组件
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # 打开文件按钮
        self.open_btn = QPushButton("打开视频")
        self.open_btn.clicked.connect(self.open_file)

        # 播放按钮
        self.play_btn = QPushButton("播放")
        self.play_btn.clicked.connect(self.toggle_play)

        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")

        # 播放进度条
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # 布局
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.open_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.time_label)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addLayout(control_layout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # 信号连接
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)

    def open_file(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(self, "选择视频文件", "", "Video Files (*.mp4 *.avi *.mkv)")
        if filename:
            self.media_player.setSource(QUrl.fromLocalFile(filename))
            self.play_btn.setText("播放")
            self.media_player.pause()

    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_btn.setText("播放")
        else:
            self.media_player.play()
            self.play_btn.setText("暂停")

    def update_position(self, position):
        self.slider.setValue(position)
        self.update_time_label(position, self.media_player.duration())

    def update_duration(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def update_time_label(self, current_ms, total_ms):
        def format_time(ms):
            seconds = ms // 1000
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            if h > 0:
                return f"{h:02}:{m:02}:{s:02}"
            else:
                return f"{m:02}:{s:02}"

        current_str = format_time(current_ms)
        total_str = format_time(total_ms)
        self.time_label.setText(f"{current_str} / {total_str}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())

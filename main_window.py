"""
视频分析可视化工具主程序
"""
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QMenuBar, QStatusBar, QFileDialog, 
                             QMessageBox, QSplitter, QToolBar, QLabel)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from pathlib import Path

from video_player import VideoPlayer
from chat_panel import ChatPanel

class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.gt_annotations = []
        self.predictions = []
        self.video_duration = 0.0
        
        self.init_ui()
        self.create_toolbar()
        self.create_status_bar()
        
        # 键盘快捷键
        self.setup_shortcuts()
        
    def init_ui(self):
        """
        初始化用户界面
        """
        self.setWindowTitle("AI观赛")
        self.setGeometry(100, 100, 700, 900)
        self.setStyleSheet("background-color: #f0f2f5;")
        
        # 创建中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局 - 水平分割器
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(3, 3, 3, 3)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(0)
        main_layout.addWidget(splitter)
        
        self.video_player = VideoPlayer()
        splitter.addWidget(self.video_player)
        
        # 右侧 - 侧边栏 (25%宽度)
        self.chat_panel = ChatPanel()
        splitter.addWidget(self.chat_panel)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 2)  # 视频区域占75%
        splitter.setStretchFactor(1, 2)  # 侧边栏占25%
    
    def create_toolbar(self):
        """
        创建工具栏
        """
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 添加常用操作按钮
        toolbar.addAction("打开视频", self.open_video)
        toolbar.addAction("加载数据", self.load_gt_data)
        toolbar.addAction("播放/暂停", self.video_player.toggle_play)
    
    def create_status_bar(self):
        """
        创建状态栏
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 添加视频信息标签
        self.video_info_label = QLabel("")
        self.status_bar.addPermanentWidget(self.video_info_label)
    
    def setup_shortcuts(self):
        """
        设置键盘快捷键
        """
        # 播放/暂停
        self.video_player.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def open_video(self):
        """
        打开视频文件
        """
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(
            self,
            "打开视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv);;所有文件 (*)"
        )
        
        if video_path:
            if self.video_player.load_video(video_path):
                self.status_label.setText(f"已加载视频: {Path(video_path).name}")
            else:
                QMessageBox.critical(self, "错误", "无法加载视频文件")
    
    def load_gt_data(self):
        """
        加载GT标注数据
        """
        file_dialog = QFileDialog()
        data_path, _ = file_dialog.getOpenFileName(
            self,
            "加载GT标注数据",
            "",
            "数据文件 (*.json *.csv);;所有文件 (*)"
        )
    
    def on_duration_changed(self, duration: float):
        """
        视频时长改变事件
        """
        self.video_duration = duration
    
    def seek_to_time(self, time: float):
        """
        跳转到指定时间
        """
        self.video_player.seek_to_time(time)
    
    def seek_forward(self):
        """
        快进5秒
        """
        current_time = self.video_player.get_current_time()
        new_time = min(current_time + 5.0, self.video_player.get_duration())
        self.video_player.seek_to_time(new_time)
    
    def seek_backward(self):
        """
        快退5秒
        """
        current_time = self.video_player.get_current_time()
        new_time = max(current_time - 5.0, 0.0)
        self.video_player.seek_to_time(new_time)
    
    def keyPressEvent(self, event):
        """
        键盘事件处理
        """
        key = event.key()
        
        if key == Qt.Key.Key_Space:
            self.video_player.toggle_play()
        elif key == Qt.Key.Key_Left:
            self.seek_backward()
        elif key == Qt.Key.Key_Right:
            self.seek_forward()
        elif key == Qt.Key.Key_Comma:
            # 后退帧
            self.video_player.step_backward()
        elif key == Qt.Key.Key_Period:
            # 前进帧
            self.video_player.step_forward()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        # 确保视频播放器正确关闭
        if hasattr(self.video_player, 'video_capture') and self.video_player.video_capture:
            self.video_player.video_capture.release()
        event.accept()

def main():
    """
    主函数
    """
    app = QApplication(sys.argv)
    app.setApplicationName("AI观赛")
    app.setApplicationVersion("1.0")
    
    # 设置应用样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #e1e1e1;
            border: 1px solid #999999;
            border-radius: 3px;
            padding: 5px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #d1d1d1;
        }
        QPushButton:pressed {
            background-color: #c1c1c1;
        }
    """)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
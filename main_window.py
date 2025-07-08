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
from data_loader import DataLoader
import utils

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
        self.create_menus()
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
        
    def create_menus(self):
        """
        创建菜单栏
        """
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 打开视频
        open_video_action = QAction('打开视频(&V)', self)
        open_video_action.setShortcut(QKeySequence.StandardKey.Open)
        open_video_action.setStatusTip('打开视频文件')
        open_video_action.triggered.connect(self.open_video)
        file_menu.addAction(open_video_action)
        
        # 加载GT数据
        load_gt_action = QAction('加载GT数据(&G)', self)
        load_gt_action.setStatusTip('加载Ground Truth标注数据')
        load_gt_action.triggered.connect(self.load_gt_data)
        file_menu.addAction(load_gt_action)
        
        # 加载预测数据
        load_pred_action = QAction('加载预测数据(&P)', self)
        load_pred_action.setStatusTip('加载模型预测结果数据')
        load_pred_action.triggered.connect(self.load_prediction_data)
        file_menu.addAction(load_pred_action)
        
        file_menu.addSeparator()
        
        # 创建示例数据
        create_sample_action = QAction('创建示例数据(&S)', self)
        create_sample_action.setStatusTip('创建示例数据用于测试')
        create_sample_action.triggered.connect(self.create_sample_data)
        file_menu.addAction(create_sample_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip('退出应用程序')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 播放菜单
        play_menu = menubar.addMenu('播放(&P)')
        
        # 播放/暂停
        play_pause_action = QAction('播放/暂停(&P)', self)
        play_pause_action.setShortcut(Qt.Key.Key_Space)
        play_pause_action.setStatusTip('播放或暂停视频')
        play_pause_action.triggered.connect(self.video_player.toggle_play)
        play_menu.addAction(play_pause_action)
        
        # 停止
        stop_action = QAction('停止(&S)', self)
        stop_action.setShortcut('Ctrl+S')
        stop_action.setStatusTip('停止播放')
        stop_action.triggered.connect(self.video_player.stop)
        play_menu.addAction(stop_action)
        
        play_menu.addSeparator()
        
        # 快进/快退
        forward_action = QAction('快进(&F)', self)
        forward_action.setShortcut(Qt.Key.Key_Right)
        forward_action.setStatusTip('快进5秒')
        forward_action.triggered.connect(self.seek_forward)
        play_menu.addAction(forward_action)
        
        backward_action = QAction('快退(&B)', self)
        backward_action.setShortcut(Qt.Key.Key_Left)
        backward_action.setStatusTip('快退5秒')
        backward_action.triggered.connect(self.seek_backward)
        play_menu.addAction(backward_action)
        
        play_menu.addSeparator()
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QAction('关于(&A)', self)
        about_action.setStatusTip('关于此应用程序')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """
        创建工具栏
        """
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 添加常用操作按钮
        toolbar.addAction("打开视频", self.open_video)
        toolbar.addAction("加载GT", self.load_gt_data)
        toolbar.addAction("加载预测", self.load_prediction_data)
        toolbar.addSeparator()
        toolbar.addAction("播放/暂停", self.video_player.toggle_play)
        toolbar.addAction("停止", self.video_player.stop)
    
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
        
        
    
    def load_prediction_data(self):
        """
        加载预测结果数据
        """
        file_dialog = QFileDialog()
        data_path, _ = file_dialog.getOpenFileName(
            self,
            "加载预测结果数据",
            "",
            "数据文件 (*.json *.csv);;所有文件 (*)"
        )
        
        # if data_path:
        #     try:
        #         self.predictions = DataLoader.load_prediction_results(data_path)
        #         self.status_label.setText(f"已加载预测数据: {len(self.predictions)} 个窗口")
        #         self.update_side_panel_data()
        #     except Exception as e:
        #         QMessageBox.critical(self, "错误", f"加载预测数据失败: {str(e)}")
    
    def create_sample_data(self):
        """
        创建示例数据
        """
        try:
            DataLoader.create_sample_data()
            QMessageBox.information(self, "成功", "示例数据已创建！\n请加载 sample_gt.json 和 sample_predictions.json")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建示例数据失败: {str(e)}")
    
    def update_side_panel_data(self):
        """
        更新侧边栏数据
        """
        # if self.gt_annotations or self.predictions:
        #     self.side_panel.set_data(self.gt_annotations, self.predictions, self.video_duration)
        pass
    
    def on_position_changed(self, time: float):
        """
        播放位置改变事件
        """
        # 更新侧边栏当前时间
        # self.side_panel.update_current_time(time)
        pass
    
    def on_duration_changed(self, duration: float):
        """
        视频时长改变事件
        """
        self.video_duration = duration
        # self.update_side_panel_data()
    
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
    
    def show_about(self):
        """
        显示关于对话框
        """
        about_text = """
        <h3>视频分析可视化工具</h3>
        <p>版本: 1.0</p>
        <p>此工具用于可视化视频分析中的Ground Truth和模型预测结果对比。</p>
        <p>支持滑动窗口推理结果的实时显示。</p>
        <p><b>功能特点:</b></p>
        <ul>
        <li>视频播放和控制（支持逐帧控制）</li>
        <li>实时显示GT vs Top-5预测对比</li>
        <li>可交互的时间轴</li>
        <li>类别过滤</li>
        <li>键盘快捷键支持</li>
        <li>精确的帧级别控制</li>
        </ul>
        """
        QMessageBox.about(self, "关于", about_text)
    
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
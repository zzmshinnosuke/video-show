import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QFrame, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QFont, QFontMetrics
from PyQt6.QtCore import Qt, QTimer


class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool = True, animate: bool = False):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # 头像
        avatar = QLabel()
        avatar.setPixmap(QPixmap("icons/user.png" if is_user else "icons/bot.png").scaled(30, 30))
        avatar.setFixedSize(30, 30)
        avatar.setStyleSheet("border-radius: 20px;")

        # 气泡文本
        self.bubble = QLabel("" if animate else text)
        self.bubble.setFont(QFont("Arial", 11))
        self.bubble.setWordWrap(True)
        self.bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.bubble.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # 宽度计算
        fm = QFontMetrics(self.bubble.font())
        text_width = fm.horizontalAdvance(text)
        if is_user:
            bubble_width = min(400, text_width + 35)
        else :
            bubble_width = 400
        self.bubble.setFixedWidth(bubble_width)

        self.bubble.setStyleSheet(
            f"""
            background-color: {"#d1e7dd" if is_user else "#ffffff"};
            padding: 10px 10px;
            border-radius: 15px;
            color: #333333;
            border: none;
            """
        )

        if is_user:
            self.layout.addStretch()
            self.layout.addWidget(self.bubble)
            self.layout.addWidget(avatar)
        else:
            self.layout.addWidget(avatar)
            self.layout.addWidget(self.bubble)
            self.layout.addStretch()

        self.setLayout(self.layout)
        self.setStyleSheet("background-color: transparent;")

        # 动态输出逻辑
        if animate:
            self.full_text = text
            self.current_index = 0
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_text_slowly)
            self.timer.start(100)  # 每 30ms 输出一个字

    def update_text_slowly(self):
        if self.current_index < len(self.full_text):
            self.current_index += 1
            self.bubble.setText(self.full_text[:self.current_index])
        else:
            self.timer.stop()


class ChatPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 聊天 · 打字机效果")
        self.setGeometry(0, 0, 600, 800)
        self.setStyleSheet("background-color: #f0f2f5;")
        self.chat_history = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(5)

        self.scroll_area.setWidget(self.chat_container)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
            }
        """)
        layout.addWidget(self.scroll_area)

        # 输入栏
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入内容...")
        self.input_field.setMinimumHeight(36)
        self.input_field.setFont(QFont("Arial", 11))
        self.input_field.setStyleSheet("""
            background-color: white;
            padding: 8px 12px;
            border-radius: 18px;
            border: 1px solid #ccc;
        """)
        self.input_field.returnPressed.connect(self.send_message)

        send_btn = QPushButton("发送")
        send_btn.setMinimumHeight(36)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

    def send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        self.input_field.clear()
        self.add_message(user_text, is_user=True)

        reply = self.generate_response(user_text)
        self.chat_history.append((user_text, reply))
        self.add_message(reply, is_user=False, animate=True)

        QTimer.singleShot(500, self.scroll_to_bottom)

    def add_message(self, text, is_user=True, animate=False):
        bubble = ChatBubble(text, is_user, animate)
        self.chat_layout.addWidget(bubble)

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def generate_response(self, user_input: str) -> str:
        # 模拟 ChatGPT 回复
        res = ""
        if "太可惜了" in user_input:
            res = "是的，这个关键球确实很可惜。王曼昱的击球下网，让孙颖莎拿到了赛点。比赛进入到了最后的紧张时刻，孙颖莎现在有机会结束比赛。"
        elif "诱惑力" in user_input:    
            res = "确实如此，世乒赛奖杯象征着乒乓球运动的最高荣誉，每个选手都渴望能够捧起它。"
        elif "不容易" in user_input:    
            res = "是的，这场比赛确实非常激烈，莎莎在苦战7局后终于夺冠，展现了她的顽强斗志和高超技艺。观众们也为她的胜利欢呼雀跃。"
        elif "中国第一个" in user_input:    
            res = "中国第一个世乒赛女单冠军是邱钟惠，她在1961年获得这一荣誉。"
        else :
            res = user_input
        return res
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                             QLabel, QFrame, QListWidget, QListWidgetItem, 
                             QDialog, QFormLayout)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt, QTimer, QDateTime

class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化设置界面"""
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QFormLayout(self)
        
        # API密钥输入
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("API密钥:", self.api_key_input)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")
        
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow(button_layout)

class ChatGUI(QMainWindow):
    """
    Chat 主窗口类 - 参照Savvy风格设计
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_styles()
        
        # 在所有UI元素创建完成后，添加第一个聊天
        self.add_new_chat()
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题
        self.setWindowTitle("Savvy")
        
        # 默认窗口充满屏幕
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建左侧导航栏和右侧聊天区域
        self.create_sidebar()
        self.create_chat_area()
        
        # 将侧边栏和聊天区域添加到主布局
        main_layout.addWidget(self.sidebar_frame, 0)
        main_layout.addWidget(self.chat_container, 1)
        
        # 显示窗口
        self.show()
    
    def create_sidebar(self):
        """创建左侧导航栏"""
        # 创建侧边栏框架
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setMinimumWidth(250)
        self.sidebar_frame.setMaximumWidth(300)
        self.sidebar_frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        # 侧边栏布局
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(5)
        
        # 新聊天按钮
        self.new_chat_button = QPushButton("+ 新聊天")
        self.new_chat_button.setMinimumHeight(40)
        self.new_chat_button.clicked.connect(self.add_new_chat)
        
        # 聊天列表
        self.chat_list = QListWidget()
        self.chat_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.chat_list.itemClicked.connect(self.switch_chat)
        
        # 底部按钮区域
        bottom_layout = QHBoxLayout()
        
        # 设置按钮（纯图标，无按钮样式）
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(30, 30)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 5px;
            }
        """)
        self.settings_button.clicked.connect(self.show_settings_panel)
        self.settings_button.setToolTip("设置")
        
        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addStretch(1)
        
        # 添加到布局
        sidebar_layout.addWidget(self.new_chat_button)
        sidebar_layout.addWidget(self.chat_list, 1)
        sidebar_layout.addLayout(bottom_layout)
        
        # 初始化聊天数据，但暂时不添加聊天项
        self.chats = []  # 存储聊天历史
        self.current_chat_index = 0
    
    def create_chat_area(self):
        """创建右侧聊天区域"""
        # 创建聊天容器
        self.chat_container = QFrame()
        self.chat_container.setFrameShape(QFrame.Shape.StyledPanel)
        
        # 聊天区域布局
        chat_layout = QVBoxLayout(self.chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # 顶部标题栏
        top_bar = QFrame()
        top_bar.setMinimumHeight(60)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 10, 20, 10)
        
        # 标题标签
        self.chat_title_label = QLabel("在时刻准备着。")
        self.chat_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.chat_title_label.font()
        font.setPointSize(16)
        self.chat_title_label.setFont(font)
        
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(self.chat_title_label)
        top_bar_layout.addStretch(1)
        
        # 聊天历史区域
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setFrameShape(QFrame.Shape.NoFrame)
        
        # 底部输入区域
        input_area = QFrame()
        input_area.setMinimumHeight(80)
        input_area.setMaximumHeight(200)
        input_layout = QVBoxLayout(input_area)
        input_layout.setContentsMargins(20, 10, 20, 20)
        
        # 创建输入框
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("询问任何问题")
        self.input_box.setMinimumHeight(40)
        self.input_box.setMaximumHeight(100)
        self.input_box.returnPressed.connect(self.send_message)
        
        # 添加到布局
        input_layout.addWidget(self.input_box)
        
        # 版权信息
        footer_label = QLabel("Wen - 免费版")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #666666; font-size: 12px;")
        
        # 添加到聊天布局
        chat_layout.addWidget(top_bar)
        chat_layout.addWidget(self.chat_history, 1)
        chat_layout.addWidget(input_area)
        chat_layout.addWidget(footer_label)
    
    def setup_styles(self):
        """设置应用程序样式 - 浅色主题"""
        # 设置全局字体
        font = QFont("Microsoft YaHei", 14)
        QApplication.setFont(font)
        
        # 设置样式表
        self.setStyleSheet("""
            /* 侧边栏样式 */
            QFrame#sidebar_frame {
                background-color: #F7F7F7;
                border-right: 1px solid #E0E0E0;
            }
            
            /* 新聊天按钮 */
            QPushButton {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            
            /* 设置按钮已通过内联样式设置 */
            
            /* 聊天列表 */
            QListWidget {
                background-color: #F7F7F7;
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #EEEEEE;
                height: 40px;
            }
            QListWidget::item:selected {
                background-color: #E6F7FF;
                color: #1890FF;
            }
            
            /* 聊天区域 */
            QFrame#chat_container {
                background-color: #FFFFFF;
            }
            
            /* 聊天历史 */
            QTextEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: none;
                font-size: 16px;
                line-height: 1.6;
                padding: 20px;
            }
            
            /* 输入框 */
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #D9D9D9;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #1890FF;
                outline: none;
            }
        """)
    
    def add_new_chat(self):
        """添加新的聊天"""
        # 创建聊天项
        chat_title = "新聊天"
        chat_item = QListWidgetItem(chat_title)
        chat_item.setToolTip("点击切换到此聊天")
        
        # 添加到聊天列表
        self.chat_list.addItem(chat_item)
        self.chats.append({"title": chat_title, "messages": []})
        
        # 选中新添加的聊天
        self.chat_list.setCurrentItem(chat_item)
        self.current_chat_index = self.chat_list.count() - 1
        
        # 清空聊天历史
        self.chat_history.clear()
        
        # 添加欢迎信息
        self.append_welcome_message()
    
    def switch_chat(self, item):
        """切换聊天"""
        index = self.chat_list.row(item)
        if index >= 0 and index < len(self.chats):
            self.current_chat_index = index
            chat_data = self.chats[index]
            
            # 更新标题
            self.chat_title_label.setText(chat_data["title"])
            
            # 更新聊天历史
            self.chat_history.clear()
            for message in chat_data["messages"]:
                self.append_message(message["sender"], message["content"], message["timestamp"])
    
    def append_welcome_message(self):
        """添加欢迎消息"""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        welcome_text = "您好！我是您的AI助手，有什么可以帮助您的吗？"
        
        # 添加到聊天历史
        self.append_message("ai", welcome_text, timestamp)
        
        # 保存到当前聊天数据
        self.chats[self.current_chat_index]["messages"].append({
            "sender": "ai",
            "content": welcome_text,
            "timestamp": timestamp
        })
    
    def append_message(self, sender, content, timestamp):
        """向聊天历史添加消息"""
        if sender == "user":
            # 用户消息 - 右对齐
            message_html = f"""
                <div style="text-align: right; margin: 15px 0;">
                    <div style="display: inline-block; background-color: #E6F7FF; padding: 12px 16px; border-radius: 12px; max-width: 70%;">
                        <div style="color: #333333; font-size: 16px; line-height: 1.6;">
                            {content}
                        </div>
                        <div style="color: #999999; font-size: 12px; margin-top: 5px;">
                            {timestamp}
                        </div>
                    </div>
                </div>
            """
        else:
            # AI消息 - 左对齐
            message_html = f"""
                <div style="text-align: left; margin: 15px 0;">
                    <div style="display: inline-block; background-color: #F5F5F5; padding: 12px 16px; border-radius: 12px; max-width: 70%;">
                        <div style="color: #333333; font-size: 16px; line-height: 1.6;">
                            {content}
                        </div>
                        <div style="color: #999999; font-size: 12px; margin-top: 5px;">
                            {timestamp}
                        </div>
                    </div>
                </div>
            """
        
        self.chat_history.append(message_html)
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
    
    def send_message(self):
        """发送消息"""
        message = self.input_box.text().strip()
        if not message:
            return
        
        # 获取时间戳
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        # 添加用户消息
        self.append_message("user", message, timestamp)
        
        # 保存到当前聊天数据
        self.chats[self.current_chat_index]["messages"].append({
            "sender": "user",
            "content": message,
            "timestamp": timestamp
        })
        
        # 清空输入框
        self.input_box.clear()
        
        # 模拟AI回复
        QTimer.singleShot(1000, lambda: self.generate_ai_response(message))
    
    def show_settings_panel(self):
        """显示设置面板"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def generate_ai_response(self, user_message):
        """生成AI回复"""
        # 显示正在输入的提示
        self.chat_history.append("<div style='color: #999; font-style: italic;'>AI正在思考...</div>")
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
        
        # 确保输入框在处理API响应时不可用
        self.input_box.setEnabled(False)
        
        # 处理API调用
        try:
            # 模拟AI回复
            responses = {
                "你好": "你好！有什么我可以帮你的吗？",
                "你是谁": "我是基于PySide6构建的聊天应用，可以与您进行对话。",
                "再见": "再见！期待下次与您交流。",
                "帮助": "您可以问我任何问题，我会尽力回答。例如：'你好'、'你是谁'等。"
            }
            
            # 获取时间戳
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            # 选择回复
            ai_response = responses.get(user_message, "我理解您的问题，但我还在学习中。您可以尝试问一些其他问题。")
            
            # 移除正在思考的提示
            cursor = self.chat_history.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            
            # 添加AI回复
            self.append_message("ai", ai_response, timestamp)
            
            # 保存到当前聊天数据
            self.chats[self.current_chat_index]["messages"].append({
                "sender": "ai",
                "content": ai_response,
                "timestamp": timestamp
            })
            
        except Exception as e:
            # 显示错误消息
            error_msg = f"回复生成失败: {str(e)}"
            self.chat_history.append(f"<div style='color: red;'>{error_msg}</div>")
            print(f"回复生成异常: {str(e)}")
        finally:
            # 恢复输入框可用状态
            self.input_box.setEnabled(True)
            # 滚动到底部
            self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
    
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, '退出确认', '确定要退出Savvy吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """主函数"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("Savvy")
    app.setApplicationVersion("1.0")
    
    # 创建并显示主窗口
    window = ChatGUI()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
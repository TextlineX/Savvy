#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Agent GUI - 使用PySide6实现的AI助手界面，参照ChatGPT风格
"""

import sys
import os
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSplitter, QFrame,
    QScrollArea, QMessageBox, QListWidget, QListWidgetItem, QInputDialog,
    QMenu
)
from api_manager import DeepSeekAPIManager
from PySide6.QtGui import (
    QFont, QColor, QPalette, QIcon, QTextCursor, QTextDocument,
    QBrush, QKeySequence
)
from PySide6.QtCore import (
    Qt, QSize, QTimer, QDateTime, QSettings, QEvent, Signal, QObject
)


class AIAgentGUI(QMainWindow):
    """
    AI Agent 主窗口类 - 参照ChatGPT风格设计
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_settings()
        self.setup_styles()
        
        # 初始化API管理器
        self.api_manager = None
        self.initialize_api_manager()
        
        # 在所有UI元素创建完成后，添加第一个聊天
        self.add_new_chat()
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        self.setWindowTitle("ChatGPT")
        self.setGeometry(100, 100, 1200, 800)
        
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
        self.sidebar_frame.setFrameShape(QFrame.StyledPanel)
        
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
        self.chat_list.setSelectionMode(QListWidget.SingleSelection)
        self.chat_list.itemClicked.connect(self.switch_chat)
        
        # API设置按钮
        self.api_settings_button = QPushButton("⚙️ API设置")
        self.api_settings_button.setMinimumHeight(30)
        self.api_settings_button.clicked.connect(self.show_api_settings)
        
        # 添加到布局
        sidebar_layout.addWidget(self.new_chat_button)
        sidebar_layout.addWidget(self.chat_list, 1)
        sidebar_layout.addWidget(self.api_settings_button)
        
        # 初始化聊天数据，但暂时不添加聊天项
        self.chats = []  # 存储聊天历史
        self.current_chat_index = 0
    
    def create_chat_area(self):
        """创建右侧聊天区域"""
        # 创建聊天容器
        self.chat_container = QFrame()
        self.chat_container.setFrameShape(QFrame.StyledPanel)
        
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
        self.chat_title_label.setAlignment(Qt.AlignCenter)
        font = self.chat_title_label.font()
        font.setPointSize(16)
        self.chat_title_label.setFont(font)
        
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(self.chat_title_label)
        top_bar_layout.addStretch(1)
        
        # 聊天历史区域
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setFrameShape(QFrame.NoFrame)
        
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
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #666666; font-size: 12px;")
        
        # 添加到聊天布局
        chat_layout.addWidget(top_bar)
        chat_layout.addWidget(self.chat_history, 1)
        chat_layout.addWidget(input_area)
        chat_layout.addWidget(footer_label)
    
    def setup_settings(self):
        """设置应用程序配置"""
        # 初始化设置
        self.settings = QSettings("AIAgent", "ChatGPTClone")
        # 默认系统提示
        self.system_prompt = """你是一个AI助手，具有PowerShell命令执行能力。请遵循以下规则：

1. 当用户询问与电脑操作、文件管理、系统信息、网络配置等相关的问题时，请判断是否需要生成PowerShell命令
2. 如果需要生成PowerShell命令，请按照以下格式回复：

[POWERSHELL_COMMAND]
# 这里是PowerShell命令
Get-Process
[END_COMMAND]

3. 在命令前后提供必要的解释和说明
4. 确保生成的命令安全可靠，避免执行危险操作
5. 对于简单的查询，直接回答即可，不需要生成命令

请根据用户的问题内容判断是否需要生成PowerShell命令。"""
        
    def setup_styles(self):
        """设置应用程序样式 - 浅色主题"""
        # 设置全局字体
        font = QFont("Microsoft YaHei", 14)
        QApplication.setFont(font)
        
        # 设置浅色主题
        light_palette = QPalette()
        
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
    
    def initialize_api_manager(self):
        """初始化API管理器"""
        # 尝试从设置中获取API密钥
        api_key = self.settings.value("api_key", "sk-1eb5c511d3a74b648ca30059781fff31")
        try:
            self.api_manager = DeepSeekAPIManager(api_key=api_key)
        except Exception as e:
            QMessageBox.warning(self, "API初始化失败", f"无法初始化API管理器: {str(e)}")
            self.api_manager = None
    
    def show_api_settings(self):
        """显示API设置对话框"""
        current_key = self.settings.value("api_key", "sk-1eb5c511d3a74b648ca30059781fff31")
        
        # 获取新的API密钥
        new_key, ok = QInputDialog.getText(
            self, "API设置", "请输入DeepSeek API密钥:",
            echo=QLineEdit.PasswordEchoOnEdit, text=current_key
        )
        
        if ok and new_key:
            # 保存新的API密钥
            self.settings.setValue("api_key", new_key)
            
            # 重新初始化API管理器
            self.initialize_api_manager()
            
            # 测试连接
            try:
                test_messages = self.api_manager.format_messages(
                    self.system_prompt,
                    ["Hello, testing connection"]
                )
                test_response = self.api_manager.generate_response(test_messages)
                if test_response:
                    QMessageBox.information(self, "API设置成功", "API密钥设置成功，连接测试通过！")
            except Exception as e:
                QMessageBox.warning(self, "API连接测试失败", f"无法连接到DeepSeek API: {str(e)}")
    
    def extract_powershell_command(self, text: str):
        """从文本中提取PowerShell命令"""
        import re
        pattern = r'\[POWERSHELL_COMMAND\](.*?)\[END_COMMAND\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            command = match.group(1).strip()
            # 清理命令中的注释行
            lines = command.split('\n')
            cleaned_lines = []
            for line in lines:
                if not line.strip().startswith('#'):
                    cleaned_lines.append(line.strip())
            return '\n'.join(cleaned_lines)
        return None

    def execute_and_display_powershell(self, command: str):
        """实时执行PowerShell命令并在界面上显示输出"""
        if not self.api_manager:
            self.show_error("API管理器未初始化")
            return

        # 显示执行状态和命令内容
        self.chat_history.append(f"<div style='color: orange;'>🔧 正在执行PowerShell命令...</div>")
        self.chat_history.append(f"<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;'>"
                               f"<strong>命令:</strong> {command}</div>")
        
        # 创建停止按钮
        stop_button_id = f"stop_powershell_{id(self)}"
        self.chat_history.append(f"<div id='powershell_output' style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto;'>"
                               f"<button id='{stop_button_id}' style='background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;'>停止执行</button>"
                               f"<br><span style='color: #6c757d;'>实时输出:</span><br>")
        
        # 滚动到底部
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
        
        # 处理GUI事件，确保界面更新
        QApplication.processEvents()
        
        # 实时执行命令
        output_content = ""
        is_running = True
        
        try:
            for result_chunk in self.api_manager.execute_powershell_command_realtime(command):
                if result_chunk["type"] == "stdout":
                    output_content += result_chunk["line"] + "\n"
                    # 更新实时输出
                    self.update_powershell_output(output_content, stop_button_id, is_running)
                elif result_chunk["type"] == "stderr":
                    output_content += f"<span style='color: red;'>错误: {result_chunk['line']}</span>\n"
                    self.update_powershell_output(output_content, stop_button_id, is_running)
                elif result_chunk["type"] in ["result", "error"]:
                    is_running = False
                    if result_chunk.get("success"):
                        self.chat_history.append(f"<div style='color: green;'>✅ 命令执行完成</div>")
                    else:
                        error_msg = result_chunk.get("error", "未知错误")
                        self.chat_history.append(f"<div style='color: red;'>❌ 命令执行失败: {error_msg}</div>")
                    break
                
                # 处理GUI事件，确保界面更新
                QApplication.processEvents()
                
        except Exception as e:
            self.chat_history.append(f"<div style='color: red;'>❌ 执行过程中发生错误: {str(e)}</div>")
        
        # 滚动到底部
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
    
    def update_powershell_output(self, output_content: str, stop_button_id: str, is_running: bool):
        """更新PowerShell实时输出显示"""
        # 构建完整的输出HTML
        button_html = f"<button id='{stop_button_id}' style='background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;' {'disabled' if not is_running else ''}>停止执行</button>"
        
        output_html = f"<div id='powershell_output' style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto;'>"
        output_html += f"{button_html}<br><span style='color: #6c757d;'>实时输出:</span><br>{output_content}</div>"
        
        # 更新显示
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        
        # 查找并替换输出区域
        current_text = self.chat_history.toPlainText()
        if "powershell_output" in current_text:
            # 使用简单的文本替换方法
            html_content = self.chat_history.toHtml()
            import re
            pattern = r"<div id='powershell_output'[^>]*>.*?</div>"
            new_html = re.sub(pattern, output_html, html_content, flags=re.DOTALL)
            self.chat_history.setHtml(new_html)
        
        # 滚动到底部
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
        
        # 处理GUI事件
        QApplication.processEvents()

    def generate_ai_response(self, user_message):
        """使用DeepSeek API生成AI回复"""
        # 显示正在输入的提示
        self.chat_history.append("<div style='color: #999; font-style: italic;'>AI正在思考...</div>")
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
        
        # 确保输入框在处理API响应时不可用
        self.input_box.setEnabled(False)
        
        # 处理API调用
        try:
            # 准备消息列表
            user_messages = []
            assistant_messages = []
            
            # 从当前聊天历史中提取消息
            for msg in self.chats[self.current_chat_index]["messages"]:
                if msg["sender"] == "user":
                    user_messages.append(msg["content"])
                elif msg["sender"] == "ai":
                    assistant_messages.append(msg["content"])
            
            # 格式化消息 - 注意：当前用户消息将在format_messages方法中单独处理
            messages = self.api_manager.format_messages(
                self.system_prompt,
                user_messages,
                assistant_messages,
                user_message  # 单独传递当前用户消息
            )
            
            # 使用流式响应获取AI回复
            full_response = ""
            
            # 移除正在思考的提示
            cursor = self.chat_history.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            
            # 开始添加AI回复的容器
            self.chat_history.insertHtml("<div id='ai-response'>")
            
            # 流式获取响应
            for chunk in self.api_manager.generate_streaming_response(messages):
                full_response += chunk
                
                # 更新聊天历史显示 - 使用更简单的方法
                self.chat_history.clear()
                self.chat_history.insertHtml(f"<div id='ai-response'>{full_response}</div>")
                
                # 滚动到底部
                self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
                
                # 处理GUI事件，确保界面更新
                QApplication.processEvents()
            
            # 完成AI回复的容器
            self.chat_history.insertHtml("</div>")
            
            # 获取时间戳
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            # 保存到当前聊天数据
            self.chats[self.current_chat_index]["messages"].append({
                "sender": "ai",
                "content": full_response,
                "timestamp": timestamp
            })
            
            # 检测并执行PowerShell命令
            powershell_command = self.extract_powershell_command(full_response)
            if powershell_command:
                self.execute_and_display_powershell(powershell_command)
            
        except Exception as e:
            # 显示错误消息
            error_msg = f"API调用失败: {str(e)}"
            self.chat_history.append(f"<div style='color: red;'>{error_msg}</div>")
            print(f"API调用异常: {str(e)}")
        finally:
            # 恢复输入框可用状态
            self.input_box.setEnabled(True)
            # 滚动到底部
            self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())
    
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        reply = QMessageBox.question(
            self, '退出确认', '确定要退出ChatGPT吗？',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """主函数"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("ChatGPT")
    app.setApplicationVersion("1.0")
    
    # 创建并显示主窗口
    window = AIAgentGUI()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
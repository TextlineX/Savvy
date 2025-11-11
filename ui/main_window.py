#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QVBoxLayout, QHBoxLayout, QMessageBox)
from PySide6.QtCore import QSettings, Qt, QDateTime
from PySide6.QtGui import QFont

# 延迟导入，避免循环导入
import importlib

from ui.settings_dialog import SettingsDialog
from ui.chat_components import ChatComponents
from ui.api_manager_wrapper import APIManagerWrapper


class AIAgentGUI(QMainWindow):
    """
    AI Agent 主窗口类 - 参照Savvy风格设计
    """
    
    def __init__(self):
        super().__init__()
        # 初始化组件
        self.chat_components = ChatComponents(self)
        self.api_wrapper = APIManagerWrapper(self)
        
        self.init_ui()
        self.setup_settings()
        self.setup_styles()
        
        # 初始化API管理器
        self.api_wrapper.initialize_api_manager()
        
        # 在所有UI元素创建完成后，显示欢迎界面
        self.show_welcome_screen()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题
        self.setWindowTitle("Savvy")
        
        # 设置窗口大小并居中显示
        self.resize(1000, 600)
        self.center_window()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建左侧导航栏和右侧聊天区域
        sidebar = self.chat_components.create_sidebar()
        chat_area = self.chat_components.create_chat_area()
        
        # 将侧边栏和聊天区域添加到主布局
        main_layout.addWidget(sidebar, 0)
        main_layout.addWidget(chat_area, 1)
        
        # 显示窗口
        self.show()
    
    def center_window(self):
        """将窗口居中显示"""
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def setup_settings(self):
        """设置应用程序配置"""
        # 初始化设置
        self.settings = QSettings("AIAgent", "Savvy")
    
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
                border: 1px solid #D9D9D9;
                outline: none;
            }
        """)
    
    def show_welcome_screen(self):
        """显示欢迎界面"""
        welcome_html = """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
            <h2>欢迎使用 Savvy</h2>
            <p style="color: #666; margin-bottom: 20px;">点击左侧 "+ 新聊天" 按钮开始对话</p>
        </div>
        """
        self.chat_components.chat_history.setHtml(welcome_html)
    
    def add_new_chat(self):
        """添加新的聊天"""
        self.chat_components.show_new_chat_input()
    
    def handle_new_chat_title(self):
        """处理新聊天标题输入"""
        title = self.chat_components.new_chat_input.text()
        if not title or not title.strip():
            title = "新聊天"
        else:
            title = title.strip()
        
        # 创建新的聊天会话
        self.chat_components.create_new_chat(title)
    
    def switch_chat(self, item):
        """切换聊天"""
        self.chat_components.switch_chat(item)
    
    def send_message(self):
        """发送消息"""
        message = self.chat_components.input_box.text().strip()
        if not message:
            return
        
        # 发送消息到聊天组件
        if self.chat_components.send_message(message):
            # 清空输入框
            self.chat_components.input_box.clear()
            # 生成AI回复
            self.api_wrapper.generate_ai_response(message)
    
    def show_settings_panel(self):
        """显示设置面板"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 重新初始化API管理器
            self.api_wrapper.initialize_api_manager()
    
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        reply = QMessageBox.question(
            self, '退出确认', '确定要退出Savvy吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
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
    window = AIAgentGUI()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
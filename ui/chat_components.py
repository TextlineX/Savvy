#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
聊天组件模块 - 包含聊天相关的UI组件和功能
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QTextEdit, QLineEdit, QPushButton, 
                               QLabel, QFrame, QListWidget, QListWidgetItem, 
                               QVBoxLayout, QHBoxLayout)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QTextCursor


class ChatComponents:
    """
    聊天组件类 - 管理聊天界面的创建和交互
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.chats = []
        self.current_chat_index = 0
    
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
        self.new_chat_button.clicked.connect(self.parent.add_new_chat)
        
        # 聊天列表
        self.chat_list = QListWidget()
        self.chat_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.chat_list.itemClicked.connect(self.parent.switch_chat)
        
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
        self.settings_button.clicked.connect(self.parent.show_settings_panel)
        self.settings_button.setToolTip("设置")
        
        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addStretch(1)
        
        # 添加到布局
        sidebar_layout.addWidget(self.new_chat_button)
        sidebar_layout.addWidget(self.chat_list, 1)
        sidebar_layout.addLayout(bottom_layout)
        
        return self.sidebar_frame
    
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
        
        # 创建一个堆叠布局用于切换聊天历史和新建聊天输入框
        self.chat_stack = QWidget()
        self.chat_stack_layout = QVBoxLayout(self.chat_stack)
        self.chat_stack_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_stack_layout.addWidget(self.chat_history)
        
        # 底部输入区域
        self.input_area = QFrame()
        self.input_area.setMinimumHeight(80)
        self.input_area.setMaximumHeight(200)
        input_layout = QVBoxLayout(self.input_area)
        input_layout.setContentsMargins(20, 10, 20, 20)
        
        # 创建输入框
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("询问任何问题")
        self.input_box.setMinimumHeight(40)
        self.input_box.setMaximumHeight(100)
        self.input_box.returnPressed.connect(self.parent.send_message)
        
        # 添加到布局
        input_layout.addWidget(self.input_box)
        
        # 版权信息
        footer_label = QLabel("Savvy - 内测版")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #666666; font-size: 12px;")
        
        # 添加到聊天布局
        chat_layout.addWidget(top_bar)
        chat_layout.addWidget(self.chat_stack, 1)
        chat_layout.addWidget(self.input_area)
        chat_layout.addWidget(footer_label)
        
        return self.chat_container
    
    def show_new_chat_input(self):
        """在聊天区域显示新建聊天输入框"""
        # 更新标题
        self.chat_title_label.setText("创建新聊天")
        
        # 隐藏底部输入区域
        self.input_area.setVisible(False)
        
        # 创建居中布局的输入框
        self.new_chat_widget = QWidget()
        layout = QVBoxLayout(self.new_chat_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加提示标签
        prompt_label = QLabel("您今天在想什么？")
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt_label.setStyleSheet("""
            color: #000000;
            font-size: 24px;
            font-weight: normal;
            margin-bottom: 20px;
        """)
        layout.addWidget(prompt_label)
        
        # 创建输入框
        self.new_chat_input = QLineEdit()
        self.new_chat_input.setPlaceholderText("请输入新聊天标题")
        self.new_chat_input.setMinimumHeight(50)
        self.new_chat_input.setMaximumWidth(400)
        self.new_chat_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.new_chat_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 12px 20px;
                border: 2px solid #D9D9D9;
                border-radius: 25px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #D9D9D9;
                outline: none;
            }
        """)
        self.new_chat_input.returnPressed.connect(self.parent.handle_new_chat_title)
        
        # 添加到布局
        layout.addWidget(self.new_chat_input)
        
        # 清空聊天历史区域并添加新的输入框
        # 先移除所有子控件
        for i in reversed(range(self.chat_stack_layout.count())): 
            self.chat_stack_layout.itemAt(i).widget().setParent(None)
        
        # 添加新的输入控件
        self.chat_stack_layout.addWidget(self.new_chat_widget)
        
        # 聚焦到输入框
        self.new_chat_input.setFocus()
    
    def create_new_chat(self, title):
        """创建新的聊天会话"""
        if not title or not title.strip():
            title = "新聊天"
        else:
            title = title.strip()
            
        # 创建聊天项
        chat_item = QListWidgetItem(title)
        chat_item.setToolTip("点击切换到此聊天")
        
        # 添加到聊天列表
        self.chat_list.addItem(chat_item)
        self.chats.append({"title": title, "messages": []})
        
        # 选中新添加的聊天
        self.chat_list.setCurrentItem(chat_item)
        self.current_chat_index = self.chat_list.count() - 1
        
        # 更新标题
        self.chat_title_label.setText(title)
        
        # 恢复聊天历史显示
        for i in reversed(range(self.chat_stack_layout.count())): 
            self.chat_stack_layout.itemAt(i).widget().setParent(None)
        self.chat_stack_layout.addWidget(self.chat_history)
        
        # 清空聊天历史
        self.chat_history.clear()
        self.chat_history.setStyleSheet("")
        
        # 显示底部输入区域
        self.input_area.setVisible(True)
        
        # 添加欢迎信息
        self.append_welcome_message()
    
    def switch_chat(self, item):
        """切换聊天"""
        # 确保显示的是聊天历史而不是输入框
        has_chat_history = False
        for i in range(self.chat_stack_layout.count()):
            if self.chat_stack_layout.itemAt(i).widget() == self.chat_history:
                has_chat_history = True
                break
        
        if not has_chat_history:
            # 恢复聊天历史显示
            for i in reversed(range(self.chat_stack_layout.count())): 
                self.chat_stack_layout.itemAt(i).widget().setParent(None)
            self.chat_stack_layout.addWidget(self.chat_history)
        
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
    
    def send_message(self, message):
        """发送消息"""
        if not message:
            return
        
        # 确保有有效的聊天会话
        if not self.chats:
            # 如果没有聊天会话，先创建一个默认的
            self.create_new_chat("默认聊天")
        
        # 获取时间戳
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        # 添加用户消息
        self.append_message("user", message, timestamp)
        
        # 保存到当前聊天数据
        if self.current_chat_index < len(self.chats):
            self.chats[self.current_chat_index]["messages"].append({
                "sender": "user",
                "content": message,
                "timestamp": timestamp
            })
        else:
            # 如果索引无效，添加到第一个聊天（如果存在）
            if self.chats:
                self.chats[0]["messages"].append({
                    "sender": "user",
                    "content": message,
                    "timestamp": timestamp
                })
        
        return True
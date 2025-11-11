#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API管理器包装模块 - 封装AI API调用功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor


class APIManagerWrapper:
    """
    API管理器包装类 - 处理与AI API的交互
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.api_manager = None
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
    
    def initialize_api_manager(self):
        """初始化API管理器"""
        try:
            # 延迟导入API管理器，避免循环导入
            from api_manager import DeepSeekAPIManager
            
            # 尝试初始化API管理器
            self.api_manager = DeepSeekAPIManager()
            return True
        except Exception as e:
            print(f"初始化API管理器失败: {e}")
            self.api_manager = None
            return False
    
    def generate_ai_response(self, user_message):
        """使用DeepSeek API生成AI回复"""
        # 显示正在输入的提示
        self.parent.chat_components.chat_history.append("<div style='color: #999; font-style: italic;'>AI正在思考...</div>")
        self.parent.chat_components.chat_history.verticalScrollBar().setValue(
            self.parent.chat_components.chat_history.verticalScrollBar().maximum())
        
        # 确保输入框在处理API响应时不可用
        self.parent.chat_components.input_box.setEnabled(False)
        
        # 处理API调用
        try:
            if not self.api_manager:
                raise Exception("API管理器未初始化")
                
            # 准备消息列表
            user_messages = []
            assistant_messages = []
            
            # 从当前聊天历史中提取消息
            for msg in self.parent.chat_components.chats[self.parent.chat_components.current_chat_index]["messages"]:
                if msg["sender"] == "user":
                    user_messages.append(msg["content"])
                elif msg["sender"] == "ai":
                    assistant_messages.append(msg["content"])
            
            # 格式化消息
            messages = self.api_manager.format_messages(
                self.system_prompt,
                user_messages,
                assistant_messages,
                user_message
            )
            
            # 使用流式响应获取AI回复
            full_response = ""
            
            # 移除正在思考的提示
            cursor = self.parent.chat_components.chat_history.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            
            # 开始添加AI回复的容器
            self.parent.chat_components.chat_history.insertHtml("<div id='ai-response'>")
            
            # 流式获取响应
            for chunk in self.api_manager.generate_streaming_response(messages):
                full_response += chunk
                
                # 更新聊天历史显示
                self.parent.chat_components.chat_history.clear()
                self.parent.chat_components.chat_history.insertHtml(f"<div id='ai-response'>{full_response}</div>")
                
                # 滚动到底部
                self.parent.chat_components.chat_history.verticalScrollBar().setValue(
                    self.parent.chat_components.chat_history.verticalScrollBar().maximum())
                
                # 处理GUI事件，确保界面更新
                QApplication.processEvents()
            
            # 完成AI回复的容器
            self.parent.chat_components.chat_history.insertHtml("</div>")
            
            # 获取时间戳
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            # 保存到当前聊天数据
            self.parent.chat_components.chats[self.parent.chat_components.current_chat_index]["messages"].append({
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
            self.parent.chat_components.chat_history.append(f"<div style='color: red;'>{error_msg}</div>")
            print(f"API调用异常: {str(e)}")
        finally:
            # 恢复输入框可用状态
            self.parent.chat_components.input_box.setEnabled(True)
            # 滚动到底部
            self.parent.chat_components.chat_history.verticalScrollBar().setValue(
                self.parent.chat_components.chat_history.verticalScrollBar().maximum())
    
    def extract_powershell_command(self, text: str):
        """从文本中提取PowerShell命令"""
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
            self.parent.chat_components.chat_history.append("<div style='color: red;'>❌ API管理器未初始化</div>")
            return
            
        # 显示正在执行的提示
        self.parent.chat_components.chat_history.append("<div style='color: #1890FF; font-weight: bold;'>正在执行PowerShell命令...</div>")
        
        # 滚动到底部
        self.parent.chat_components.chat_history.verticalScrollBar().setValue(
            self.parent.chat_components.chat_history.verticalScrollBar().maximum())
        
        # 执行命令并显示输出
        for result in self.api_manager.execute_powershell_command_realtime(command):
            if result["type"] == "stdout":
                output_line = result["line"]
                self.parent.chat_components.chat_history.append(f"<div style='color: #333;'>{output_line}</div>")
            elif result["type"] == "stderr":
                error_line = result["line"]
                self.parent.chat_components.chat_history.append(f"<div style='color: red;'>{error_line}</div>")
            elif result["type"] == "result":
                if result["success"]:
                    self.parent.chat_components.chat_history.append("<div style='color: green;'>✅ 命令执行完成</div>")
                else:
                    if result.get("is_timeout"):
                        self.parent.chat_components.chat_history.append("<div style='color: orange;'>⏰ 命令执行超时</div>")
                    else:
                        self.parent.chat_components.chat_history.append(f"<div style='color: red;'>❌ 命令执行失败 (退出码: {result['returncode']})</div>")
                        if result.get("error"):
                            self.parent.chat_components.chat_history.append(f"<div style='color: red;'>错误信息: {result['error']}</div>")
            elif result["type"] == "error":
                self.parent.chat_components.chat_history.append(f"<div style='color: red;'>❌ 执行错误: {result['error']}</div>")
            
            # 滚动到底部
            self.parent.chat_components.chat_history.verticalScrollBar().setValue(
                self.parent.chat_components.chat_history.verticalScrollBar().maximum())
            
            # 处理GUI事件，确保界面更新
            QApplication.processEvents()
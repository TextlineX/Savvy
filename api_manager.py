#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API管理器 - 封装DeepSeek API调用功能
"""

import os
import time
import sys
from typing import List, Dict, Optional, Any
from openai import OpenAI
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DeepSeekAPIManager:
    """
    DeepSeek API管理器，封装所有与DeepSeek API相关的操作
    """
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.deepseek.com/v1"):
        """
        初始化API管理器
        
        Args:
            api_key: DeepSeek API密钥，如果为None则尝试从环境变量获取
            base_url: DeepSeek API基础URL
        """
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未提供，请在设置中配置API密钥或设置环境变量DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """
        初始化OpenAI客户端
        """
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未提供，请设置环境变量DEEPSEEK_API_KEY或直接传入")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_response(self, messages: List[Dict[str, str]], 
                          model: str = "deepseek-chat", 
                          stream: bool = False, 
                          temperature: float = 0.7,
                          max_tokens: int = 2048) -> Optional[str]:
        """
        生成AI回复
        
        Args:
            messages: 消息列表，每个消息包含role和content
            model: 使用的模型名称
            stream: 是否流式响应
            temperature: 生成温度，控制随机性
            max_tokens: 最大生成token数
            
        Returns:
            AI生成的回复内容
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"API调用错误: {str(e)}")
            return None
    
    def generate_streaming_response(self, messages: List[Dict[str, str]],
                                  model: str = "deepseek-chat",
                                  temperature: float = 0.7,
                                  max_tokens: int = 2048):
        """
        生成流式AI回复
        
        Args:
            messages: 消息列表
            model: 使用的模型名称
            temperature: 生成温度
            max_tokens: 最大生成token数
            
        Yields:
            每个生成的文本片段
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            print(f"流式API调用错误: {str(e)}")
            yield f"\n\nAPI调用失败: {str(e)}"
    
    def format_messages(self, system_prompt: str, user_messages: List[str], 
                       assistant_messages: List[str] = None, 
                       current_user_message: str = None) -> List[Dict[str, str]]:
        """
        格式化消息列表
        
        Args:
            system_prompt: 系统提示
            user_messages: 用户消息列表（历史消息）
            assistant_messages: 助手回复列表（历史消息）
            current_user_message: 当前用户消息（可选）
            
        Returns:
            格式化后的消息列表
        """
        messages = []
        
        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史用户和助手消息对
        if assistant_messages and len(assistant_messages) != len(user_messages):
            # 如果历史消息数量不匹配，只使用匹配的部分
            min_length = min(len(user_messages), len(assistant_messages))
            user_messages = user_messages[:min_length]
            assistant_messages = assistant_messages[:min_length]
        
        for i, user_msg in enumerate(user_messages):
            messages.append({"role": "user", "content": user_msg})
            if assistant_messages and i < len(assistant_messages):
                messages.append({"role": "assistant", "content": assistant_messages[i]})
        
        # 添加当前用户消息（如果有）
        if current_user_message:
            messages.append({"role": "user", "content": current_user_message})
        
        return messages
    
    def execute_powershell_command_realtime(self, command: str, timeout: int = 300):
        """
        实时执行PowerShell命令并显示输出
        
        Args:
            command: PowerShell命令
            timeout: 超时时间（秒），默认5分钟
            
        Yields:
            执行结果字典
        """
        try:
            # 使用Popen启动进程，实时获取输出
            process = subprocess.Popen(
                ["powershell", "-Command", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )

            # 实时读取输出
            output_lines = []
            error_lines = []
            
            # 设置超时
            start_time = time.time()
            
            while process.poll() is None:
                # 检查是否超时
                if time.time() - start_time > timeout:
                    process.kill()
                    yield {
                        "type": "error",
                        "success": False,
                        "error": f"命令执行超时（{timeout}秒）",
                        "is_timeout": True
                    }
                    return
                
                # 读取标准输出
                stdout_line = process.stdout.readline()
                if stdout_line:
                    output_lines.append(stdout_line.strip())
                    yield {"type": "stdout", "line": stdout_line.strip()}
                
                # 读取标准错误
                stderr_line = process.stderr.readline()
                if stderr_line:
                    error_lines.append(stderr_line.strip())
                    yield {"type": "stderr", "line": stderr_line.strip()}
                
                time.sleep(0.1)  # 避免CPU占用过高
            
            # 读取剩余输出
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                for line in remaining_stdout.strip().split('\n'):
                    if line:
                        output_lines.append(line)
                        yield {"type": "stdout", "line": line}
                        
            if remaining_stderr:
                for line in remaining_stderr.strip().split('\n'):
                    if line:
                        error_lines.append(line)
                        yield {"type": "stderr", "line": line}
            
            # 返回最终结果
            yield {
                "type": "result",
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "output": "\n".join(output_lines),
                "error": "\n".join(error_lines)
            }

        except Exception as e:
            yield {
                "type": "error",
                "success": False,
                "error": f"执行命令时发生错误: {str(e)}"
            }


# 示例用法
if __name__ == "__main__":
    # 测试API调用
    try:
        api_manager = DeepSeekAPIManager()
        
        # 测试基本调用
        messages = api_manager.format_messages(
            system_prompt="You are a helpful assistant",
            user_messages=["Hello, who are you?"]
        )
        
        print("测试基本API调用:")
        response = api_manager.generate_response(messages)
        print(f"回复: {response}")
        
        # 测试流式调用
        print("\n测试流式API调用:")
        full_response = ""
        for chunk in api_manager.generate_streaming_response(messages):
            full_response += chunk
            print(chunk, end="", flush=True)
            time.sleep(0.01)  # 模拟延迟以更好地观察流式输出
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
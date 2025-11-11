#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置管理器 - 负责处理应用程序的设置配置
"""

import os
import json
from typing import Any, Dict, Optional


class SettingsManager:
    """
    设置管理器类，用于管理应用程序的设置文件
    """
    
    def __init__(self, settings_dir: str = "settings"):
        """
        初始化设置管理器
        
        Args:
            settings_dir: 设置文件夹名称
        """
        # 获取项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.settings_dir = os.path.join(self.project_root, settings_dir)
        self.modules_dir = os.path.join(self.settings_dir, "modules")
        
        # 主设置文件
        self.settings_file = os.path.join(self.settings_dir, "settings.json")
        
        # 确保目录存在
        os.makedirs(self.settings_dir, exist_ok=True)
        os.makedirs(self.modules_dir, exist_ok=True)
        
        # 加载主设置
        self.settings = self.load_main_settings()
        
        # 加载各模块设置
        self.modules = {}
        self.load_modules_settings()
    
    def load_main_settings(self) -> Dict[str, Any]:
        """
        加载主设置文件
        
        Returns:
            主设置字典
        """
        if not os.path.exists(self.settings_file):
            # 创建默认主设置
            default_settings = {
                "version": "1.0",
                "modules": [
                    "basic",
                    "theme",
                    "api",
                    "security",
                    "network"
                ],
                "active_module": "basic"
            }
            self.save_main_settings(default_settings)
            return default_settings
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_main_settings(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存主设置到文件
        
        Args:
            settings: 要保存的设置，如果为None则保存当前设置
            
        Returns:
            保存是否成功
        """
        settings_to_save = settings if settings is not None else self.settings
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存主设置文件失败: {e}")
            return False
    
    def load_modules_settings(self):
        """
        加载所有模块的设置
        """
        for module_name in self.settings.get("modules", []):
            module_file = os.path.join(self.modules_dir, f"{module_name}.json")
            if os.path.exists(module_file):
                try:
                    with open(module_file, 'r', encoding='utf-8') as f:
                        self.modules[module_name] = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    self.modules[module_name] = {}
            else:
                # 如果模块文件不存在，创建默认配置
                self.modules[module_name] = self.get_default_module_config(module_name)
                self.save_module_settings(module_name, self.modules[module_name])
    
    def get_default_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        获取模块的默认配置
        
        Args:
            module_name: 模块名称
            
        Returns:
            默认配置字典
        """
        default_configs = {
            "basic": {
                "auto_start": False,
                "minimize_to_tray": False,
                "language": "简体中文"
            },
            "theme": {
                "theme_mode": "浅色主题",
                "font_size": 14
            },
            "api": {
                "api_key": "",
                "api_url": "",
                "timeout": 30
            },
            "security": {
                "encrypt_data": False,
                "encrypt_cache": False,
                "password_protect": False,
                "lock_timeout": 5
            },
            "network": {
                "use_proxy": False,
                "proxy_host": "",
                "proxy_port": 8080,
                "proxy_protocol": "HTTP"
            }
        }
        
        return default_configs.get(module_name, {})
    
    def save_module_settings(self, module_name: str, config: Dict[str, Any]) -> bool:
        """
        保存模块设置到文件
        
        Args:
            module_name: 模块名称
            config: 配置字典
            
        Returns:
            保存是否成功
        """
        module_file = os.path.join(self.modules_dir, f"{module_name}.json")
        
        try:
            with open(module_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存模块 {module_name} 的设置文件失败: {e}")
            return False
    
    def get(self, module_name: str, key: str, default: Any = None) -> Any:
        """
        获取模块配置项的值
        
        Args:
            module_name: 模块名称
            key: 配置项键名
            default: 默认值
            
        Returns:
            配置项的值
        """
        if module_name in self.modules and key in self.modules[module_name]:
            return self.modules[module_name][key]
        return default
    
    def set(self, module_name: str, key: str, value: Any) -> bool:
        """
        设置模块配置项的值
        
        Args:
            module_name: 模块名称
            key: 配置项键名
            value: 要设置的值
            
        Returns:
            设置是否成功
        """
        if module_name not in self.modules:
            self.modules[module_name] = {}
        
        self.modules[module_name][key] = value
        return self.save_module_settings(module_name, self.modules[module_name])
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        获取整个模块的配置
        
        Args:
            module_name: 模块名称
            
        Returns:
            模块配置字典
        """
        return self.modules.get(module_name, {})
    
    def save_module_config(self, module_name: str, config: Dict[str, Any]) -> bool:
        """
        保存整个模块的配置
        
        Args:
            module_name: 模块名称
            config: 配置字典
            
        Returns:
            保存是否成功
        """
        self.modules[module_name] = config
        return self.save_module_settings(module_name, config)


# 全局设置管理器实例
settings_manager = SettingsManager()
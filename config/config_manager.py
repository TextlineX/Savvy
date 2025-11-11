#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器 - 负责处理应用程序的所有配置
"""

import os
import json
from typing import Any, Dict, Optional


class ConfigManager:
    """
    配置管理器类，用于管理应用程序的配置文件
    """
    
    def __init__(self, config_dir: str = "config", config_file: str = "settings.json"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件夹名称
            config_file: 配置文件名
        """
        # 获取项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = os.path.join(self.project_root, config_dir)
        self.config_file = os.path.join(self.config_dir, config_file)
        
        # 创建配置目录（如果不存在）
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 默认配置
        self.default_config = {
            "api": {
                "api_key": "",
                "api_url": "",
                "timeout": 30
            },
            "basic": {
                "auto_start": False,
                "minimize_to_tray": False,
                "language": "简体中文"
            },
            "theme": {
                "theme_mode": "浅色主题",
                "font_size": 14
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
        
        # 加载配置
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Returns:
            配置字典
        """
        # 如果配置文件不存在，创建默认配置文件
        if not os.path.exists(self.config_file):
            self.save_config(self.default_config)
            return self.default_config.copy()
        
        # 读取配置文件
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 确保所有默认键都存在
                return self._merge_config(config, self.default_config)
        except (json.JSONDecodeError, FileNotFoundError):
            # 如果读取失败，返回默认配置
            return self.default_config.copy()
    
    def _merge_config(self, current_config: Dict, default_config: Dict) -> Dict:
        """
        合并当前配置和默认配置，确保所有必需的键都存在
        
        Args:
            current_config: 当前配置
            default_config: 默认配置
            
        Returns:
            合并后的配置
        """
        merged = default_config.copy()
        
        for key, value in current_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_config(value, merged[key])
            else:
                merged[key] = value
                
        return merged
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置，如果为None则保存当前配置
            
        Returns:
            保存是否成功
        """
        config_to_save = config if config is not None else self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置项的值
        
        Args:
            key_path: 配置项路径，使用点号分隔，如 "api.api_key"
            default: 默认值
            
        Returns:
            配置项的值
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        设置配置项的值
        
        Args:
            key_path: 配置项路径，使用点号分隔，如 "api.api_key"
            value: 要设置的值
            
        Returns:
            设置是否成功
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        try:
            # 导航到倒数第二层
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # 设置最后一层的值
            config_ref[keys[-1]] = value
            return True
        except Exception as e:
            print(f"设置配置项失败: {e}")
            return False
    
    def save(self) -> bool:
        """
        保存当前配置
        
        Returns:
            保存是否成功
        """
        return self.save_config(self.config)


# 全局配置管理器实例
config_manager = ConfigManager()
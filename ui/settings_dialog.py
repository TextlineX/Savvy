#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置对话框模块
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLineEdit, QPushButton,
                               QVBoxLayout, QWidget, QListWidget, QStackedWidget,
                               QLabel, QFormLayout, QCheckBox, QGroupBox, 
                               QComboBox, QSpinBox)
from PySide6.QtCore import Qt

# 导入配置管理器
from config import config_manager


class SettingsDialog(QDialog):
    """
    设置对话框类，支持多个设置模块
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化设置界面"""
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(600, 400)
        
        # 主布局
        main_layout = QHBoxLayout(self)
        
        # 左侧导航栏
        self.nav_list = QListWidget()
        self.nav_list.setMaximumWidth(150)
        self.nav_list.addItems(["基础设置", "主题设置", "API设置", "安全设置", "网络设置"])
        self.nav_list.currentRowChanged.connect(self.switch_panel)
        
        # 右侧内容区域
        self.content_stack = QStackedWidget()
        
        # 创建各个设置面板
        self.basic_panel = self.create_basic_panel()
        self.theme_panel = self.create_theme_panel()
        self.api_panel = self.create_api_panel()
        self.security_panel = self.create_security_panel()
        self.network_panel = self.create_network_panel()
        
        # 添加面板到堆叠窗口
        self.content_stack.addWidget(self.basic_panel)
        self.content_stack.addWidget(self.theme_panel)
        self.content_stack.addWidget(self.api_panel)
        self.content_stack.addWidget(self.security_panel)
        self.content_stack.addWidget(self.network_panel)
        
        # 按钮布局
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")
        
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.setAlignment(Qt.AlignRight)
        
        # 右侧布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.content_stack)
        right_layout.addWidget(buttons_widget)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        # 添加到主布局
        main_layout.addWidget(self.nav_list)
        main_layout.addWidget(right_widget)
        
        # 默认选中第一个
        self.nav_list.setCurrentRow(0)
    
    def create_basic_panel(self):
        """创建基础设置面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 启动设置
        startup_group = QGroupBox("启动设置")
        startup_layout = QVBoxLayout(startup_group)
        self.auto_start_checkbox = QCheckBox("开机自启动")
        self.minimize_tray_checkbox = QCheckBox("启动时最小化到托盘")
        startup_layout.addWidget(self.auto_start_checkbox)
        startup_layout.addWidget(self.minimize_tray_checkbox)
        
        # 语言设置
        language_group = QGroupBox("语言设置")
        language_layout = QVBoxLayout(language_group)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        language_layout.addWidget(QLabel("界面语言:"))
        language_layout.addWidget(self.language_combo)
        
        layout.addWidget(startup_group)
        layout.addWidget(language_group)
        layout.addStretch()
        
        return panel
    
    def create_theme_panel(self):
        """创建主题设置面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 主题选择
        theme_group = QGroupBox("主题选择")
        theme_layout = QVBoxLayout(theme_group)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题", "自动"])
        theme_layout.addWidget(QLabel("主题模式:"))
        theme_layout.addWidget(self.theme_combo)
        
        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QFormLayout(font_group)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(14)
        font_layout.addRow("字体大小:", self.font_size_spin)
        
        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addStretch()
        
        return panel
    
    def create_api_panel(self):
        """创建API设置面板"""
        panel = QWidget()
        layout = QFormLayout(panel)
        
        # API密钥输入
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        layout.addRow("API密钥:", self.api_key_input)
        
        # API地址
        self.api_url_input = QLineEdit()
        layout.addRow("API地址:", self.api_url_input)
        
        # 超时设置
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" 秒")
        layout.addRow("请求超时:", self.timeout_spin)
        
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("注意：修改API设置后需要重启应用才能生效"))
        
        return panel
    
    def create_security_panel(self):
        """创建安全设置面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 数据加密
        encryption_group = QGroupBox("数据加密")
        encryption_layout = QVBoxLayout(encryption_group)
        self.encrypt_data_checkbox = QCheckBox("启用本地数据加密")
        self.encrypt_cache_checkbox = QCheckBox("加密缓存文件")
        encryption_layout.addWidget(self.encrypt_data_checkbox)
        encryption_layout.addWidget(self.encrypt_cache_checkbox)
        
        # 密码保护
        password_group = QGroupBox("密码保护")
        password_layout = QVBoxLayout(password_group)
        self.password_protect_checkbox = QCheckBox("启用密码保护")
        self.lock_timeout_spin = QSpinBox()
        self.lock_timeout_spin.setRange(1, 60)
        self.lock_timeout_spin.setValue(5)
        self.lock_timeout_spin.setSuffix(" 分钟无操作后锁定")
        password_layout.addWidget(self.password_protect_checkbox)
        password_layout.addWidget(self.lock_timeout_spin)
        
        layout.addWidget(encryption_group)
        layout.addWidget(password_group)
        layout.addStretch()
        
        return panel
    
    def create_network_panel(self):
        """创建网络设置面板"""
        panel = QWidget()
        layout = QFormLayout(panel)
        
        # 代理设置
        self.proxy_checkbox = QCheckBox("使用代理")
        layout.addRow(self.proxy_checkbox)
        
        self.proxy_host_input = QLineEdit()
        layout.addRow("代理主机:", self.proxy_host_input)
        
        self.proxy_port_input = QSpinBox()
        self.proxy_port_input.setRange(1, 65535)
        self.proxy_port_input.setValue(8080)
        layout.addRow("代理端口:", self.proxy_port_input)
        
        # 网络协议
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["HTTP", "HTTPS", "SOCKS5"])
        layout.addRow("协议类型:", self.protocol_combo)
        
        return panel
    
    def switch_panel(self, index):
        """切换设置面板"""
        self.content_stack.setCurrentIndex(index)
    
    def load_settings(self):
        """加载设置"""
        # API设置
        api_key = self.config.get("api.api_key", "")
        self.api_key_input.setText(api_key)
        
        api_url = self.config.get("api.api_url", "")
        self.api_url_input.setText(api_url)
        
        timeout = self.config.get("api.timeout", 30)
        self.timeout_spin.setValue(timeout)
        
        # 基础设置
        auto_start = self.config.get("basic.auto_start", False)
        self.auto_start_checkbox.setChecked(auto_start)
        
        minimize_tray = self.config.get("basic.minimize_to_tray", False)
        self.minimize_tray_checkbox.setChecked(minimize_tray)
        
        language = self.config.get("basic.language", "简体中文")
        index = self.language_combo.findText(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        # 主题设置
        theme = self.config.get("theme.theme_mode", "浅色主题")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        font_size = self.config.get("theme.font_size", 14)
        self.font_size_spin.setValue(font_size)
        
        # 安全设置
        encrypt_data = self.config.get("security.encrypt_data", False)
        self.encrypt_data_checkbox.setChecked(encrypt_data)
        
        encrypt_cache = self.config.get("security.encrypt_cache", False)
        self.encrypt_cache_checkbox.setChecked(encrypt_cache)
        
        password_protect = self.config.get("security.password_protect", False)
        self.password_protect_checkbox.setChecked(password_protect)
        
        lock_timeout = self.config.get("security.lock_timeout", 5)
        self.lock_timeout_spin.setValue(lock_timeout)
        
        # 网络设置
        use_proxy = self.config.get("network.use_proxy", False)
        self.proxy_checkbox.setChecked(use_proxy)
        
        proxy_host = self.config.get("network.proxy_host", "")
        self.proxy_host_input.setText(proxy_host)
        
        proxy_port = self.config.get("network.proxy_port", 8080)
        self.proxy_port_input.setValue(proxy_port)
        
        protocol = self.config.get("network.proxy_protocol", "HTTP")
        index = self.protocol_combo.findText(protocol)
        if index >= 0:
            self.protocol_combo.setCurrentIndex(index)
    
    def save_settings(self):
        """保存设置"""
        # API设置
        self.config.set("api.api_key", self.api_key_input.text())
        self.config.set("api.api_url", self.api_url_input.text())
        self.config.set("api.timeout", self.timeout_spin.value())
        
        # 基础设置
        self.config.set("basic.auto_start", self.auto_start_checkbox.isChecked())
        self.config.set("basic.minimize_to_tray", self.minimize_tray_checkbox.isChecked())
        self.config.set("basic.language", self.language_combo.currentText())
        
        # 主题设置
        self.config.set("theme.theme_mode", self.theme_combo.currentText())
        self.config.set("theme.font_size", self.font_size_spin.value())
        
        # 安全设置
        self.config.set("security.encrypt_data", self.encrypt_data_checkbox.isChecked())
        self.config.set("security.encrypt_cache", self.encrypt_cache_checkbox.isChecked())
        self.config.set("security.password_protect", self.password_protect_checkbox.isChecked())
        self.config.set("security.lock_timeout", self.lock_timeout_spin.value())
        
        # 网络设置
        self.config.set("network.use_proxy", self.proxy_checkbox.isChecked())
        self.config.set("network.proxy_host", self.proxy_host_input.text())
        self.config.set("network.proxy_port", self.proxy_port_input.value())
        self.config.set("network.proxy_protocol", self.protocol_combo.currentText())
        
        # 保存配置到文件
        self.config.save()
        
        self.accept()
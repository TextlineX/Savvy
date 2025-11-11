#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数 - 启动AI Agent GUI"""
    print("正在启动AI Agent GUI...")
    
    try:
        # 导入PySide6
        from PySide6.QtWidgets import QApplication
        # 导入主窗口
        from ui.main_window import AIAgentGUI
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("Savvy")
        app.setApplicationVersion("1.0")
        
        # 创建并显示主窗口
        window = AIAgentGUI()
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"导入GUI模块失败: {e}")
        print("请确保已安装PySide6: pip install PySide6")
        sys.exit(1)
    except Exception as e:
        print(f"启动GUI时发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
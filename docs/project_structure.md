# 项目结构

## 目录结构

```
Savvy/
├── agent/                  # AI代理核心模块
│   ├── command.py          # 命令解析和执行
│   ├── executor.py         # 命令执行器
│   └── module_loader.py    # 模块加载器
├── config/                 # 配置管理模块
│   ├── __init__.py
│   └── config_manager.py   # 配置管理器
├── settings/               # 设置模块
│   ├── modules/            # 各类设置的JSON文件
│   │   ├── api.json
│   │   ├── basic.json
│   │   ├── network.json
│   │   ├── security.json
│   │   └── theme.json
│   ├── __init__.py
│   └── settings_manager.py # 设置管理器
├── templates/              # 模板文件
│   └── echo.json           # 示例模板
├── ui/                     # 用户界面模块
│   ├── main_window.py      # 主窗口
│   ├── chat_components.py  # 聊天组件
│   ├── api_manager_wrapper.py  # API管理器包装
│   └── settings_dialog.py  # 设置对话框
├── docs/                   # 文档目录
├── README.md               # 项目说明
├── api_manager.py          # API管理器
├── chat_app.py             # 聊天应用
├── main.py                 # 程序入口
└── requirements.txt        # 依赖包列表
```

## 模块说明

### agent/ - AI代理核心模块
- `command.py`: 负责解析自然语言命令并将其转换为可执行的指令
- `executor.py`: 执行各种类型的命令，包括系统命令、文件操作等
- `module_loader.py`: 动态加载和管理不同的功能模块

### config/ - 配置管理模块
- `config_manager.py`: 管理应用程序的配置文件，包括读取、写入和更新配置

### settings/ - 设置模块
- `settings_manager.py`: 管理用户界面和应用程序的各种设置
- `modules/`: 包含各类设置的JSON文件，如API设置、基础设置、网络设置等

### templates/ - 模板文件
- `echo.json`: 示例模板文件，演示如何创建和使用模板

### ui/ - 用户界面模块
- `main_window.py`: 主应用程序窗口，协调各个UI组件
- `chat_components.py`: 聊天界面相关的组件和功能
- `api_manager_wrapper.py`: 包装API管理器，处理与AI的交互
- `settings_dialog.py`: 设置对话框界面和逻辑

### 根目录文件
- `README.md`: 项目说明文档
- `api_manager.py`: 管理与AI API的通信
- `chat_app.py`: 聊天应用的主要逻辑
- `main.py`: 程序入口点
- `requirements.txt`: 项目依赖包列表
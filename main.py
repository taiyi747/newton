#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
牛顿环综合实验平台 - 桌面应用（入口文件）
使用 PyQt5 内置浏览器核心显示 HTML 界面
无边框窗口，中键拖动，边缘调整大小，双击关闭

主要逻辑已拆分到 app/ 目录：
- app.bridge_handler: BridgeHandler 类（前后端通信）
- app.main_window: NewtonRingsApp 类（主窗口）
"""

import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

# 判断是否在 cx_Freeze 打包环境中
def is_frozen():
    return getattr(sys, 'frozen', False)

# 获取应用根目录
def get_app_dir():
    if is_frozen():
        # cx_Freeze 打包后，可执行文件在根目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

# 导入桥接模块
APP_DIR = get_app_dir()
LIB_DIR = os.path.join(APP_DIR, 'lib')
if os.path.exists(LIB_DIR):
    sys.path.insert(0, LIB_DIR)
    sys.path.insert(0, APP_DIR)  # 添加 APP_DIR 以支持 app/ 导入

# 导入AI模块
try:
    from ai_module import get_ai_instance, get_streaming_handler, create_stream, remove_stream, clear_ai_history
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    print(f"警告: AI模块导入失败: {e}")

from bridge import call_api


def validate_environment():
    """验证运行环境"""
    # 设置QtWebEngine环境变量以解决图形渲染问题
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")
    os.environ.setdefault("QT_QPA_PLATFORM", "windows")


def check_dependencies():
    """检查依赖项"""
    required_modules = {
        'PyQt5': 'PyQt5',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
    }

    missing = []
    for name, import_name in required_modules.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(name)

    if missing:
        print(f"错误: 缺少以下依赖项: {', '.join(missing)}")
        print("请运行: pip install " + " ".join(missing))
        return False
    return True


# 从 app/ 导入拆分后的类
from app import bridge_handler as app_bridge_handler
from app.bridge_handler import BridgeHandler
from app import main_window as app_main_window
from app.main_window import NewtonRingsApp

# 初始化 app 模块的全局变量
app_main_window._init_globals(BridgeHandler, APP_DIR)
app_bridge_handler._init_globals(AI_AVAILABLE, LIB_DIR)


def main():
    """主函数"""
    try:
        # 生产环境：移除所有调试输出
        if not check_dependencies():
            sys.exit(1)

        validate_environment()

        # 创建Qt应用
        app = QApplication(sys.argv)

        # 设置应用程序属性
        app.setApplicationName("牛顿环综合实验平台")
        app.setApplicationVersion("1.0")

        # 创建主窗口
        window = NewtonRingsApp()
        window.show()

        # 运行应用程序
        sys.exit(app.exec_())

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
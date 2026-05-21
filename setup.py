#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cx_Freeze 打包配置 - 牛顿环综合实验平台
优化体积，仅包含必要组件
"""

import sys
import os
from cx_Freeze import setup, Executable

# 应用信息
APP_NAME = "牛顿环综合实验平台"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "牛顿环综合实验平台 - 桌面应用"

# 获取当前目录
base_dir = os.path.dirname(os.path.abspath(__file__))

# 依赖配置 - 只包含必要的包
build_exe_options = {
    # 需要包含的包
    "packages": [
        "PyQt5",
        "PyQt5.QtWebEngineWidgets",
        "PyQt5.QtWebChannel",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
        "numpy",
        "matplotlib",
        "matplotlib.backends.backend_agg",
        "openai",
        "pandas",
    ],
    
    # 需要包含的模块
    "includes": [
        "json",
        "os",
        "sys",
        "io",
        "base64",
        "threading",
        "traceback",
        "math",
        "re",
        "time",
        "random",
        "colorsys",
        "pathlib",
        "typing",
        "collections",
        "functools",
        "decimal",
        "inspect",
    ],
    
    # 排除不需要的包（减小体积）
    "excludes": [
        # 测试相关
        "pytest",
        "unittest",
        "test",
        "tests",
        "_pytest",
        
        # 开发工具
        "pdb",
        "pydoc",
        "doctest",
        "idlelib",
        "tkinter",
        "tkinter.ttk",
        "tcl",
        "Tkinter",
        
        # 文档和示例
        "sphinx",
        "docutils",
        
        # 网络/服务器（除必要的）
        "http.server",
        "socketserver",
        "wsgiref",
        
        # 其他大体积且不需要的包
        "boto3",
        "botocore",
        "jmespath",
        "s3transfer",
        # "matplotlib.pyplot",  # 仿真模块需要 pyplot
        "matplotlib.backends.backend_tkagg",
        # "matplotlib.backends.backend_qt5agg",  # 仿真模块需要 Qt5Agg
        "PyQt5.QtBluetooth",
        "PyQt5.QtDesigner",
        "PyQt5.QtHelp",
        "PyQt5.QtMultimedia",
        "PyQt5.QtMultimediaWidgets",
        # "PyQt5.QtNetwork",  # PyQtWebEngine 依赖此模块
        "PyQt5.QtNfc",
        "PyQt5.QtOpenGL",
        "PyQt5.QtPositioning",
        # "PyQt5.QtPrintSupport",  # matplotlib 需要此模块
        "PyQt5.QtQml",
        "PyQt5.QtQuick",
        "PyQt5.QtQuickWidgets",
        "PyQt5.QtSensors",
        "PyQt5.QtSerialPort",
        "PyQt5.QtSql",
        "PyQt5.QtSvg",
        "PyQt5.QtTest",
        "PyQt5.QtWinExtras",
        "PyQt5.QtXml",
        "PyQt5.QtXmlPatterns",
        "scipy",
        "sklearn",
        "pandas.plotting",
        "pandas.io.clipboard",
        "pandas.io.sql",
    ],
    
    # 包含的数据文件
    "include_files": [
        # 前端资源
        ("frontend", "frontend"),
        ("lib", "lib"),
        ("qrc", "qrc"),
        
        # Qt 配置文件
        ("qt.conf", "qt.conf"),
        
        # 翻译文件（可选，但推荐保留）
        ("translations", "translations"),
        
        # QtWebEngine 必要文件
        ("QtWebEngineProcess.exe", "QtWebEngineProcess.exe"),
    ],
    
    # 压缩选项
    "optimize": 2,
    
    # 构建目录
    "build_exe": "build/牛顿环综合实验平台",
    
    # 不复制依赖项（手动控制）
    "include_msvcr": True,
}

# 可执行文件配置
# cx_Freeze 8.x 使用 "gui" 作为 GUI 应用的 base
base = "gui" if sys.platform == "win32" else None

executables = [
    Executable(
        script="run.py",
        base=base,
        target_name="牛顿环综合实验平台",
        icon=os.path.join(base_dir, "qrc", "power_on_off_switch_exit_icon_141963.ico"),
    )
]

# 执行打包
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    options={"build_exe": build_exe_options},
    executables=executables,
)

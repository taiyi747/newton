# -*- coding: utf-8 -*-
"""
GUI 基础模块 - 包含公共导入、工具函数和配置
"""

import numpy as np
import matplotlib.colors
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 使用统一配置模块
from lib.config import init_matplotlib_fonts
init_matplotlib_fonts()

# ==================== 公共颜色映射 ====================
colors = [(0.576, 0.376, 0.114), (0.831, 0.608, 0.216)]  # 暗纹偏灰色，明纹偏橘色
sodium_cmap = matplotlib.colors.LinearSegmentedColormap.from_list('sodium_cmap', colors)

# ==================== 公共工具函数 ====================

def scale_pixmap(pixmap, width, height):
    """
    统一的图像缩放方法

    Args:
        pixmap: QtGui.QPixmap 对象
        width: 目标宽度
        height: 目标高度

    Returns:
        缩放后的 QPixmap
    """
    return pixmap.scaled(width, height,
                         QtCore.Qt.KeepAspectRatioByExpanding,
                         QtCore.Qt.SmoothTransformation)


def set_tooltip_style(widget):
    """设置工具提示样式"""
    style = """
    QToolTip {
        background-color: black;
        color: white;
        border: 1px solid white;
        padding: 2px;
        opacity: 200;
    }
    """
    widget.setStyleSheet(style)
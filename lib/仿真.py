# -*- coding: utf-8 -*-
"""
牛顿环物理仿真模块

保留物理计算功能，同时重导出 GUI 组件以保持向后兼容。
GUI 组件已拆分到 lib.gui 子包中。
"""

import numpy as np
import random
import matplotlib.colors
import sys

# 使用统一配置模块
from lib.config import init_matplotlib_fonts
init_matplotlib_fonts()


# ==================== 物理计算函数 ====================

def newtons_rings(lam=500e-9, R=1, levels=50, offset=0.0):
    """
    生成牛顿环图像数据

    Args:
        lam: 波长（米）
        R: 曲率半径（米）
        levels: 干涉环级数
        offset: 图像偏移量

    Returns:
        X, Y: 网格坐标
        B: 亮度数组
        ym: 最大坐标范围
    """
    ym = np.sqrt(levels * lam * R)
    xs = np.linspace(-ym, ym, 1001)
    ys = np.linspace(-ym, ym, 1001)
    X, Y = np.meshgrid(xs, ys)
    r = np.sqrt((X + offset) ** 2 + Y ** 2)  # 偏移应用到X方向
    I = np.cos(np.pi * (r ** 2 / R + lam / 2) / lam) ** 2
    B = (I / 4.0) * 255
    return X, Y, B, ym


# ==================== 颜色映射 ====================
colors = [(0.576, 0.376, 0.114), (0.831, 0.608, 0.216)]  # 暗纹偏灰色，明纹偏橘色
sodium_cmap = matplotlib.colors.LinearSegmentedColormap.from_list('sodium_cmap', colors)


# ==================== 全局变量 ====================
current_level = -6   # 牛顿环当前显示的级次从-6开始
lam = 500e-9         # 波长
R = random.uniform(0.8, 2)  # 曲率半径在0.8到2之间随机
max_level = 50       # 最大级次


# ==================== 向后兼容：GUI 组件重导出 ====================
# 从 lib.gui 子包导入所有窗口类，保持向后兼容
try:
    from lib.gui import (
        MainWindow,
        PowerWindow,
        LensWindow,
        DataWindow,
        ScaleWindow,
        ReflectorWindow,
        Ui_Form,
    )
except ImportError as e:
    # 如果 gui 包未正确安装，发出警告但仍允许物理计算功能使用
    print(f"警告: 无法导入 GUI 组件 ({e})，物理计算功能仍然可用")


# ==================== 主入口 ====================
if __name__ == '__main__':
    from PyQt5 import QtWidgets

    # 使用延迟导入避免循环依赖
    from lib.gui.main_window import MainWindow

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
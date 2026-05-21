# -*- coding: utf-8 -*-
"""
Matplotlib 统一绘图工具模块
消除 calculate_* 函数中的重复绘图代码
"""

import io
import base64
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


def fig_to_base64(fig):
    """将 matplotlib 图形转换为 base64 编码的 PNG 图像"""
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_base64


def create_ring_image(X, Y, B, wavelength_nm, title, get_cmap_func):
    """
    创建牛顿环模拟图像（通用函数）

    参数:
        X, Y: 网格坐标
        B: 亮度数组
        wavelength_nm: 波长（nm）
        title: 图像标题
        get_cmap_func: 获取颜色映射的函数

    返回:
        base64 编码的图像字符串
    """
    fig = Figure(figsize=(8, 8), dpi=100)
    ax = fig.add_subplot(111)
    cmap = get_cmap_func(wavelength_nm)
    ax.pcolormesh(X, Y, B, shading='gouraud', cmap=cmap)
    ax.set_axis_off()
    ax.set_title(title, fontsize=14)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    return fig_to_base64(fig)


def create_intensity_plot(r, intensity, wavelength_nm, radius_m,
                          title, xlabel="半径 r (mm)", ylabel="光强 I (相对单位)"):
    """
    创建光强分布曲线图（通用函数）

    参数:
        r: 半径数组
        intensity: 光强数组
        wavelength_nm: 波长（nm）
        radius_m: 曲率半径（m）
        title: 图表标题
        xlabel, ylabel: 轴标签

    返回:
        base64 编码的图像字符串
    """
    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)

    ax.plot(r * 1e3, intensity, 'b-', linewidth=2, label='光强分布')
    ax.axvline(x=0, color='k', linestyle='--', alpha=0.3, linewidth=1)

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 5)

    # 限制显示范围
    display_range = max(np.abs(r)) / 3
    ax.set_xlim(-display_range * 1e3, display_range * 1e3)

    return fig_to_base64(fig)


def create_fit_plot(k, D_sq, coefficients, wavelength_nm, refractive_n):
    """
    创建线性拟合结果图（用于数据处理）

    参数:
        k: 环序数数组
        D_sq: 直径平方数组 (米^2)
        coefficients: 拟合系数 [a, b]
        wavelength_nm: 波长（nm）
        refractive_n: 折射率

    返回:
        (base64编码的图像字符串, 计算得到的R值)
    """
    a, b = coefficients
    WL_m = wavelength_nm * 1e-9
    WL_n = WL_m / refractive_n
    calculated_R = a / (4 * WL_n)

    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(111)

    # 绘制散点
    ax.scatter(k, D_sq * 1e6, color='red', s=50, label='实验数据点', zorder=5)

    # 绘制拟合线
    k_fine = np.linspace(k.min(), k.max(), 100)
    D_sq_fine = a * k_fine + b
    ax.plot(k_fine, D_sq_fine * 1e6, 'b-', linewidth=2, label='拟合直线')

    # 绘制残差线
    D_sq_fit = a * k + b
    for ki, dsq, dsq_fit in zip(k, D_sq, D_sq_fit):
        ax.plot([ki, ki], [dsq * 1e6, dsq_fit * 1e6], 'r--', alpha=0.5)

    ax.set_xlabel('环序数 k', fontsize=12)
    ax.set_ylabel('直径平方 D² (10⁻⁶ m²)', fontsize=12)
    ax.set_title(f'牛顿环拟合计算R（n={refractive_n:.2f}，λ={wavelength_nm:.1f} nm）', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    # 添加结果文本
    text_str = (f'拟合结果:\n'
                f'计算得到 R = {calculated_R:.2f} m\n'
                f'波长 λ = {wavelength_nm:.1f} nm\n'
                f'折射率 n = {refractive_n:.2f}\n'
                f'斜率 a = {a:.2e} m²\n'
                f'数据点数: {len(k)}')
    ax.text(0.05, 0.95, text_str, transform=ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            fontsize=10)

    return fig_to_base64(fig), calculated_R


def create_ring_image_by_R(calculated_R, wavelength_nm, refractive_n):
    """
    根据计算出的曲率半径创建模拟牛顿环图像（用于数据处理结果展示）

    参数:
        calculated_R: 计算得到的曲率半径（米）
        wavelength_nm: 波长（nm）
        refractive_n: 折射率

    返回:
        base64 编码的图像字符串
    """
    WL_m = wavelength_nm * 1e-9

    ym = np.sqrt(50 * WL_m * calculated_R)
    xs = np.linspace(-ym, ym, 801)
    ys = np.linspace(-ym, ym, 801)
    X, Y = np.meshgrid(xs, ys)
    r = np.sqrt(X**2 + Y**2)
    d = r**2 / (2 * calculated_R)
    I = 2 * (1 - np.cos(4 * np.pi * refractive_n * d / WL_m))
    B = (I / 4.0) * 255

    # 动态导入避免循环依赖
    from lib.config import get_wavelength_cmap

    fig = Figure(figsize=(8, 8), dpi=100)
    ax = fig.add_subplot(111)
    cmap = get_wavelength_cmap(wavelength_nm)
    ax.pcolormesh(X, Y, B, shading='gouraud', cmap=cmap)
    ax.set_axis_off()
    ax.set_title(f'牛顿环模拟图像（λ={wavelength_nm:.1f} nm，R={calculated_R:.2f} m）', fontsize=14)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    return fig_to_base64(fig)
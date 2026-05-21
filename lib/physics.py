# -*- coding: utf-8 -*-
"""
牛顿环物理计算核心模块
提取通用计算逻辑，消除代码重复
"""

import numpy as np


# ==================== 通用物理计算函数 ====================

def compute_optical_path_difference(r, R, curvature_difference=0.0, h=0.0):
    """
    通用光程差计算函数

    参数:
        r: 半径数组
        R: 曲率半径
        curvature_difference: 曲率差 (1/R1 - 1/R2 或 1/R1 + 1/R2)
        h: 间隙高度（非接触式）

    返回:
        d: 光程差数组
    """
    # 基础空气膜厚度
    if curvature_difference != 0:
        d = (r**2 / 2) * curvature_difference
    else:
        d = r**2 / (2 * R)

    # 非接触式需要加上间隙 h
    if h != 0:
        d = d + h

    return d


def compute_intensity(d, lam, n=1.0):
    """
    通用光强计算

    参数:
        d: 光程差数组
        lam: 波长（米）
        n: 折射率

    返回:
        intensity: 光强数组
    """
    return 2 * (1 - np.cos(4 * np.pi * n * d / lam))


def compute_ring_radius(k, lam, R, n=1.0):
    """
    计算第k级牛顿环的半径

    参数:
        k: 环的级数
        lam: 波长（米）
        R: 曲率半径
        n: 折射率

    返回:
        环半径
    """
    return np.sqrt(k * lam * R / n)


# ==================== 物理计算与图像生成函数 ====================

def newtons_rings_1d(lam, R, n=1.0, h=0.0, curvature_diff=0.0, num_points=3000):
    """
    一维牛顿环光强分布计算

    参数:
        lam: 波长（米）
        R: 曲率半径
        n: 折射率
        h: 间隙高度（米）
        curvature_diff: 曲率差
        num_points: 采样点数

    返回:
        r, intensity, max_r
    """
    max_r = np.sqrt(50 * lam * R)
    r = np.linspace(-max_r, max_r, num_points)
    d = compute_optical_path_difference(r, R, curvature_diff, h)
    intensity = compute_intensity(d, lam, n)
    return r, intensity, max_r


def newtons_rings_2d(lam, R, n=1.0, h=0.0, curvature_diff=0.0,
                     levels=50, resolution=801):
    """
    二维牛顿环图像数据计算

    参数:
        lam: 波长（米）
        R: 曲率半径
        n: 折射率
        h: 间隙高度（米）
        curvature_diff: 曲率差
        levels: 环的级数
        resolution: 网格分辨率

    返回:
        X, Y, B, ym
    """
    ym = np.sqrt(levels * lam * R)
    xs = np.linspace(-ym, ym, resolution)
    ys = np.linspace(-ym, ym, resolution)
    X, Y = np.meshgrid(xs, ys)
    r = np.sqrt(X**2 + Y**2)
    d = compute_optical_path_difference(r, R, curvature_diff, h)
    I = compute_intensity(d, lam, n)
    B = (I / 4.0) * 255
    return X, Y, B, ym


# ==================== 兼容旧API的别名函数 ====================

def newtons_rings_noncontact(lam=589.3e-9, R=1.0, h=0.0, n=1.0):
    """非接触式普通牛顿环装置的光强分布（兼容旧API）"""
    return newtons_rings_1d(lam, R, n, h=h, curvature_diff=0.0)


def newtons_rings_truncated(lam=589.3e-9, R=1.0, h=0.0, n=1.0):
    """截顶式浅近切割牛顿环（兼容旧API）"""
    return newtons_rings_1d(lam, R, n, h=h, curvature_diff=0.0)


def newtons_rings_image(lam=500e-9, R=1.0, levels=50, h=0.0, n=1.0):
    """生成非接触式牛顿环二维图像（兼容旧API）"""
    return newtons_rings_2d(lam, R, n, h=h, curvature_diff=0.0, levels=levels)


def newtons_rings_image_truncated(lam=500e-9, R=1.0, levels=50, h=0.0, n=1.0):
    """生成截顶式牛顿环二维图像（兼容旧API）"""
    return newtons_rings_2d(lam, R, n, h=h, curvature_diff=0.0, levels=levels)


def newtons_rings_convex_concave_contact(lam=589.3e-9, R1=1.0, R2=1.0, n=1.0):
    """平凸透镜和平凹透镜牛顿环（接触式）（兼容旧API）"""
    curvature_diff = 1/R1 - 1/R2
    return newtons_rings_1d(lam, R1, n, curvature_diff=curvature_diff)


def newtons_rings_image_convex_concave_contact(lam=500e-9, R1=1.0, R2=1.0, levels=50, n=1.0):
    """生成平凸-平凹透镜二维图像（接触式）（兼容旧API）"""
    curvature_diff = 1/R1 - 1/R2
    return newtons_rings_2d(lam, R1, n, curvature_diff=curvature_diff, levels=levels)


def newtons_rings_convex_convex_contact(lam=589.3e-9, R1=1.0, R2=1.0, n=1.0):
    """平凸透镜和平凸透镜牛顿环（接触式）（兼容旧API）"""
    curvature_diff = 1/R1 + 1/R2
    return newtons_rings_1d(lam, R1, n, curvature_diff=curvature_diff)


def newtons_rings_image_convex_convex_contact(lam=500e-9, R1=1.0, R2=1.0, levels=50, n=1.0):
    """生成双平凸透镜二维图像（接触式）（兼容旧API）"""
    curvature_diff = 1/R1 + 1/R2
    return newtons_rings_2d(lam, R1, n, curvature_diff=curvature_diff, levels=levels)


def newtons_rings_convex_concave_noncontact(lam=589.3e-9, R1=1.0, R2=1.0, h=0.0, n=1.0):
    """平凸透镜和平凹透镜牛顿环（非接触式）（兼容旧API）"""
    curvature_diff = 1/R1 - 1/R2
    return newtons_rings_1d(lam, R1, n, h=h, curvature_diff=curvature_diff)


def newtons_rings_image_convex_concave_noncontact(lam=500e-9, R1=1.0, R2=1.0, levels=50, h=0.0, n=1.0):
    """生成平凸-平凹透镜二维图像（非接触式）（兼容旧API）"""
    curvature_diff = 1/R1 - 1/R2
    return newtons_rings_2d(lam, R1, n, h=h, curvature_diff=curvature_diff, levels=levels)


def newtons_rings_convex_convex_noncontact(lam=589.3e-9, R1=1.0, R2=1.0, h=0.0, n=1.0):
    """平凸透镜和平凸透镜牛顿环（非接触式）（兼容旧API）"""
    curvature_diff = 1/R1 + 1/R2
    return newtons_rings_1d(lam, R1, n, h=h, curvature_diff=curvature_diff)


def newtons_rings_image_convex_convex_noncontact(lam=500e-9, R1=1.0, R2=1.0, levels=50, h=0.0, n=1.0):
    """生成双平凸透镜二维图像（非接触式）（兼容旧API）"""
    curvature_diff = 1/R1 + 1/R2
    return newtons_rings_2d(lam, R1, n, h=h, curvature_diff=curvature_diff, levels=levels)
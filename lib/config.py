# -*- coding: utf-8 -*-
"""
统一配置模块 - 集中管理字体、缓存等公共配置
"""

import matplotlib
import matplotlib.colors
import functools

# 延迟导入 pandas，仅在需要时加载
def get_pandas_read_csv():
    """获取 pandas read_csv 函数"""
    from pandas import read_csv
    return read_csv


# ==================== 字体配置 ====================

def init_matplotlib_fonts():
    """
    初始化matplotlib中文字体（单例模式，多次调用无副作用）

    使用方式：
        from lib.config import init_matplotlib_fonts
        init_matplotlib_fonts()
    """
    matplotlib.rcParams['font.sans-serif'] = [
        'SimHei', 'Microsoft YaHei', 'PingFang SC', 'WenQuanYi Micro Hei'
    ]
    matplotlib.rcParams['axes.unicode_minus'] = False


# 模块导入时自动初始化
init_matplotlib_fonts()


# ==================== 缓存管理器 ====================

class CalculationCache:
    """物理计算结果缓存管理器"""

    def __init__(self, maxsize=128):
        self._cache = {}
        self._maxsize = maxsize

    def get(self, key):
        """获取缓存值"""
        return self._cache.get(key)

    def set(self, key, value):
        """设置缓存值"""
        if len(self._cache) >= self._maxsize:
            # 简单策略：清除第一个元素
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        self._cache[key] = value

    def clear(self):
        """清空所有缓存"""
        self._cache.clear()

    def size(self):
        """返回当前缓存大小"""
        return len(self._cache)


# 全局缓存实例
calculation_cache = CalculationCache(maxsize=128)

# 计算缓存（用于颜色映射等）
_calculation_cache = {}


def cached_calculation(cache_key_func):
    """计算结果缓存装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = cache_key_func(*args, **kwargs)
            cached = calculation_cache.get(key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            calculation_cache.set(key, result)
            return result
        return wrapper
    return decorator


# ==================== 颜色映射 ====================

def get_wavelength_cmap(wavelength_nm):
    """根据波长获取颜色映射"""
    cache_key = f"cmap_{wavelength_nm}"
    if cache_key in _calculation_cache:
        return _calculation_cache[cache_key]

    if 400 <= wavelength_nm < 450:
        color1, color2 = (0.5, 0.0, 0.8), (0.8, 0.2, 1.0)
    elif 450 <= wavelength_nm < 495:
        color1, color2 = (0.0, 0.2, 0.8), (0.2, 0.4, 1.0)
    elif 495 <= wavelength_nm < 570:
        color1, color2 = (0.0, 0.6, 0.2), (0.2, 0.9, 0.4)
    elif 570 <= wavelength_nm < 590:
        color1, color2 = (0.8, 0.6, 0.0), (1.0, 0.8, 0.2)
    elif 590 <= wavelength_nm < 620:
        color1, color2 = (0.8, 0.4, 0.0), (1.0, 0.6, 0.2)
    else:
        color1, color2 = (0.8, 0.0, 0.0), (1.0, 0.2, 0.2)

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(f'wl_{wavelength_nm}', [color1, color2])
    _calculation_cache[cache_key] = cmap
    return cmap


def clear_all_caches():
    """清空所有缓存"""
    calculation_cache.clear()
    _calculation_cache.clear()
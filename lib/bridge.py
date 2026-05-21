#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前后端通信桥梁 - 牛顿环综合实验平台
提供计算功能API供前端调用

重构版本：使用统一的配置、物理计算和绘图模块
"""

import json
import numpy as np

# 使用统一配置模块
from lib.config import (
    init_matplotlib_fonts,
    get_wavelength_cmap,
    get_pandas_read_csv,
    clear_all_caches
)
from lib.physics import (
    newtons_rings_noncontact,
    newtons_rings_truncated,
    newtons_rings_image,
    newtons_rings_image_truncated,
    newtons_rings_convex_concave_contact,
    newtons_rings_image_convex_concave_contact,
    newtons_rings_convex_convex_contact,
    newtons_rings_image_convex_convex_contact,
    newtons_rings_convex_concave_noncontact,
    newtons_rings_image_convex_concave_noncontact,
    newtons_rings_convex_convex_noncontact,
    newtons_rings_image_convex_convex_noncontact
)
from lib.plotting import (
    fig_to_base64,
    create_ring_image,
    create_intensity_plot,
    create_fit_plot,
    create_ring_image_by_R
)

# 初始化字体配置
init_matplotlib_fonts()


# ==================== API函数 - 使用通用绘图函数简化 ====================

def calculate_normal_newton_rings(wavelength_nm, radius_m, spacing_nm, refractive_n):
    """计算普通牛顿环（演示实验）"""
    try:
        lam = wavelength_nm * 1e-9
        h = spacing_nm * 1e-9

        # 计算光强分布
        r, intensity, max_r = newtons_rings_noncontact(lam=lam, R=radius_m, h=h, n=refractive_n)

        # 生成牛顿环图像
        X, Y, B, ym = newtons_rings_image(lam=lam, R=radius_m, levels=50, h=h, n=refractive_n)

        # 创建图像1：牛顿环图样
        ring_image = create_ring_image(X, Y, B, wavelength_nm,
            f'牛顿环模拟图像（λ={wavelength_nm:.1f}nm, h={spacing_nm:.0f}nm)',
            get_wavelength_cmap)

        # 创建图像2：光强分布曲线
        intensity_plot = create_intensity_plot(r, intensity, wavelength_nm, radius_m,
            f'光强分布曲线（λ={wavelength_nm:.1f}nm, R={radius_m:.2f}m)')

        return {
            "success": True,
            "ring_image": f"data:image/png;base64,{ring_image}",
            "intensity_plot": f"data:image/png;base64,{intensity_plot}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculate_truncated_newton_rings(wavelength_nm, radius_m, height_nm, refractive_n):
    """计算截顶式牛顿环 - 复用普通牛顿环逻辑"""
    # 截顶式本质上与普通牛顿环相同
    return calculate_normal_newton_rings(wavelength_nm, radius_m, height_nm, refractive_n)


def calculate_convex_concave_contact(wavelength_nm, R1_m, R2_m, refractive_n):
    """计算平凸-平凹透镜接触式牛顿环"""
    try:
        lam = wavelength_nm * 1e-9

        r, intensity, max_r = newtons_rings_convex_concave_contact(lam=lam, R1=R1_m, R2=R2_m, n=refractive_n)
        X, Y, B, ym = newtons_rings_image_convex_concave_contact(lam=lam, R1=R1_m, R2=R2_m, levels=50, n=refractive_n)

        ring_image = create_ring_image(X, Y, B, wavelength_nm,
            f'平凸-平凹透镜（接触式）\nλ={wavelength_nm:.1f}nm, R1={R1_m:.2f}m, R2={R2_m:.2f}m',
            get_wavelength_cmap)

        intensity_plot = create_intensity_plot(r, intensity, wavelength_nm, R1_m,
            f'曲率差异分析（R1/R2={R1_m/R2_m:.2f}）')

        return {
            "success": True,
            "ring_image": f"data:image/png;base64,{ring_image}",
            "intensity_plot": f"data:image/png;base64,{intensity_plot}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculate_convex_convex_contact(wavelength_nm, R1_m, R2_m, refractive_n):
    """计算双平凸透镜接触式牛顿环"""
    try:
        lam = wavelength_nm * 1e-9

        r, intensity, max_r = newtons_rings_convex_convex_contact(lam=lam, R1=R1_m, R2=R2_m, n=refractive_n)
        X, Y, B, ym = newtons_rings_image_convex_convex_contact(lam=lam, R1=R1_m, R2=R2_m, levels=50, n=refractive_n)

        ring_image = create_ring_image(X, Y, B, wavelength_nm,
            f'双平凸透镜（接触式）\nλ={wavelength_nm:.1f}nm, R1={R1_m:.2f}m, R2={R2_m:.2f}m',
            get_wavelength_cmap)

        intensity_plot = create_intensity_plot(r, intensity, wavelength_nm, R1_m,
            f'双凸面干涉分析（R1={R1_m:.2f}m, R2={R2_m:.2f}m）')

        return {
            "success": True,
            "ring_image": f"data:image/png;base64,{ring_image}",
            "intensity_plot": f"data:image/png;base64,{intensity_plot}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculate_convex_concave_noncontact(wavelength_nm, R1_m, R2_m, spacing_nm, refractive_n):
    """计算平凸-平凹透镜非接触式牛顿环"""
    try:
        lam = wavelength_nm * 1e-9
        h = spacing_nm * 1e-9

        r, intensity, max_r = newtons_rings_convex_concave_noncontact(lam=lam, R1=R1_m, R2=R2_m, h=h, n=refractive_n)
        X, Y, B, ym = newtons_rings_image_convex_concave_noncontact(lam=lam, R1=R1_m, R2=R2_m, levels=50, h=h, n=refractive_n)

        ring_image = create_ring_image(X, Y, B, wavelength_nm,
            f'平凸-平凹透镜（非接触式）\nλ={wavelength_nm:.1f}nm, h={spacing_nm:.0f}nm',
            get_wavelength_cmap)

        intensity_plot = create_intensity_plot(r, intensity, wavelength_nm, R1_m,
            f'间距影响分析（h={spacing_nm:.0f}nm）')

        return {
            "success": True,
            "ring_image": f"data:image/png;base64,{ring_image}",
            "intensity_plot": f"data:image/png;base64,{intensity_plot}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculate_convex_convex_noncontact(wavelength_nm, R1_m, R2_m, spacing_nm, refractive_n):
    """计算双平凸透镜非接触式牛顿环"""
    try:
        lam = wavelength_nm * 1e-9
        h = spacing_nm * 1e-9

        r, intensity, max_r = newtons_rings_convex_convex_noncontact(lam=lam, R1=R1_m, R2=R2_m, h=h, n=refractive_n)
        X, Y, B, ym = newtons_rings_image_convex_convex_noncontact(lam=lam, R1=R1_m, R2=R2_m, levels=50, h=h, n=refractive_n)

        ring_image = create_ring_image(X, Y, B, wavelength_nm,
            f'双平凸透镜（非接触式）\nλ={wavelength_nm:.1f}nm, h={spacing_nm:.0f}nm',
            get_wavelength_cmap)

        intensity_plot = create_intensity_plot(r, intensity, wavelength_nm, R1_m,
            f'双凸面非接触干涉分析（h={spacing_nm:.0f}nm）')

        return {
            "success": True,
            "ring_image": f"data:image/png;base64,{ring_image}",
            "intensity_plot": f"data:image/png;base64,{intensity_plot}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 数据处理功能 ====================

def process_data(csv_content, wavelength_nm, refractive_n):
    """
    处理CSV数据并计算曲率半径

    csv_content: CSV文件内容字符串
    返回: {"success": True, "calculated_R": ..., "fit_plot": base64, "ring_image": base64}
    """
    try:
        import csv

        # 使用标准库csv解析
        lines = csv_content.strip().split('\n')
        if len(lines) < 3:
            return {"success": False, "error": "CSV文件至少需要3行数据"}

        # 解析CSV
        reader = csv.reader(lines)
        rows = list(reader)

        if len(rows) < 3:
            return {"success": False, "error": "CSV文件至少需要3行数据"}

        # 数据格式：第一行为级数，第二行为左侧位置，第三行为右侧位置
        k = []
        left_positions = []
        right_positions = []

        # 解析第一行（级数k）
        for val in rows[0][1:]:
            try:
                if val.strip():
                    k.append(int(float(val.strip())))
            except:
                pass

        # 解析第二行（左侧位置）
        for val in rows[1][1:]:
            try:
                if val.strip():
                    left_positions.append(float(val.strip()))
            except:
                pass

        # 解析第三行（右侧位置）
        for val in rows[2][1:]:
            try:
                if val.strip():
                    right_positions.append(float(val.strip()))
            except:
                pass

        # 确保数据长度一致
        min_length = min(len(k), len(left_positions), len(right_positions))
        if min_length < 3:
            return {"success": False, "error": "有效数据点太少，至少需要3个数据点"}

        k = np.array(k[:min_length])
        left_positions = np.array(left_positions[:min_length])
        right_positions = np.array(right_positions[:min_length])

        # 计算直径和直径平方
        diameter_mm = np.abs(left_positions - right_positions)
        D_sq = (diameter_mm * 1e-3) ** 2

        # 线性拟合
        X = np.column_stack([k, np.ones_like(k)])
        coefficients, _, _, _ = np.linalg.lstsq(X, D_sq, rcond=None)

        # 创建拟合图
        fit_plot, calculated_R = create_fit_plot(k, D_sq, coefficients, wavelength_nm, refractive_n)

        # 创建模拟牛顿环图像
        ring_image = create_ring_image_by_R(calculated_R, wavelength_nm, refractive_n)

        return {
            "success": True,
            "calculated_R": round(calculated_R, 2),
            "fit_plot": f"data:image/png;base64,{fit_plot}",
            "ring_image": f"data:image/png;base64,{ring_image}"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== AI助手功能 ====================

# 导入AI模块
try:
    from ai_module import get_ai_instance, get_streaming_handler, create_stream, remove_stream, clear_ai_history
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("警告: AI模块未找到，AI功能将不可用")


def ai_chat_stream_start(message, stream_id):
    """启动AI流式对话"""
    if not AI_AVAILABLE:
        return {"success": False, "error": "AI模块未加载"}

    try:
        handler = create_stream(stream_id)
        handler.start_stream(message)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def ai_chat_stream_chunk(stream_id):
    """获取AI流式对话的下一个数据块"""
    if not AI_AVAILABLE:
        return {"success": False, "error": "AI模块未加载", "chunk": "", "done": True}

    try:
        handler = get_streaming_handler(stream_id)
        chunk = handler.get_next_chunk()
        done = handler.check_done()
        return {
            "success": True,
            "chunk": chunk,
            "done": done
        }
    except Exception as e:
        return {"success": False, "error": str(e), "chunk": "", "done": True}


def ai_stop_stream(stream_id):
    """停止AI流式对话"""
    if not AI_AVAILABLE:
        return {"success": False, "error": "AI模块未加载"}

    try:
        handler = get_streaming_handler(stream_id)
        handler.stop()
        remove_stream(stream_id)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def ai_clear_history():
    """清空AI对话历史"""
    if not AI_AVAILABLE:
        return {"success": False, "error": "AI模块未加载"}

    try:
        clear_ai_history()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== API路由映射 ====================

API_FUNCTIONS = {
    # 演示实验
    "demo_normal": calculate_normal_newton_rings,
    "demo_truncated": calculate_truncated_newton_rings,
    "demo_convex_concave_contact": calculate_convex_concave_contact,
    "demo_convex_convex_contact": calculate_convex_convex_contact,
    "demo_convex_concave_noncontact": calculate_convex_concave_noncontact,
    "demo_convex_convex_noncontact": calculate_convex_convex_noncontact,
    # 数据处理
    "process_data": process_data,
    # AI助手
    "ai_chat_stream_start": ai_chat_stream_start,
    "ai_chat_stream_chunk": ai_chat_stream_chunk,
    "ai_stop_stream": ai_stop_stream,
    "ai_clear_history": ai_clear_history,
    # 系统
    "exit": lambda **kwargs: {"success": True, "message": "应用退出"},
}


def call_api(method, params):
    """
    调用API函数
    method: API方法名
    params: 参数字典
    返回: JSON字符串
    """
    if method in API_FUNCTIONS:
        try:
            result = API_FUNCTIONS[method](**params)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    else:
        return json.dumps({"success": False, "error": f"未知方法: {method}"})
# 牛顿环综合实验平台

基于 PyQt5 + HTML/Tailwind CSS 的牛顿环实验教学桌面应用。

## 功能概述

本软件是一个面向大学物理实验教学的综合性实验平台，支持以下功能：

### 1. 牛顿环实验模拟
- 普通牛顿环（平凸透镜 + 平面玻璃）
- 截顶式牛顿环
- 平凸透镜 + 平凹透镜组合
- 双平凸透镜组合
- 支持接触式和非接触式两种模式

### 2. 实验参数设置
- 波长调节（可见光范围）
- 曲率半径调节
- 透镜类型选择
- 接触/非接触模式切换

### 3. 数据处理
- 测量牛顿环环序数和直径
- 线性拟合法计算曲率半径
- 数据导出（CSV 格式）

### 4. AI 助手
- 对接 DeepSeek 大语言模型
- 流式对话响应
- 解答牛顿环实验及物理学问题

## 技术架构

### 后端
- Python 3.x
- PyQt5/QtWebEngine - 桌面应用框架
- NumPy - 物理计算
- Matplotlib - 数据可视化

### 前端
- HTML5 + Tailwind CSS
- JavaScript 原生（无框架依赖）

### 模块结构

```
├── main.py              # 应用入口
├── app/
│   ├── bridge_handler.py  # 前后端通信桥接
│   └── main_window.py    # 主窗口
├── lib/
│   ├── physics.py       # 物理计算核心
│   ├── plotting.py      # 绘图工具
│   ├── ai_module.py     # DeepSeek AI 模块
│   ├── config.py       # 统一配置
│   └── gui/           # Qt GUI 组件
└── frontend/
    └── index.html     # Web 界面
```

## 环境配置

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行开发版本

```bash
python main.py
```

### 打包发布

```bash
python setup.py build
```

## 环境要求

- Python 3.8+
- Windows 10/11（其他平台未测试）
- 至少 4GB 可用内存

## 项目特点

1. **混合架构**：PyQt5 内嵌浏览器 + HTML/Tailwind 前端
2. **物理精确**：基于薄膜干涉理论的精确计算
3. **AI 辅助**：集成大语言模型解答实验问题
4. **数据处理**：支持实验数据的记录、拟合和导出

## 许可证

仅供教学实验使用。
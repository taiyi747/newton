# -*- coding: utf-8 -*-
"""
标尺窗口模块 - ScaleWindow 类
"""

from .base import QtWidgets, QtCore, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, np, Figure, FigureCanvas


class ScaleWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle('刻度窗口')
        self.setGeometry(100, 100, 800, 700)

        self.main_window = main_window
        self.center_position_mm = 25
        self.show_data = False  # 控制横向和纵向标尺读数显示
        # 保存当前的current_level，用于判断是否需要更新透镜窗口

        # 延迟导入全局变量
        import sys
        if 'lib.仿真' in sys.modules:
            sim = sys.modules['lib.仿真']
        else:
            import lib.仿真 as sim
            sys.modules['lib.仿真'] = sim
        self._sim_module = sim

        self.saved_level = sim.current_level

        # 创建画布
        self.figure = Figure(figsize=(10, 1.2))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)

        self.vertical_figure = Figure(figsize=(10, 3.5))
        self.vertical_canvas = FigureCanvas(self.vertical_figure)
        self.vertical_canvas.setParent(self)

        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.addWidget(self.vertical_canvas)

        # 按钮布局
        self.button_layout = QHBoxLayout()
        layout.addLayout(self.button_layout)

        # 控制按钮
        self.move_to_left_40_button = QPushButton("左40级", self)
        self.move_to_left_40_button.clicked.connect(self.move_to_left_40)
        self.button_layout.addWidget(self.move_to_left_40_button)

        self.move_left_5_button = QPushButton("←5级", self)
        self.move_left_5_button.clicked.connect(self.move_left_5)
        self.button_layout.addWidget(self.move_left_5_button)

        self.center_button = QPushButton("居中", self)
        self.center_button.clicked.connect(self.center)
        self.button_layout.addWidget(self.center_button)

        self.move_right_5_button = QPushButton("5级→", self)
        self.move_right_5_button.clicked.connect(self.move_right_5)
        self.button_layout.addWidget(self.move_right_5_button)

        # 显示读数开关（同时控制横向和纵向）
        self.data_switch = QtWidgets.QCheckBox("显示读数", self)
        self.data_switch.stateChanged.connect(self.toggle_data_display)
        self.button_layout.addWidget(self.data_switch)

        # 初始绘制
        self.update_displays()

    def toggle_data_display(self, state):
        """切换横向和纵向标尺读数显示"""
        self.show_data = (state == QtCore.Qt.Checked)
        self.update_displays()

    def calculate_ring_radius(self, k, lam, R, is_dark=True):
        """计算牛顿环半径（mm）"""
        if k < 0:
            return 0.0
        factor = k if is_dark else k + 0.5
        if factor <= 0:
            return 0.0
        return np.sqrt(factor * lam * R) * 1000

    def draw_scale(self):
        """绘制横向标尺，带条件读数显示"""
        sim = self._sim_module
        global current_level, lam, R

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # 标尺参数
        scale_length_mm = 50
        scale_length_pixels = 500
        resolution = 1

        ax.set_xlim(0, scale_length_pixels)
        ax.set_ylim(0, 60)
        ax.set_yticks([])
        ax.set_xticks([])

        # 绘制刻度
        for pos_mm in np.arange(0, scale_length_mm + resolution, resolution):
            pos_pixels = (pos_mm / scale_length_mm) * scale_length_pixels
            if pos_mm % 10 == 0:
                ax.plot([pos_pixels, pos_pixels], [20, 40], 'k-', linewidth=1.5)
                ax.text(pos_pixels - 6, 10, f"{int(pos_mm)}",
                       fontsize=11, color='black', fontweight='bold')
            else:
                ax.plot([pos_pixels, pos_pixels], [25, 35], 'k-', linewidth=0.8)

        # 计算指针位置
        if hasattr(self.main_window, 'lens_window'):
            current_k = abs(sim.current_level)
            power_on = hasattr(self.main_window, 'power_window') and \
                      getattr(self.main_window.power_window, 'is_on', False)

            radius_mm = self.calculate_ring_radius(current_k, sim.lam, sim.R, is_dark=not power_on)
            direction = -1 if sim.current_level < 0 else 1
            pointer_position = self.center_position_mm + direction * radius_mm
            pointer_position = max(0, min(pointer_position, scale_length_mm))

            pointer_pixels = (pointer_position / scale_length_mm) * scale_length_pixels

            # 绘制指针
            ax.plot([pointer_pixels, pointer_pixels], [43, 50], 'r', linewidth=3)

            # 条件显示读数（由开关控制）
            if self.show_data:
                ax.text(pointer_pixels, 55, f'{pointer_position:.3f}mm',
                       fontsize=10, color='red', ha='center', fontweight='bold')

        # 中心参考线
        center_pixels = (self.center_position_mm / scale_length_mm) * scale_length_pixels
        ax.plot([center_pixels, center_pixels], [15, 45], 'b--', linewidth=1, alpha=0.5)

        # 隐藏边框
        for spine in ax.spines.values():
            spine.set_visible(False)

        self.canvas.draw()
        self.pointer_position = pointer_position if hasattr(self, 'pointer_position') else self.center_position_mm

    def draw_vertical_scale(self):
        """绘制纵向鼓轮（机械式：刻度0-99，往下拧数值变大）"""
        self.vertical_figure.clear()
        ax = self.vertical_figure.add_subplot(111)

        # 鼓轮参数
        window_size = 15  # 显示窗口行数
        indicator_line = 7  # 指示线固定在第7行（中间）

        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, window_size - 0.5)
        ax.set_xticks([])
        ax.set_yticks([])

        # 从横向标尺获取精确的指针位置
        if hasattr(self, 'pointer_position'):
            decimal_part = self.pointer_position - int(self.pointer_position)
            drum_reading = round(decimal_part * 100, 1)
        else:
            drum_reading = 0

        # 鼓轮读数：0-99.9，表示0.00-0.99mm
        base_scale = int(drum_reading)  # 当前指针所在的整数刻度（0-99）
        fractional = drum_reading - base_scale  # 小数部分（0-0.9）

        # 修正：四舍五入到1位小数
        sub_scale = int(round(fractional * 10))
        if sub_scale >= 10:
            sub_scale = 0
            base_scale = (base_scale + 1) % 100

        # 鼓轮显示逻辑（往下拧数值变大）：
        # - 往下拧，鼓轮向下移动，显示的数值增大
        # - 视图从上到下，数值从小到大（上面小，下面大）
        # - 指示线对准当前刻度 base_scale
        # - 上面一行（i=6）显示 base_scale - 1
        # - 下面一行（i=8）显示 base_scale + 1
        # - 每行显示一个整数刻度

        # 计算每一行应该显示的刻度值
        # 注意：鼓轮显示需要调整，确保指针对准正确的刻度
        # 当读数为64.5时，指针应该对准64和65之间，而不是65
        for i in range(window_size):
            # i=0在最上面，显示 base_scale - 7
            # i=7在中间，显示 base_scale
            # i=14在最下面，显示 base_scale + 7
            scale_offset = i - indicator_line  # -7, -6, ..., 0, ..., 6, 7
            reading = (base_scale + scale_offset) % 100

            # 计算y位置（考虑小数偏移）
            # fractional表示指针在当前刻度的位置（0-0.9）
            # 鼓轮向下移动时（fractional增加），看到的刻度向上走
            # 所以y_pos = i - fractional，而不是 i + fractional
            y_pos = i - fractional

            # 确保刻度在可视范围内
            if y_pos < -1.0 or y_pos > window_size + 0.5:
                continue

            # 判断是否是主刻度（10的倍数）
            is_main = (reading % 10 == 0)

            # 绘制刻度线
            if is_main:
                # 主刻度：长刻度线 + 数字
                ax.plot([0.35, 0.65], [y_pos, y_pos], 'k-', linewidth=1.5)
                ax.text(0.7, y_pos, f"{reading:02d}",
                       fontsize=11, color='black', ha='left', fontweight='bold')
            else:
                # 短刻度线
                ax.plot([0.4, 0.6], [y_pos, y_pos], 'k-', linewidth=0.8)

        # 绘制指示线（红色）
        ax.plot([0.3, 0.7], [indicator_line, indicator_line], 'r-', linewidth=2.5)
        if self.show_data:
            ax.text(0.75, indicator_line, f"{base_scale:02d}.{sub_scale}",
                   fontsize=14, color='red', ha='left', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

        # 鼓轮标题
        ax.text(0.5, window_size - 0.8, "鼓轮读数（0.01mm）",
               fontsize=12, color='black', ha='center', fontweight='bold')

        # 样式
        ax.set_facecolor('#f0f0f0')
        for spine in ax.spines.values():
            spine.set_visible(False)

        self.vertical_canvas.draw()

    def move_to_left_40(self):
        sim = self._sim_module
        sim.current_level = -40
        self.update_displays()

    def move_left_5(self):
        sim = self._sim_module
        sim.current_level -= 5
        self.update_displays()

    def center(self):
        sim = self._sim_module
        sim.current_level = 0
        self.update_displays()

    def move_right_5(self):
        sim = self._sim_module
        sim.current_level += 5
        self.update_displays()

    def update_displays(self):
        """更新所有显示"""
        sim = self._sim_module
        global current_level, lam, R
        current_level = sim.current_level
        lam = sim.lam
        R = sim.R

        # 只有在current_level实际改变时才更新透镜窗口
        if hasattr(self.main_window, 'lens_window') and current_level != self.saved_level:
            if current_level < 0:
                offset = -np.sqrt(abs(current_level) * lam * R)
            else:
                offset = np.sqrt(current_level * lam * R)
            self.main_window.lens_window.move_ring(offset)
        # 确保saved_level始终与current_level同步，防止重复移动
        self.saved_level = current_level

        self.draw_scale()
        self.draw_vertical_scale()

    def resizeEvent(self, event):
        """窗口大小调整时重绘"""
        self.canvas.resize(self.width(), 150)
        self.vertical_canvas.resize(self.width(), 350)
        self.draw_scale()
        self.draw_vertical_scale()
        super().resizeEvent(event)
# -*- coding: utf-8 -*-
"""
透镜窗口模块 - LensWindow 类（牛顿环核心仿真）
"""

from .base import (QtWidgets, QtGui, QtCore, Figure, FigureCanvas,
                   sodium_cmap, scale_pixmap)

# 延迟导入全局变量
_main_module = None

def _get_main_module():
    """获取主仿真模块的全局变量"""
    global _main_module
    if _main_module is None:
        # 延迟导入仿真模块以获取全局变量
        import sys
        if 'lib.仿真' in sys.modules:
            _main_module = sys.modules['lib.仿真']
        else:
            import lib.仿真 as sim_module
            _main_module = sim_module
            sys.modules['lib.仿真'] = sim_module
    return _main_module


class LensWindow(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initial_offset = 6  # 初始偏移量，使牛顿环图像居中
        self.offset = self.initial_offset
        self.cover_pixmap = None
        self.current_image_index = 0
        self.image_paths = ["qrc/mj1.png", "qrc/mj2.png", "qrc/mj3.png"]
        # 亮度级别：40, 70, 100
        self.brightness_level = 0  # 0=40%, 1=70%, 2=100%
        self.brightness_values = [0.4, 0.7, 1.0]
        self.initUI()

    def initUI(self):
        self.setWindowTitle('目镜窗口')
        self.setFixedSize(800, 800)

        self.figure = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.canvas.resize(self.width(), self.height())

        # 亮度滤镜层 - 用于调节图像亮度（在canvas之后创建，但在cover_label之前）
        self.filter_label = QtWidgets.QLabel(self)
        self.filter_label.setGeometry(0, 0, self.width(), self.height())
        self.filter_label.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.filter_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.cover_label = QtWidgets.QLabel(self)
        self.cover_label.setGeometry(0, 0, self.width(), self.height())
        self.cover_label.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        self.load_cover_image()

        # 目镜调节按钮（右上角）
        self.image_toggle_button = QtWidgets.QPushButton(" ", self)
        self.image_toggle_button.setGeometry(680, 30, 100, 100)
        self.image_toggle_button.clicked.connect(self.toggle_image)
        self.image_toggle_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.image_toggle_button.setToolTip("调整目镜")

        # 物镜调节按钮 - 在目镜按钮下方对称位置（右下角）
        self.wj_button = QtWidgets.QPushButton(" ", self)
        self.wj_button.setGeometry(700, 690, 100, 100)
        # 设置物镜按钮图标
        wujing_icon = QtGui.QIcon("qrc/wujing.png")
        self.wj_button.setIcon(wujing_icon)
        self.wj_button.setIconSize(QtCore.QSize(80, 80))
        self.wj_button.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: none;")
        self.wj_button.setToolTip("调节物镜")
        self.wj_button.clicked.connect(self.cycle_brightness)

        tooltip_style = """
        QToolTip {
            background-color: black;
            color: white;
            border: 1px solid white;
            padding: 2px;
            opacity: 200;
        }
        """
        self.setStyleSheet(tooltip_style)

        self.update_newtons_rings()

        self.load_image(0)

    def load_cover_image(self):
        cover_image_path = "qrc/mj1.png"
        self.cover_pixmap = QtGui.QPixmap(cover_image_path)
        if not self.cover_pixmap.isNull():
            self.cover_pixmap = scale_pixmap(self.cover_pixmap, self.width(), self.height())
            self.cover_label.setPixmap(self.cover_pixmap)
            self.cover_label.setScaledContents(True)
        else:
            print(f"无法加载图片: {cover_image_path}")

    def update_newtons_rings(self):
        # 获取全局变量
        sim = _get_main_module()
        global lam, R, newtons_rings

        # 检查显示牛顿环图像的条件
        power_on = hasattr(self.main_window, 'power_window') and \
                   getattr(self.main_window.power_window, 'is_on', False)
        newton_state_t = self.main_window.newton_state == 'T'
        reflector_state_ok = hasattr(self.main_window, 'reflector_window') and \
                             getattr(self.main_window.reflector_window, 'current_state', 0) == 1

        if power_on and newton_state_t and reflector_state_ok:
            # 条件满足，显示牛顿环图像
            X, Y, B, ym = sim.newtons_rings(lam=sim.lam, R=sim.R, offset=self.offset)

            self.figure.clear()

            ax = self.figure.add_subplot(111)
            # 渲染牛顿环图像
            ax.pcolormesh(X, Y, B, shading='gouraud', cmap=sodium_cmap)

            ax.set_axis_off()

            self.figure.subplots_adjust(left=0, right=1, bottom=0, top=1)

            self.canvas.draw()

            # 更新亮度滤镜
            self.update_brightness_filter()
        else:
            # 条件不满足，清空图像
            self.figure.clear()
            self.canvas.draw()

    def update_brightness_filter(self):
        """更新亮度滤镜层"""
        brightness = self.brightness_values[self.brightness_level]
        # 亮度越低，黑色覆盖层越不透明
        if brightness < 1.0:
            opacity = int((1.0 - brightness) * 255)
            self.filter_label.setStyleSheet(
                f"background-color: rgba(0, 0, 0, {opacity});"
            )
        else:
            self.filter_label.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

    def move_ring(self, offset):
        self.offset = offset
        self.update_newtons_rings()

    def load_image(self, index):
        image_path = self.image_paths[index]
        pixmap = QtGui.QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = scale_pixmap(pixmap, self.width(), self.height())
            self.cover_label.setPixmap(pixmap)
            self.cover_label.setScaledContents(True)
        else:
            print(f"无法加载图片: {image_path}")

    def toggle_image(self):
        """切换目镜图片 - 用于任务4（目镜调焦）"""
        self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
        self.load_image(self.current_image_index)
        # 目镜状态为3（第3张图片mj3.png）时表示调节清晰，完成任务4
        # 只有在放置了牛顿环的情况下才能完成任务4
        if self.current_image_index == 2 and self.main_window.newton_state == 'T':
            self.main_window.update_task_style(3, True)
        else:
            self.main_window.update_task_style(3, False)
            # 如果任务4未完成，重置任务5
            self.main_window.update_task_style(4, False)

    def cycle_brightness(self):
        """循环调整图像亮度 - 用于任务5（物镜调焦）
        亮度在 40% -> 70% -> 100% 之间循环
        只有任务4完成后才能调节
        """
        # 只有任务4完成后才能调节物镜
        if self.main_window.task_states[3] == 0:
            return

        self.brightness_level = (self.brightness_level + 1) % 3

        # 更新显示
        self.update_brightness_filter()

        # 当亮度为100%时完成任务5
        if self.brightness_level == 2:  # 100%
            # 先更新任务状态
            self.main_window.update_task_style(4, True)
            # 完成任务5后弹出标尺和数据窗口
            # 使用定时器延迟显示，避免当前操作影响
            QtCore.QTimer.singleShot(100, self.main_window.show_scale_and_data_windows)
        else:
            # 如果亮度不是100%，重置任务5
            self.main_window.update_task_style(4, False)

    def resizeEvent(self, event):
        self.canvas.resize(self.width(), self.height())
        self.filter_label.setGeometry(0, 0, self.width(), self.height())
        if self.cover_pixmap:
            self.cover_pixmap = scale_pixmap(self.cover_pixmap, self.width(), self.height())
            self.cover_label.setPixmap(self.cover_pixmap)
            self.cover_label.resize(self.width(), self.height())
        super().resizeEvent(event)
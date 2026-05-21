# -*- coding: utf-8 -*-
"""
主窗口模块 - MainWindow 类
"""

from .base import QtWidgets, QtGui, QtCore, scale_pixmap

# 导入全局变量（来自 lib.仿真 模块）
import sys
if 'lib.仿真' in sys.modules:
    _sim = sys.modules['lib.仿真']
else:
    import lib.仿真 as _sim


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # 延迟导入 Ui_Form，避免循环依赖
        from .ui_form import Ui_Form
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.initUI()
        self.newton_state = 'F'  # 牛顿环状态，默认为 F
        self.reflector_window = None  # 用于存储反射镜窗口的引用
        self.data_window = None  # 新增的数据窗口引用
        self.scale_window = None  # 新增的刻度窗口引用
        # 任务状态: 0=未完成(白色), 1=已完成(绿色)
        self.task_states = [0, 0, 0, 0, 0, 0]
        print(f"曲率半径 R: {_sim.R}")

    def initUI(self):
        self.ui.dy_Button.clicked.connect(self.show_power_window)
        self.ui.mj_Button.clicked.connect(self.show_lens_window_only)
        self.ui.fsj_Button.clicked.connect(self.show_reflector_window)
        self.ui.ndh_Button.clicked.connect(self.toggle_newton_state)
        self.set_tooltip_style()

    def update_task_style(self, task_index, completed=True):
        """更新任务步骤的样式"""
        if 0 <= task_index < len(self.ui.task_steps):
            step_label = self.ui.task_steps[task_index]
            self.task_states[task_index] = 1 if completed else 0
            if completed:
                step_label.setStyleSheet("""
                    color: white;
                    font-size: 13px;
                    background-color: #4CAF50;
                    border-radius: 5px;
                    padding: 5px;
                    border: 1px solid #45a049;
                    font-weight: bold;
                """)
            else:
                step_label.setStyleSheet("""
                    color: #333;
                    font-size: 13px;
                    background-color: white;
                    border-radius: 5px;
                    padding: 5px;
                    border: 1px solid #ccc;
                """)

    def set_tooltip_style(self):
        style = """
        QToolTip {
            background-color: black;
            color: white;
            border: 1px solid white;
            padding: 2px;
            opacity: 200;
        }
        """
        self.setStyleSheet(style)

    def show_power_window(self):
        # 延迟导入
        from .power_window import PowerWindow
        self.power_window = PowerWindow(self)
        self.power_window.show()

    def show_lens_window_only(self):
        """显示目镜窗口 - 根据任务状态决定行为"""
        # 任务4未完成时，只显示目镜窗口
        # 任务4完成且任务5未完成时，可以点击物镜按钮调整亮度
        # 任务5完成后，显示标尺和数据窗口
        from .lens_window import LensWindow

        if not hasattr(self, 'lens_window') or self.lens_window is None or not self.lens_window.isVisible():
            self.lens_window = LensWindow(self)
            self.lens_window.show()
        else:
            self.lens_window.activateWindow()

        # 如果任务5已完成，显示标尺和数据窗口
        if self.task_states[4] == 1:
            self.show_scale_and_data_windows()

    def show_scale_and_data_windows(self):
        """显示标尺窗口和数据记录窗口"""
        from .scale_window import ScaleWindow
        from .data_window import DataWindow

        if self.scale_window is None or not self.scale_window.isVisible():
            self.scale_window = ScaleWindow(self)
            self.scale_window.show()
        else:
            self.scale_window.activateWindow()

        if self.data_window is None or not self.data_window.isVisible():
            self.data_window = DataWindow(self, self.scale_window)
            self.data_window.show()
        else:
            self.data_window.activateWindow()

    def show_reflector_window(self):
        from .reflector_window import ReflectorWindow
        if self.reflector_window is None or not self.reflector_window.isVisible():
            self.reflector_window = ReflectorWindow(self)
            self.reflector_window.show()
        else:
            self.reflector_window.activateWindow()

    def toggle_newton_state(self):
        self.newton_state = 'T' if self.newton_state == 'F' else 'F'
        print(f"牛顿环状态: {self.newton_state}")
        # 放置牛顿环时完成任务3
        if self.newton_state == 'T':
            self.update_task_style(2, True)
        else:
            self.update_task_style(2, False)
            # 取下牛顿环时重置任务4
            self.update_task_style(3, False)
        self.update_main_image_based_on_state()

    def update_main_image_based_on_state(self):
        if hasattr(self, 'power_window') and self.power_window:
            if self.newton_state == 'T' and self.power_window.is_on:
                self.update_main_image("qrc/T-O.png")
            elif self.newton_state == 'T' and not self.power_window.is_on:
                self.update_main_image("qrc/T-C.png")
            elif self.newton_state == 'F' and self.power_window.is_on:
                self.update_main_image("qrc/F-O.png")
            else:
                self.update_main_image("qrc/F-C.png")
        else:
            if self.newton_state == 'T':
                self.update_main_image("qrc/T-C.png")
            else:
                self.update_main_image("qrc/F-C.png")

    def closeEvent(self, event):
        for window in [getattr(self, attr, None) for attr in
                       ['power_window', 'lens_window', 'reflector_window', 'scale_window', 'data_window']]:
            if window:
                window.close()
        event.accept()

    def update_main_image(self, image_path):
        pixmap = QtGui.QPixmap(image_path)
        pixmap = scale_pixmap(pixmap, self.ui.yiqi.width(), self.ui.yiqi.height())
        self.ui.yiqi.setPixmap(pixmap)
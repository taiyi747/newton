# -*- coding: utf-8 -*-
"""
主窗口类 - NewtonRingsApp 类
"""

import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl, Qt, QEvent
from PyQt5.QtGui import QCursor

# 全局变量占位（由 main.py 设置）
BRIDGE_HANDLER_CLASS = None
APP_DIR = ""


def _init_globals(bridge_handler_class, app_dir):
    """初始化全局变量（由 main.py 调用）"""
    global BRIDGE_HANDLER_CLASS, APP_DIR
    BRIDGE_HANDLER_CLASS = bridge_handler_class
    APP_DIR = app_dir


class NewtonRingsApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口大小
        self.resize(1920, 1080)
        self.setMinimumSize(400, 300)

        # 创建中央部件
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #e0e0e0;
            }
        """)
        self.setCentralWidget(self.central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)

        # 创建Web视图
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("border-radius: 6px; background: white;")

        # 设置WebChannel
        self.setup_web_channel()

        # 获取HTML文件路径
        html_path = os.path.join(APP_DIR, "frontend", "index.html")

        if os.path.exists(html_path):
            self.web_view.load(QUrl.fromLocalFile(html_path))
        else:
            error_html = f"""
            <html><body style="font-family: Arial; padding: 50px;">
            <h2 style="color: #ff4444;">错误：HTML文件未找到</h2>
            <p>请确保 frontend/index.html 文件存在。</p>
            <p>查找路径：{html_path}</p>
            </body></html>
            """
            self.web_view.setHtml(error_html)

        main_layout.addWidget(self.web_view)

        # 拖动和调整大小状态
        self.middle_dragging = False
        self.middle_drag_pos = None
        self.resizing = False
        self.resize_edge = None
        self.resize_start_pos = None
        self.resize_start_geometry = None

        # 双击检测
        self.last_click_time = 0

        # 安装事件过滤器到web_view
        self.web_view.installEventFilter(self)

        # 启用鼠标跟踪
        self.setMouseTracking(True)
        self.central_widget.setMouseTracking(True)
        self.web_view.setMouseTracking(True)

        # 仿真实验窗口引用
        self.simulation_window = None

        # 存储窗口最大化前的几何信息
        self._normal_geometry = None
        self._is_maximized = False

    def toggle_maximize(self):
        """切换窗口最大化/还原状态"""
        if self._is_maximized:
            # 还原窗口
            self.showNormal()
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            self._is_maximized = False
            # 通知前端窗口已还原
            self.notify_maximize_state_changed(False)
        else:
            # 最大化窗口
            self._normal_geometry = self.geometry()
            self.showMaximized()
            self._is_maximized = True
            # 通知前端窗口已最大化
            self.notify_maximize_state_changed(True)

    def notify_maximize_state_changed(self, is_maximized):
        """通知前端窗口最大化状态已改变"""
        try:
            script = f"""
                if (typeof window.onMaximizeStateChanged === 'function') {{
                    window.onMaximizeStateChanged({str(is_maximized).lower()});
                }}
            """
            self.web_view.page().runJavaScript(script)
        except Exception:
            pass

    def setup_web_channel(self):
        """设置WebChannel用于前后端通信"""
        self.channel = QWebChannel()
        # 延迟导入，避免循环依赖
        from app.bridge_handler import BridgeHandler
        self.bridge_handler = BridgeHandler()
        self.bridge_handler.main_window = self
        self.channel.registerObject("bridge", self.bridge_handler)
        self.web_view.page().setWebChannel(self.channel)

    def open_simulation(self):
        """打开仿真实验窗口"""
        try:
            # 动态导入仿真模块
            import importlib.util
            from lib import 仿真 as sim_module

            # 延迟导入 lib.仿真 模块
            import sys
            lib_dir = os.path.join(APP_DIR, 'lib')
            simulation_path = os.path.join(lib_dir, '仿真.py')

            if os.path.exists(simulation_path):
                spec = importlib.util.spec_from_file_location("simulation", simulation_path)
                simulation_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(simulation_module)

                if self.simulation_window is None or not self.simulation_window.isVisible():
                    self.simulation_window = simulation_module.MainWindow()
                    self.simulation_window.show()
                else:
                    self.simulation_window.activateWindow()
            else:
                print(f"仿真实验文件未找到: {simulation_path}")
        except Exception as e:
            print(f"打开仿真实验窗口失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def eventFilter(self, obj, event):
        """事件过滤器，处理web_view的鼠标事件"""
        if obj == self.web_view:
            event_type = event.type()

            # 处理鼠标按下
            if event_type == QEvent.MouseButtonPress:
                if event.button() == Qt.MiddleButton:
                    # 中键按下 - 开始拖动（任意位置）
                    self.middle_dragging = True
                    self.middle_drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                    self.web_view.setCursor(QCursor(Qt.SizeAllCursor))
                    return True

                elif event.button() == Qt.LeftButton:
                    # 左键按下 - 检测是否在边缘
                    pos_in_window = self.web_view.mapToParent(event.pos())
                    edge = self.get_edge_at_pos(pos_in_window)

                    if edge:
                        # 在边缘 - 开始调整大小
                        self.resizing = True
                        self.resize_edge = edge
                        self.resize_start_pos = event.globalPos()
                        self.resize_start_geometry = self.geometry()
                        return True
                    else:
                        # 不在边缘 - 检测双击
                        current_time = time.time() * 1000
                        if current_time - self.last_click_time < 300:
                            # 双击关闭
                            self.close()
                            return True
                        self.last_click_time = current_time
                        # 不拦截单击事件，让web_view正常处理
                        return False

            # 处理鼠标移动
            elif event_type == QEvent.MouseMove:
                pos_in_window = self.web_view.mapToParent(event.pos())

                # 如果正在拖动
                if self.middle_dragging and (event.buttons() & Qt.MiddleButton):
                    new_pos = event.globalPos() - self.middle_drag_pos
                    self.move(new_pos)
                    return True

                # 如果正在调整大小
                elif self.resizing and (event.buttons() & Qt.LeftButton):
                    self.do_resize(event.globalPos())
                    return True

                # 否则更新光标
                else:
                    edge = self.get_edge_at_pos(pos_in_window)
                    if edge:
                        self.web_view.setCursor(self.get_cursor_for_edge(edge))
                    else:
                        self.web_view.unsetCursor()
                    return False

            # 处理鼠标释放
            elif event_type == QEvent.MouseButtonRelease:
                if event.button() == Qt.MiddleButton and self.middle_dragging:
                    self.middle_dragging = False
                    self.middle_drag_pos = None
                    self.web_view.unsetCursor()
                    return True

                elif event.button() == Qt.LeftButton and self.resizing:
                    self.resizing = False
                    self.resize_edge = None
                    self.resize_start_pos = None
                    self.resize_start_geometry = None
                    return True

        return super().eventFilter(obj, event)

    def get_edge_at_pos(self, pos):
        """判断鼠标位置是否在边缘"""
        margin = 10
        x, y = pos.x(), pos.y()
        w, h = self.central_widget.width(), self.central_widget.height()

        on_left = x < margin
        on_right = x > w - margin
        on_top = y < margin
        on_bottom = y > h - margin

        if on_left and on_top:
            return 'top-left'
        elif on_right and on_top:
            return 'top-right'
        elif on_left and on_bottom:
            return 'bottom-left'
        elif on_right and on_bottom:
            return 'bottom-right'
        elif on_left:
            return 'left'
        elif on_right:
            return 'right'
        elif on_top:
            return 'top'
        elif on_bottom:
            return 'bottom'

        return None

    def get_cursor_for_edge(self, edge):
        """根据边缘返回对应的光标形状"""
        cursors = {
            'left': Qt.SizeHorCursor,
            'right': Qt.SizeHorCursor,
            'top': Qt.SizeVerCursor,
            'bottom': Qt.SizeVerCursor,
            'top-left': Qt.SizeFDiagCursor,
            'top-right': Qt.SizeBDiagCursor,
            'bottom-left': Qt.SizeBDiagCursor,
            'bottom-right': Qt.SizeFDiagCursor
        }
        return QCursor(cursors.get(edge, Qt.ArrowCursor))

    def mousePressEvent(self, event):
        """主窗口鼠标按下事件"""
        if event.button() == Qt.MiddleButton:
            self.middle_dragging = True
            self.middle_drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.SizeAllCursor))
            event.accept()
        elif event.button() == Qt.LeftButton:
            edge = self.get_edge_at_pos(event.pos())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
                event.accept()

    def mouseMoveEvent(self, event):
        """主窗口鼠标移动事件"""
        if self.middle_dragging and (event.buttons() & Qt.MiddleButton):
            self.move(event.globalPos() - self.middle_drag_pos)
            event.accept()
        elif self.resizing:
            self.do_resize(event.globalPos())
            event.accept()
        else:
            edge = self.get_edge_at_pos(event.pos())
            if edge:
                self.setCursor(self.get_cursor_for_edge(edge))
            else:
                self.unsetCursor()

    def mouseReleaseEvent(self, event):
        """主窗口鼠标释放事件"""
        if event.button() == Qt.MiddleButton and self.middle_dragging:
            self.middle_dragging = False
            self.middle_drag_pos = None
            self.unsetCursor()
            event.accept()
        elif event.button() == Qt.LeftButton and self.resizing:
            self.resizing = False
            self.resize_edge = None
            self.resize_start_pos = None
            self.resize_start_geometry = None
            event.accept()

    def do_resize(self, global_pos):
        """执行调整大小"""
        if not self.resize_start_geometry:
            return

        delta = global_pos - self.resize_start_pos
        new_geom = self.resize_start_geometry

        left = new_geom.left()
        top = new_geom.top()
        right = new_geom.right()
        bottom = new_geom.bottom()

        min_width = self.minimumWidth()
        min_height = self.minimumHeight()

        if 'left' in self.resize_edge:
            new_left = left + delta.x()
            if right - new_left >= min_width:
                left = new_left
        elif 'right' in self.resize_edge:
            new_right = right + delta.x()
            if new_right - left >= min_width:
                right = new_right

        if 'top' in self.resize_edge:
            new_top = top + delta.y()
            if bottom - new_top >= min_height:
                top = new_top
        elif 'bottom' in self.resize_edge:
            new_bottom = bottom + delta.y()
            if new_bottom - top >= min_height:
                bottom = new_bottom

        self.setGeometry(left, top, right - left, bottom - top)
# -*- coding: utf-8 -*-
"""
反射镜窗口模块 - ReflectorWindow 类
"""

from .base import QtWidgets, QtGui, QtCore, scale_pixmap


class ReflectorWindow(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Reflector Window')
        self.setFixedSize((800 * 16) // 9, 800)

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setGeometry(0, 0, 800, (800 * 16) // 9)
        self.image_label.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        initial_image = "qrc/0.png"
        pixmap = QtGui.QPixmap(initial_image)
        pixmap = scale_pixmap(pixmap, self.image_label.width(), self.image_label.height())
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        self.state_button = QtWidgets.QPushButton("", self)
        self.state_button.setGeometry(425, 400, 50, 100)
        self.state_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.state_button.clicked.connect(self.toggle_state)
        self.state_button.setToolTip("点击调整角度")

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

        self.states = [
            {"image": "qrc/0.png", "text": ""},
            {"image": "qrc/135.png", "text": ""},
            {"image": "qrc/90.png", "text": ""},
            {"image": "qrc/45.png", "text": ""}
        ]
        self.current_state = 0
        if hasattr(self.main_window, 'reflector_state'):
            self.current_state = self.main_window.reflector_state
        self.update_state()

    def toggle_state(self):
        self.current_state = (self.current_state + 1) % 4
        self.update_state()
        # 检查是否调整到第二张图片（状态1，135度）
        if self.current_state == 1:
            self.main_window.update_task_style(1, True)
        else:
            self.main_window.update_task_style(1, False)

    def update_state(self):
        state = self.states[self.current_state]
        pixmap = QtGui.QPixmap(state["image"])
        pixmap = scale_pixmap(pixmap, self.image_label.width(), self.image_label.height())
        self.image_label.setPixmap(pixmap)
        self.state_button.setText(state["text"])

    def closeEvent(self, event):
        self.main_window.reflector_state = self.current_state
        event.accept()

    def resizeEvent(self, event):
        if hasattr(self, 'image_label') and self.image_label:
            current_state = self.states[self.current_state]
            pixmap = QtGui.QPixmap(current_state["image"])
            pixmap = scale_pixmap(pixmap, self.width(), self.height())
            self.image_label.setPixmap(pixmap)
            self.image_label.resize(self.width(), self.height())
        super().resizeEvent(event)
# -*- coding: utf-8 -*-
"""
电源窗口模块 - PowerWindow 类
"""

from .base import QtWidgets, QtGui, QtCore, scale_pixmap


class PowerWindow(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.is_on = False
        self.power_image_on = "qrc/电源-开.png"
        self.power_image_off = "qrc/电源-关.png"
        self.main_image_on = "qrc/F-O.png"
        self.main_image_off = "qrc/F-C.png"
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Power Window')
        self.setFixedSize(800, 450)

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setGeometry(0, 0, 800, 450)
        self.image_label.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        pixmap = QtGui.QPixmap(self.power_image_off)
        pixmap = scale_pixmap(pixmap, 800, 450)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        self.toggle_button = QtWidgets.QPushButton("", self)
        self.toggle_button.setGeometry(500, 300, 45, 45)
        self.toggle_button.setStyleSheet("background-color: rgba(0, 0, 0,0);")
        self.toggle_button.clicked.connect(self.toggle_images)

    def toggle_images(self):
        if self.is_on:
            self.is_on = False
            self.update_power_image(self.power_image_off)
            if self.main_window.newton_state == 'T':
                self.main_window.update_main_image("qrc/T-C.png")
            else:
                self.main_window.update_main_image(self.main_image_off)
            # 关闭电源时重置任务1
            self.main_window.update_task_style(0, False)
        else:
            self.is_on = True
            self.update_power_image(self.power_image_on)
            if self.main_window.newton_state == 'T':
                self.main_window.update_main_image("qrc/T-O.png")
            else:
                self.main_window.update_main_image(self.main_image_on)
            # 打开电源时完成任务1
            self.main_window.update_task_style(0, True)

    def update_power_image(self, image_path):
        pixmap = QtGui.QPixmap(image_path)
        pixmap = scale_pixmap(pixmap, self.image_label.width(), self.image_label.height())
        self.image_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        if hasattr(self, 'image_label') and self.image_label:
            pixmap = QtGui.QPixmap(self.power_image_on if self.is_on else self.power_image_off)
            pixmap = scale_pixmap(pixmap, self.width(), self.height())
            self.image_label.setPixmap(pixmap)
            self.image_label.resize(self.width(), self.height())
        super().resizeEvent(event)
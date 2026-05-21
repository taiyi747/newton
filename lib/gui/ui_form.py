# -*- coding: utf-8 -*-
"""
UI表单模块 - Ui_Form 类
"""

from .base import QtWidgets, QtCore, scale_pixmap,QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1920, 1080)
        self.yiqi = QtWidgets.QLabel(Form)
        self.yiqi.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.yiqi.setText("")
        pixmap = QtGui.QPixmap("qrc/F-C.png")
        pixmap = scale_pixmap(pixmap, 1920, 1080)
        self.yiqi.setPixmap(pixmap)
        self.yiqi.setScaledContents(True)
        self.yiqi.setObjectName("yiqi")
        self.dy_Button = QtWidgets.QPushButton(Form)
        self.dy_Button.setGeometry(QtCore.QRect(1400, 590, 431, 341))
        self.dy_Button.setStyleSheet("background-color: rgba(255, 255, 255,0);")
        self.dy_Button.setText("")
        self.dy_Button.setObjectName("dy_Button")
        self.ndh_Button = QtWidgets.QPushButton(Form)
        self.ndh_Button.setGeometry(QtCore.QRect(700, 970, 151, 71))
        self.ndh_Button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.ndh_Button.setText("")
        self.ndh_Button.setObjectName("ndh_Button")
        self.fsj_Button = QtWidgets.QPushButton(Form)
        self.fsj_Button.setGeometry(QtCore.QRect(540, 620, 61, 91))
        self.fsj_Button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.fsj_Button.setText("")
        self.fsj_Button.setObjectName("fsj_Button")
        self.mj_Button = QtWidgets.QPushButton(Form)
        self.mj_Button.setGeometry(QtCore.QRect(284, 60, 131, 151))
        self.mj_Button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.mj_Button.setText("")
        self.mj_Button.setObjectName("mj_Button")


        # 任务框 - 右上角
        self.task_frame = QtWidgets.QFrame(Form)
        self.task_frame.setGeometry(QtCore.QRect(1600, 20, 280, 240))
        self.task_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 128, 128, 0.7);
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.task_frame.setObjectName("task_frame")

        # 任务标题
        self.task_title = QtWidgets.QLabel(self.task_frame)
        self.task_title.setGeometry(QtCore.QRect(10, 10, 260, 30))
        self.task_title.setText("实验操作步骤")
        self.task_title.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background-color: transparent;
            border: none;
        """)
        self.task_title.setAlignment(QtCore.Qt.AlignCenter)

        # 任务步骤
        self.task_steps = []
        task_texts = [
            "1. 打开钠光灯电源",
            "2. 调整反射镜至45°",
            "3. 放置牛顿环",
            "4. 目镜调焦",
            "5. 物镜调焦",
            "6. 记录实验数据"
        ]
        for i, text in enumerate(task_texts):
            step_label = QtWidgets.QLabel(self.task_frame)
            step_label.setGeometry(QtCore.QRect(15, 50 + i * 30, 250, 26))
            step_label.setText(text)
            step_label.setStyleSheet("""
                color: #333;
                font-size: 13px;
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #ccc;
            """)
            step_label.setObjectName(f"task_step_{i}")
            self.task_steps.append(step_label)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.dy_Button.setToolTip(_translate("Form", "电力"))
        self.ndh_Button.setToolTip(_translate("Form", "牛顿环"))
        self.fsj_Button.setToolTip(_translate("Form", "反射镜"))
        self.mj_Button.setToolTip(_translate("Form", "目镜"))
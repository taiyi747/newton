# -*- coding: utf-8 -*-
"""
数据窗口模块 - DataWindow 类
"""

from .base import QtWidgets, QtCore, QWidget, QPushButton
import csv


class DataWindow(QWidget):
    def __init__(self, main_window, scale_window):
        super().__init__()
        self.main_window = main_window
        self.scale_window = scale_window  # 添加刻度窗口引用
        self.initUI()

    def initUI(self):
        self.setWindowTitle('数据窗口')
        self.setGeometry(100, 100, 800, 600)

        # 创建表格
        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(10, 10, 780, 500)
        self.table.setColumnCount(9)  # 8个级次 + 1个左右标识列
        self.table.setRowCount(2)     # 2行（左、右）

        # 设置表头
        self.table.setHorizontalHeaderLabels([''] + [f'{level}' for level in [40, 35, 30, 25, 20, 15, 10, 5]])
        self.table.setVerticalHeaderLabels(['Left', 'Right'])

        # 设置单元格只读
        for row in range(2):
            for col in range(9):
                if row == 0 and col == 0:
                    item = QtWidgets.QTableWidgetItem('Left')
                elif row == 1 and col == 0:
                    item = QtWidgets.QTableWidgetItem('Right')
                else:
                    item = QtWidgets.QTableWidgetItem('')
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

        # 为每个单元格添加输入框
        self.input_boxes = {}
        for row in range(2):
            for col in range(1, 9):
                level = [40, 35, 30, 25, 20, 15, 10, 5][col - 1]
                key = ('Left', level) if row == 0 else ('Right', level)
                input_box = QtWidgets.QLineEdit(self.table)
                input_box.setPlaceholderText(f"手动输入数据")
                self.table.setCellWidget(row, col, input_box)
                self.input_boxes[key] = input_box

        # 保存到本地文件按钮
        self.save_to_file_button = QPushButton('保存到本地文件', self)
        self.save_to_file_button.setGeometry(10, 520, 780, 60)
        self.save_to_file_button.clicked.connect(self.save_data_to_file)

    def save_data_to_file(self):
        try:
            # 收集所有数据
            data = []
            headers = [' ', '40', '35', '30', '25', '20', '15', '10', '5']

            # 左数据
            left_row = ['Left']
            for level in [40, 35, 30, 25, 20, 15, 10, 5]:
                key = ('Left', level)
                text = self.input_boxes[key].text()
                left_row.append(text if text else '')
            data.append(left_row)

            # 右数据
            right_row = ['Right']
            for level in [40, 35, 30, 25, 20, 15, 10, 5]:
                key = ('Right', level)
                text = self.input_boxes[key].text()
                right_row.append(text if text else '')
            data.append(right_row)

            # 打开文件对话框以选择保存路径
            options = QtWidgets.QFileDialog.Options()
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "保存数据到文件", "", "CSV 文件 (*.csv);;所有文件 (*)", options=options
            )

            if file_name:
                # 确保文件以.csv结尾
                if not file_name.endswith('.csv'):
                    file_name += '.csv'

                # 将数据写入CSV文件
                with open(file_name, 'w', encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)
                    writer.writerows(data)

                print(f"数据已保存到 {file_name}")
                # 数据保存成功，完成任务6
                self.main_window.update_task_style(5, True)
        except Exception as e:
            # 捕获异常并显示错误信息
            error_message = f"保存数据时出错: {str(e)}"
            QtWidgets.QMessageBox.critical(self, "错误", error_message)
            print(error_message)
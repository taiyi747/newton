# -*- coding: utf-8 -*-
"""
前后端通信处理器 - BridgeHandler 类
"""

import json
import os
import base64
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


# 延迟导入，从 main.py 传递
AI_AVAILABLE = False
LIB_DIR = ""


def _init_globals(ai_available, lib_dir):
    """初始化全局变量（由 main.py 调用）"""
    global AI_AVAILABLE, LIB_DIR
    AI_AVAILABLE = ai_available
    LIB_DIR = lib_dir


class BridgeHandler(QObject):
    """前后端通信处理器"""

    # 信号：用于向前端发送数据
    resultReady = pyqtSignal(str, str)  # (callback_id, result_json)
    simulationOpened = pyqtSignal()  # 仿真窗口打开信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = None
        self._active_streams = {}  # 存储活动的流处理器

    @pyqtSlot(str, str, str, result=str)
    def callBackend(self, method, params_json, callback_id):
        """
        前端调用后端的入口
        method: API方法名
        params_json: JSON格式的参数字符串
        callback_id: 回调ID，用于前端匹配响应
        """
        # 延迟导入 call_api
        from bridge import call_api

        try:
            params = json.loads(params_json) if params_json else {}

            # 处理AI相关的特殊方法
            if method == 'ai_chat_stream_start':
                result = self._handle_ai_stream_start(params, callback_id)
            elif method == 'ai_chat_stream_chunk':
                result = self._handle_ai_stream_chunk(params)
            elif method == 'ai_stop_stream':
                result = self._handle_ai_stop_stream(params)
            elif method == 'ai_clear_history':
                result = self._handle_ai_clear_history()
            else:
                # 其他普通API调用
                result = call_api(method, params)

            self.resultReady.emit(callback_id, result)
            return result
        except Exception as e:
            error_result = json.dumps({"success": False, "error": str(e)})
            self.resultReady.emit(callback_id, error_result)
            return error_result

    def _handle_ai_stream_start(self, params, callback_id):
        """处理AI流式对话启动"""
        from ai_module import create_stream

        print(f"\n[Run.py调试] _handle_ai_stream_start 被调用")
        print(f"[Run.py调试] 接收到的 params: {params}")

        if not AI_AVAILABLE:
            print(f"[Run.py调试] AI模块未加载!")
            return json.dumps({"success": False, "error": "AI模块未加载"})

        try:
            message = params.get('message', '')
            stream_id = params.get('stream_id', 'default')
            print(f"[Run.py调试] message: {repr(message)}")
            print(f"[Run.py调试] stream_id: {stream_id}")

            # 创建流处理器
            handler = create_stream(stream_id)
            self._active_streams[stream_id] = handler

            # 启动流式对话（在后台线程）
            def on_chunk(chunk):
                pass

            def on_complete():
                pass

            handler.start_stream(message, on_chunk, on_complete)

            return json.dumps({"success": True})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    def _handle_ai_stream_chunk(self, params):
        """获取AI流式数据块"""
        from ai_module import get_streaming_handler

        if not AI_AVAILABLE:
            return json.dumps({"success": False, "error": "AI模块未加载", "chunk": "", "done": True})

        try:
            stream_id = params.get('stream_id', 'default')
            handler = get_streaming_handler(stream_id)

            chunk = handler.get_next_chunk()
            done = handler.check_done()

            if chunk:
                print(f"[Run.py调试] _handle_ai_stream_chunk 返回 chunk (长度={len(chunk)})")
            if done:
                print(f"[Run.py调试] _handle_ai_stream_chunk 返回 done=True")

            return json.dumps({
                "success": True,
                "chunk": chunk,
                "done": done
            })
        except Exception as e:
            print(f"[Run.py调试] _handle_ai_stream_chunk 错误: {str(e)}")
            return json.dumps({"success": False, "error": str(e), "chunk": "", "done": True})

    def _handle_ai_stop_stream(self, params):
        """停止AI流式对话"""
        from ai_module import remove_stream

        if not AI_AVAILABLE:
            return json.dumps({"success": False, "error": "AI模块未加载"})

        try:
            stream_id = params.get('stream_id', 'default')
            if stream_id in self._active_streams:
                self._active_streams[stream_id].stop()
                del self._active_streams[stream_id]
            remove_stream(stream_id)
            return json.dumps({"success": True})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    def _handle_ai_clear_history(self):
        """清空AI对话历史"""
        from ai_module import clear_ai_history

        if not AI_AVAILABLE:
            return json.dumps({"success": False, "error": "AI模块未加载"})

        try:
            clear_ai_history()
            return json.dumps({"success": True})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(result=str)
    def openSimulation(self):
        """打开仿真实验窗口"""
        if self.main_window:
            self.main_window.open_simulation()
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "主窗口未初始化"})

    @pyqtSlot(result=str)
    def exitApp(self):
        """退出应用程序"""
        if self.main_window:
            self.main_window.close()
        return json.dumps({"success": True})

    @pyqtSlot(result=str)
    def minimizeWindow(self):
        """最小化窗口"""
        if self.main_window:
            self.main_window.showMinimized()
        return json.dumps({"success": True})

    @pyqtSlot(result=str)
    def toggleMaximizeWindow(self):
        """最大化/还原窗口"""
        if self.main_window:
            self.main_window.toggle_maximize()
        return json.dumps({"success": True})

    @pyqtSlot(result=bool)
    def isWindowMaximized(self):
        """检查窗口是否已最大化"""
        if self.main_window:
            return self.main_window.isMaximized()
        return False

    @pyqtSlot(str, str, result=str)
    def saveImage(self, base64_data, default_filename):
        """
        保存图像到用户选择的位置
        base64_data: base64编码的图像数据（包含data:image/png;base64,前缀）
        default_filename: 默认文件名
        """
        from PyQt5.QtWidgets import QFileDialog

        try:
            # 弹出保存文件对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "保存图像",
                default_filename,
                "图像文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*.*)"
            )

            if not file_path:
                return json.dumps({"success": False, "cancelled": True, "message": "用户取消保存"})

            # 从base64数据中提取实际图像数据
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            # 解码并保存
            image_data = base64.b64decode(base64_data)
            with open(file_path, 'wb') as f:
                f.write(image_data)

            return json.dumps({"success": True, "path": file_path})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(str, result=str)
    def getSetting(self, params_json=None):
        """读取setting文件中的advanced配置"""
        try:
            setting_file = os.path.join(LIB_DIR, 'setting')
            if os.path.exists(setting_file):
                with open(setting_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # 解析 key = value 格式
                    if '=' in content:
                        key, value = content.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key == 'advanced':
                            return json.dumps({"success": True, "advanced": int(value)})
            return json.dumps({"success": True, "advanced": 0})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "advanced": 0})

    @pyqtSlot(result=str)
    def getVersion(self):
        """获取版本信息"""
        return json.dumps({"version": "1.0.0", "name": "牛顿环综合实验平台"})

    @pyqtSlot(str, result=str)
    def loadPdf(self, pdf_name):
        """
        加载PDF文件并转换为base64图片（所有页面）
        pdf_name: 'ndcz' 或 'ndsm'
        """
        try:
            try:
                import fitz  # PyMuPDF
            except ImportError:
                return json.dumps({"success": False, "error": "缺少PyMuPDF库，请运行: pip install PyMuPDF==1.23.5"})

            # 构建PDF文件路径
            pdf_path = os.path.join(LIB_DIR, f'{pdf_name}.pdf')
            if not os.path.exists(pdf_path):
                return json.dumps({"success": False, "error": f"PDF文件不存在: {pdf_name}.pdf"})

            # 打开PDF文件
            doc = fitz.open(pdf_path)
            total_pages = len(doc)

            # 渲染所有页面为图片
            pages_base64 = []
            for page_num in range(total_pages):
                page = doc[page_num]
                # 设置缩放比例以获得清晰的图片
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)

                # 转换为PNG并base64编码
                img_data = pix.tobytes("png")
                base64_data = base64.b64encode(img_data).decode('utf-8')
                pages_base64.append(f"data:image/png;base64,{base64_data}")

            doc.close()

            return json.dumps({
                "success": True,
                "pages": pages_base64,
                "total_pages": total_pages
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(result=str)
    def saveTemplate(self):
        """
        保存数据模板文件到用户选择的位置
        从 lib/template.csv 读取并弹出保存对话框
        """
        from PyQt5.QtWidgets import QFileDialog

        try:
            # 读取模板文件
            template_path = os.path.join(LIB_DIR, 'template.csv')
            if not os.path.exists(template_path):
                return json.dumps({"success": False, "error": "模板文件不存在"})

            # 弹出保存文件对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "保存模板文件",
                "牛顿环数据模板.csv",
                "CSV文件 (*.csv);;所有文件 (*.*)"
            )

            if not file_path:
                return json.dumps({"success": False, "cancelled": True, "message": "用户取消保存"})

            # 复制模板文件到用户选择的位置
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)

            return json.dumps({"success": True, "path": file_path})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
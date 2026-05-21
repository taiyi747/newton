#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手模块 - 接入DeepSeek模型 (使用OpenAI SDK)
支持流式传输，由AI自行判断是否回答

请确保已安装OpenAI SDK: pip install openai

官方文档: https://api-docs.deepseek.com/
"""

import os
import threading
from typing import Generator, Callable, Optional

# DeepSeek API配置 - 优先从环境变量读取
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', "sk-f2863fb2d2d34ce7b0ce9cc68e8fec99")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 尝试导入OpenAI SDK
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("警告: 未安装OpenAI SDK，请运行: pip install openai")


# 系统提示词 - 由AI自行判断是否回答，禁止Markdown格式
SYSTEM_PROMPT = """你是一个专业的物理实验助手，主要帮助用户解答牛顿环实验及物理学相关问题。

你的核心职责：
1. 详细解释牛顿环实验的物理原理，包括薄膜干涉、光程差、半波损失等概念
2. 指导实验操作步骤，帮助用户正确进行实验
3. 协助分析实验数据，包括数据处理方法、误差分析等
4. 解答物理公式推导和计算问题
5. 解释各种实验参数（波长、曲率半径、折射率等）对实验结果的影响
6. 回答其他物理学领域的问题（力学、电磁学、热学、量子力学等）
7. 回答相关数学问题（微积分、线性代数、微分方程等）

回答风格：
- 专业、准确、易懂
- 适合大学生物理实验水平
- 使用中文回答
- 如果问题比较复杂，可以分步骤解释
- 禁止使用Markdown格式（如**粗体**、*斜体*、###标题、```代码块等），使用纯文本格式
- 使用自然段落和序号（1. 2. 3.）来组织内容
- 公式使用简单的文本表示，如用"λ"表示波长，不要用LaTeX格式

判断规则：
- 如果问题是关于物理、光学、牛顿环、数学、科学相关的问题，请正常回答
- 如果问题与物理实验明显无关（如天气、娱乐八卦、个人情感、商业广告等），请礼貌地引导用户回到物理话题

示例回答格式：
牛顿环是一种薄膜干涉现象。其原理是：当单色光垂直照射到平凸透镜与平面玻璃之间的空气薄膜时，会在薄膜上下表面分别反射，这两束反射光发生干涉，形成明暗相间的环形条纹。

1. 核心结构：平凸透镜+平面玻璃
2. 干涉条件：光程差等于波长的整数倍或半整数倍
3. 条纹特点：中心为暗斑，向外逐渐变密

请问还有什么想了解的吗？
"""


class DeepSeekAI:
    """DeepSeek AI助手类 (使用OpenAI SDK)"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化AI助手
        
        Args:
            api_key: DeepSeek API密钥，如果为None则使用默认配置
        """
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.conversation_history = []
        self.max_history = 10  # 保留最近10轮对话
        self._client = None  # OpenAI客户端实例
        
    def _get_client(self):
        """获取或创建OpenAI客户端"""
        if not OPENAI_AVAILABLE:
            raise ImportError("请安装OpenAI SDK: pip install openai")
        
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=DEEPSEEK_BASE_URL
            )
        return self._client
        
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
        self._client = None  # 重置客户端，下次使用时重新创建
        
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def _prepare_messages(self, user_message: str) -> list:
        """准备消息列表，包含系统提示和历史记录"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages
    
    def _update_history(self, user_message: str, assistant_message: str):
        """更新对话历史"""
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        # 只保留最近的几轮对话
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def chat_stream(self, message: str) -> Generator[str, None, None]:
        """
        流式对话 - 直接发送给AI，由AI自行判断是否回答
        
        Args:
            message: 用户消息
            
        Yields:
            str: 流式返回的文本片段
        """
        # ========== 调试打印：AI模块接收到的消息 ==========
        print(f"\n[AI模块调试] chat_stream 被调用")
        print(f"[AI模块调试] 接收到的 message: {repr(message)}")
        print(f"[AI模块调试] API密钥状态: {'已配置' if self.api_key and self.api_key != 'sk-' else '未配置'}")
        # =============================================
        
        # 检查API密钥
        if not self.api_key or self.api_key == "sk-":
            print(f"[AI模块调试] 错误：未配置DeepSeek API密钥")
            yield "错误：未配置DeepSeek API密钥。"
            return
        
        # 检查OpenAI SDK是否可用
        if not OPENAI_AVAILABLE:
            print(f"[AI模块调试] 错误：未安装OpenAI SDK")
            yield "错误：未安装OpenAI SDK。请运行: pip install openai"
            return
        
        try:
            client = self._get_client()
            messages = self._prepare_messages(message)
            print(f"[AI模块调试] 准备发送API请求, messages数量: {len(messages)}")
            
            # 创建流式响应
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True
            )
            
            # 收集完整响应
            full_response = []
            chunk_count = 0
            
            # 处理流式响应
            print(f"[AI模块调试] 开始接收流式响应...")
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    chunk_count += 1
                    full_response.append(content)
                    yield content
            
            print(f"[AI模块调试] 流式响应完成, 共接收 {chunk_count} 个chunk")
            
            # 更新对话历史
            if full_response:
                full_text = "".join(full_response)
                print(f"[AI模块调试] 完整响应长度: {len(full_text)} 字符")
                self._update_history(message, full_text)
            else:
                print(f"[AI模块调试] 警告: 未收到任何响应内容")
                
        except Exception as e:
            print(f"[AI模块调试] API请求失败: {str(e)}")
            yield f"错误：API请求失败 - {str(e)}"
    
    def chat(self, message: str) -> str:
        """
        非流式对话，返回完整响应
        
        Args:
            message: 用户消息
            
        Returns:
            str: 完整的AI回复
        """
        # 检查OpenAI SDK是否可用
        if not OPENAI_AVAILABLE:
            return "错误：未安装OpenAI SDK。请运行: pip install openai"
        
        # 检查API密钥
        if not self.api_key or self.api_key == "sk-":
            return "错误：未配置DeepSeek API密钥。"
        
        try:
            client = self._get_client()
            messages = self._prepare_messages(message)
            
            # 使用官方SDK方法
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
            )
            
            # 获取完整响应
            content = response.choices[0].message.content
            
            # 更新对话历史
            self._update_history(message, content)
            
            return content
            
        except Exception as e:
            return f"错误：API请求失败 - {str(e)}"


def test_connection():
    """
    测试DeepSeek API连接
    
    Returns:
        bool: 连接是否成功
    """
    if not OPENAI_AVAILABLE:
        print("Error: OpenAI SDK not installed")
        return False
    
    try:
        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY', DEEPSEEK_API_KEY),
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
            ],
            stream=False
        )
        
        print("API connection test successful!")
        content = response.choices[0].message.content
        print(f"Response: {content}")
        return True
        
    except Exception as e:
        print(f"API connection test failed: {str(e)}")
        return False


def test_streaming():
    """
    测试DeepSeek API流式传输
    
    Returns:
        bool: 测试是否成功
    """
    if not OPENAI_AVAILABLE:
        print("Error: OpenAI SDK not installed")
        return False
    
    try:
        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY', DEEPSEEK_API_KEY),
            base_url="https://api.deepseek.com"
        )
        
        print("Testing streaming API...")
        
        # 流式调用
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "请用一句话介绍牛顿环实验"},
            ],
            stream=True
        )
        
        print("Streaming response: ", end="", flush=True)
        full_content = []
        
        # 处理流式响应
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                full_content.append(content)
        
        print("\n\nStreaming test completed!")
        return True
        
    except Exception as e:
        print(f"Streaming test failed: {str(e)}")
        return False


# 全局AI实例（单例模式）
_ai_instance = None


def get_ai_instance() -> DeepSeekAI:
    """获取全局AI实例"""
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = DeepSeekAI()
    return _ai_instance


def reset_ai_instance():
    """重置AI实例"""
    global _ai_instance
    _ai_instance = None


# 便捷的API函数
def ai_chat(message: str) -> str:
    """
    便捷的AI对话函数（非流式）
    
    Args:
        message: 用户消息
        
    Returns:
        str: AI回复
    """
    ai = get_ai_instance()
    return ai.chat(message)


def ai_chat_stream(message: str) -> Generator[str, None, None]:
    """
    便捷的AI流式对话函数
    
    Args:
        message: 用户消息
        
    Yields:
        str: 流式返回的文本片段
    """
    ai = get_ai_instance()
    yield from ai.chat_stream(message)


def clear_ai_history():
    """清空AI对话历史"""
    ai = get_ai_instance()
    ai.clear_history()


def set_ai_api_key(api_key: str):
    """设置AI的API密钥"""
    ai = get_ai_instance()
    ai.set_api_key(api_key)


# 用于后台线程的流式处理类
class StreamingAIHandler:
    """处理流式AI响应的后台线程处理器"""
    
    def __init__(self, stream_id: str = None):
        self.stream_id = stream_id
        self.is_running = False
        self._is_done = False
        self.current_thread = None
        self.response_buffer = []
        self.chunk_queue = []  # 用于轮询的队列
        self.lock = threading.Lock()
        
    def start_stream(self, message: str, on_chunk: Callable[[str], None] = None, on_complete: Callable[[], None] = None):
        """
        在后台线程开始流式对话
        
        Args:
            message: 用户消息
            on_chunk: 收到文本片段时的回调函数（可选）
            on_complete: 流式传输完成时的回调函数（可选）
        """
        # ========== 调试打印：StreamingAIHandler ==========
        print(f"\n[StreamingHandler调试] start_stream 被调用")
        print(f"[StreamingHandler调试] stream_id: {self.stream_id}")
        print(f"[StreamingHandler调试] message: {repr(message)}")
        print(f"[StreamingHandler调试] 当前运行状态 is_running: {self.is_running}")
        # =============================================
        
        if self.is_running:
            print(f"[StreamingHandler调试] 已经在运行中，直接返回")
            return
            
        self.is_running = True
        self._is_done = False
        self.response_buffer = []
        self.chunk_queue = []
        
        def stream_worker():
            print(f"[StreamingHandler调试] stream_worker 线程启动")
            chunk_count = 0
            try:
                ai = get_ai_instance()
                for chunk in ai.chat_stream(message):
                    chunk_count += 1
                    with self.lock:
                        self.response_buffer.append(chunk)
                        self.chunk_queue.append(chunk)
                    if on_chunk:
                        on_chunk(chunk)
                print(f"[StreamingHandler调试] stream_worker 接收到 {chunk_count} 个chunk")
            except Exception as e:
                print(f"[StreamingHandler调试] stream_worker 异常: {str(e)}")
            finally:
                self.is_running = False
                self._is_done = True
                print(f"[StreamingHandler调试] stream_worker 完成, _is_done={self._is_done}")
                if on_complete:
                    on_complete()
        
        self.current_thread = threading.Thread(target=stream_worker, daemon=True)
        self.current_thread.start()
        print(f"[StreamingHandler调试] 后台线程已启动")
    
    def stop(self):
        """停止当前的流式传输"""
        print(f"[StreamingHandler调试] stop 被调用")
        self.is_running = False
        
    def get_next_chunk(self) -> str:
        """获取下一个文本块（轮询方式）"""
        with self.lock:
            if self.chunk_queue:
                chunk = self.chunk_queue.pop(0)
                # 只在非空时打印，避免刷屏
                # print(f"[StreamingHandler调试] get_next_chunk 返回 chunk (长度={len(chunk)})")
                return chunk
            return ""
    
    def check_done(self) -> bool:
        """检查流式传输是否完成"""
        return self._is_done
    
    def get_full_response(self) -> str:
        """获取当前缓冲区的完整响应"""
        with self.lock:
            return "".join(self.response_buffer)


# 活动流处理器字典（用于多流管理）
active_streams = {}


def create_stream(stream_id: str) -> StreamingAIHandler:
    """创建一个新的流处理器"""
    handler = StreamingAIHandler(stream_id)
    active_streams[stream_id] = handler
    return handler


def get_streaming_handler(stream_id: str = None) -> StreamingAIHandler:
    """
    获取流式处理器实例
    
    Args:
        stream_id: 流ID，如果提供则返回对应的处理器，否则返回全局处理器
    """
    if stream_id and stream_id in active_streams:
        return active_streams[stream_id]
    
    # 如果没有找到，创建一个新的
    if stream_id:
        return create_stream(stream_id)
    
    # 返回全局处理器
    global _streaming_handler
    if _streaming_handler is None:
        _streaming_handler = StreamingAIHandler()
    return _streaming_handler


def remove_stream(stream_id: str):
    """移除流处理器"""
    if stream_id in active_streams:
        del active_streams[stream_id]


# 创建全局流式处理器实例
_streaming_handler = None


# 简单的命令行测试入口
if __name__ == "__main__":
    print("=" * 50)
    print("DeepSeek AI 模块测试")
    print("=" * 50)
    
    # 测试非流式API
    print("\n1. 测试非流式API连接...")
    if test_connection():
        print("\n2. 测试流式API...")
        test_streaming()
        
        print("\n3. 测试AI助手类...")
        ai = DeepSeekAI()
        
        # 测试物理相关问题
        print("\n提问: 牛顿环是什么？")
        print("回答: ", end="", flush=True)
        for chunk in ai.chat_stream("牛顿环是什么？"):
            print(chunk, end="", flush=True)
        print("\n")
    else:
        print("\nAPI连接测试失败，请检查：")
        print("1. 是否已安装OpenAI SDK: pip install openai")
        print("2. API密钥是否正确")
        print("3. 网络连接是否正常")
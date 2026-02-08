import sys
import os
import time
import asyncio
import threading
import rclpy
from rclpy.node import Node

from src.lingdong_msgs.proto.AudioResult_pb2 import AudioResult
from lingdong_msgs.msg import AudioResult as AudioResultMsg
from modules.audio.audio import ASRClient

class LingDongAudioNode(Node):
    def __init__(self):
        super().__init__('audio_node')
        
        self.logger = self.get_logger()
        # --- 状态管理 ---
        self.is_active = False           # 当前是否处于“应当响应”状态
        self.last_active_time = 0        # 上次活跃时间戳
        self.session_timeout = 10.0      # 持续响应窗口期（秒）
        self.wake_word = "灵动"           # 唤醒词
        
        self.current_session_text = ""   # 存储从唤醒开始的所有内容
        self.last_text = ""              # 用于 ASR 实时刷新的缓存
        
        # 1. 只有在有 ROS 的环境下才创建发布者
        self.publisher_ = None
        self.publisher_ = self.create_publisher(
            AudioResultMsg, 
            '/lingdong/perception/speech_result', 
            10
        )
        self.publisher_active_ = self.create_publisher(
            AudioResultMsg, 
            '/lingdong/perception/speech_active', 
            10
        )
        self.publisher_recorder_ = self.create_publisher(
            AudioResultMsg, 
            '/lingdong/perception/speech_record', 
            10
        )
        self.logger.info("📡 ROS2 Publisher initialized.")

        # 2. 实例化 ASR 客户端 (uri 可以根据需要修改)
        # 建议小车上使用 container 内部域名或 IP
        self.asr_client = ASRClient(uri="ws://localhost:10095")
        
        # 3. 在独立线程中运行异步 ASR
        self.asr_thread = threading.Thread(target=self._run_asr, daemon=True)
        self.asr_thread.start()
        
        self.logger.info("🚀 LingDong Audio Node with ASR is ready!")

    def get_trigger_reason(self, text):
        """
        核心判定逻辑：决定当前句子是否属于“对话”的一部分
        """
        # 状态 A: 关键词命中（强触发）
        if self.wake_word in text:
            return "WAKE_WORD_HIT"

        # 状态 B: 持续对话中（窗口期触发）
        current_time = time.time()
        if self.is_active and (current_time - self.last_active_time < self.session_timeout):
            # 这里可以进一步扩展：如果有大模型接入，可以将 text 发给大模型
            # 若大模型返回 "IGNORE"，则此处返回 None
            return "SESSION_CONTINUOUS"

        # 状态 C: 大模型语义触发（预留接口）
        # 比如：虽然没叫名字，但说了“快停下”或者“救命”，LLM判定需要响应
        if self.llm_judgement(text):
            return "LLM_INFERENCE_HIT"

        return None
    
    def llm_judgement(self, text):
        """
        预留接口：接入本地轻量化大模型或语义分析工具
        """
        # TODO: 接入类似 Qwen-1.8B 的判断逻辑
        # 目前先返回 False，后续可根据语义距离判断
        return False

    def _run_asr(self):
        """异步事件循环线程"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # 运行 ASR 客户端，并绑定回调函数
            loop.run_until_complete(self.asr_client.start(self.on_asr_result))
        except Exception as e:
            self.logger.error(f"ASR Thread Loop Error: {e}")

    # 修改回调函数接收两个参数
    async def on_asr_result(self, text, is_final):

        if self.wake_word in text:
            proto_msg = AudioResult()
            proto_msg.text = "active"
            proto_msg.confidence = 0.99
            proto_msg.timestamp = int(time.time())
            binary_data = proto_msg.SerializeToString() # 变成 bytes
            ros_msg = AudioResultMsg()
            # 注意：Python 的 bytes 直接赋值给 uint8[] 列表即可
            ros_msg.raw_proto_data = list(binary_data)

            self.publisher_active_.publish(ros_msg)
            self.logger.info('active immediately')

        if is_final:
            self.last_text = "" 
            proto_msg = AudioResult()
            proto_msg.text = text
            proto_msg.confidence = 0.99
            proto_msg.timestamp = int(time.time())
            binary_data = proto_msg.SerializeToString() # 变成 bytes
            ros_msg = AudioResultMsg()
            # 注意：Python 的 bytes 直接赋值给 uint8[] 列表即可
            ros_msg.raw_proto_data = list(binary_data)

            self.publisher_recorder_.publish(ros_msg)
            self.logger.info(f'📦 [FINAL RECORD]: {text}')

            reason = self.get_trigger_reason(text)
            # 1. 最终结果：发布到 ROS2，并换行打印
            if reason:
                if not self.is_active:
                    self.logger.info(f"\n✨ [Robot Awake]: 触发原因 -> {reason}")
                self.is_active = True
                self.last_active_time = time.time()

                self.publisher_.publish(ros_msg)
                self.logger.info(f"\n✅ [Final Result]: {text}")
            else:
                self.logger.info('Do not response')
        else:
            # 2. 中间过程：实现“蹦字”效果
            # 使用 \r 实现原地刷新，不换行
            if text != self.last_text:
                print(f"\r🎤 [Recognizing]: {text}", end="", flush=True)
                self.last_text = text

def main(args=None):
    rclpy.init(args=args)
    node = LingDongAudioNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.asr_client.stop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
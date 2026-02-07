import rclpy
from rclpy.node import Node
from std_msgs.msg import String  # 假设你使用标准字符串消息
# 如果你有自定义消息：from lingdong_msgs.msg import AudioResult

class LingDongAudioNode(Node):
    def __init__(self):
        super().__init__('audio_node')
        
        # 1. 定义发布者：将识别结果发给大脑 (LLM)
        self.publisher_ = self.create_publisher(String, '/lingdong/percept/speech_text', 10)
        
        # 2. 初始化 ASR 逻辑 (保持之前的异步结构)
        self.asr_client = AudioNode(uri="ws://localhost:10095")
        
        # 3. 启动异步循环
        self.get_logger().info("LingDong Audio Node has been started.")

    async def run(self):
        # 将我们之前的回调函数对接 ROS 发布者
        await self.asr_client.start_listening(self.publish_text)

    async def publish_text(self, text):
        msg = String()
        msg.data = text
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: "{text}"')
import sys
import time
import rclpy
from rclpy.node import Node

# ⚠️ 关键导入：必须同时包含 ROS 2 消息类和 Protobuf 类
from lingdong_msgs.msg import AudioResult as AudioResultMsg
from src.lingdong_msgs.proto.AudioResult_pb2 import AudioResult as AudioResultProto

class FeedbackNode(Node):
    def __init__(self):
        super().__init__('active_feedback_node')
        
        self.logger = self.get_logger()
        self.last_trigger_time = 0
        self.cooldown = 3.0  # 冷却时间（秒）
        
        # 创建订阅器：订阅透明传输的二进制话题
        self.subscription = self.create_subscription(
            AudioResultMsg, # 使用 ROS 2 消息类作为“壳”
            '/lingdong/perception/speech_record',
            self.listener_callback,
            10
        )
        print("📡 反馈节点已启动，正在监听 ASR 识别结果...")

    def listener_callback(self, ros_msg):
        """ROS2 订阅回调：在这里解包并打印文字"""
        try:
            # 1. 从 ROS 2 消息的 uint8 数组中解析出 Protobuf 对象
            proto_data = AudioResultProto()
            # 将 list 转换为 bytes 再进行反序列化
            proto_data.ParseFromString(bytes(ros_msg.raw_proto_data))

            # 2. 【核心打印】在这里看识别到的文字内容
            # 使用 logger.info 会带有时间戳和节点名，方便调试
            print(f"📥 接收到文字: \"{proto_data.text}\")")

            # 3. 逻辑触发判断
            # 方案 A：完全匹配关键词
            if proto_data.text == "active":
                self.execute_feedback()
            
            # 方案 B：模糊匹配（如果 ASR 只是原样转发语音）
            elif "灵动" in proto_data.text:
                self.logger.info("🎯 检测到唤醒词 '灵动'！")
                self.execute_feedback()

        except Exception as e:
            self.logger.error(f"❌ 解析数据失败: {e}")

    def execute_feedback(self):
        """执行硬件反馈动作"""
        current_time = time.time()
        if current_time - self.last_trigger_time < self.cooldown:
            return
        
        self.last_trigger_time = current_time
        self.logger.info("✨ [Action] 执行物理反馈：蓝灯闪烁 + 点头")
        
        # 终端视觉反馈
        print("\n" + "★"*40)
        print("🔥 [HARDWARE] 执行动作：🔵 蓝灯亮起 | 📐 舵机旋转")
        print("★"*40 + "\n")

def main(args=None):
    rclpy.init(args=args)
    node = FeedbackNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("🛑 节点正在关闭...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
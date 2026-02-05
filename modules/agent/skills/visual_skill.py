import os
from modules.brain.vlm.vlm_service import VLMService

class VisualSkill:
    def __init__(self, remote_brain_ip="100.88.159.2"):
        # 实际开发中，这里可以是通过网络发送图片，现在先假设图片已同步
        self.vlm = VLMService() 

    def look_and_describe(self):
        print("📸 小车正在拍照...")
        # 调用小车端的摄像头拍照命令 (示例)
        os.system("ffmpeg -f video4linux2 -i /dev/video0 -vframes 1 snapshot.jpg -y")
        
        print("🧠 正在发送给 Spirit Pro 进行视觉分析...")
        description = self.vlm.analyze_image("snapshot.jpg", "请简要描述你看到的内容，特别是障碍物。")
        return description
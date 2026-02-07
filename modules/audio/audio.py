import asyncio
import websockets
import json
import pyaudio
import numpy as np
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AudioNode")

class AudioNode:
    def __init__(self, uri="ws://localhost:10095", rate=16000, chunk_ms=100):
        self.uri = uri
        self.rate = rate
        self.chunk_size = int(rate * chunk_ms / 1000)
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False

    def _get_loopback_index(self):
        """寻找虚拟声卡索引，如果没有则返回 None 使用默认设备"""
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if "Loopback" in dev['name'] and dev['maxInputChannels'] > 0:
                return i
        return None

    async def start_listening(self, callback):
        """
        开始监听并识别
        :param callback: 这是一个函数，当识别到最终结果时，会将文字传给它
        """
        self.is_running = True
        retry_delay = 2

        while self.is_running:
            try:
                async with websockets.connect(self.uri) as websocket:
                    logger.info("Successfully connected to ASR Server.")
                    
                    # 1. 发送配置
                    config = {
                        "mode": "2pass",
                        "chunk_size": [5, 10, 5],
                        "chunk_interval": 10,
                        "wav_name": "lingdong_mic",
                        "is_speaking": True,
                        "hotwords": "灵动 25"
                    }
                    await websocket.send(json.dumps(config))
                    await asyncio.sleep(0.3)

                    # 2. 打开音频流
                    loop_idx = self._get_loopback_index()
                    self.stream = self.p.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=self.rate,
                        input=True,
                        input_device_index=loop_idx,
                        frames_per_buffer=self.chunk_size
                    )

                    logger.info(f"Microphone started (Loopback Index: {loop_idx}). Listening...")

                    # 3. 数据传输循环
                    while self.is_running:
                        # 读取音频数据
                        data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                        await websocket.send(data)

                        # 尝试接收结果
                        try:
                            # 使用 short timeout 避免阻塞读取
                            res = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                            res_dict = json.loads(res)
                            
                            # 核心逻辑：只过滤出“最终修正”的结果给大脑
                            is_final = res_dict.get("mode") == "2pass-offline" or res_dict.get("is_final")
                            text = res_dict.get("text", "").strip()
                            
                            if text and is_final:
                                logger.info(f"ASR Final Result: {text}")
                                # 执行回调函数，把文字传给 planning 或 agent 模块
                                await callback(text)
                            elif text:
                                # 实时推测结果（可选，可以打印到控制台但不触发动作）
                                sys.stdout.write(f"\rIntermediate: {text}")
                                sys.stdout.flush()

                        except asyncio.TimeoutError:
                            continue

            except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError):
                logger.error(f"ASR Server disconnected. Retrying in {retry_delay}s...")
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                await asyncio.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(retry_delay)

    def stop(self):
        self.is_running = False
        if self.stream:
            self.stream.close()
        self.p.terminate()

# --- 模拟小车大脑的逻辑 ---
async def on_speech_recognized(text):
    """当听到声音后的处理逻辑"""
    print(f"\n[大脑接收] 正在解析指令: {text}")
    
    # 这里是简单的关键词路由，未来我们会对接 modules/brain/llm
    if "向前" in text:
        print(">>> 发送控制指令: [MOVE_FORWARD]")
    elif "停" in text:
        print(">>> 发送控制指令: [STOP_ENGINE]")
    elif "灵动" in text:
        print(">>> 灵动在！请吩咐。")

if __name__ == "__main__":
    node = AudioNode()
    try:
        asyncio.run(node.start_listening(on_speech_recognized))
    except KeyboardInterrupt:
        node.stop()
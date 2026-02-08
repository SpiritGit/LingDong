import asyncio
import websockets
import json
import pyaudio
import logging

logger = logging.getLogger("ASRClient")

class ASRClient:
    def __init__(self, uri="ws://localhost:10095", rate=16000, chunk_ms=60): # 减小 chunk_ms 提升灵敏度
        self.uri = uri
        self.rate = rate
        self.chunk_size = int(rate * chunk_ms / 1000)
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False

    async def start(self, callback):
        self.is_running = True
        while self.is_running:
            try:
                async with websockets.connect(self.uri, ping_interval=None) as ws:
                    # chunk_size [5, 10, 5] 对应的是 [左上下文, 当前块, 右上下文]
                    config = {
                        "mode": "2pass", 
                        "chunk_size": [5, 10, 5], 
                        "chunk_interval": 10,
                        "wav_name": "lingdong", 
                        "is_speaking": True, 
                        "hotwords": "灵动 25",
                        "itn": True # 开启 ITN，将“一二三”转为“123”
                    }
                    await ws.send(json.dumps(config))
                    
                    self.stream = self.p.open(
                        format=pyaudio.paInt16, channels=1, rate=self.rate,
                        input=True, frames_per_buffer=self.chunk_size
                    )
                    
                    while self.is_running:
                        data = await asyncio.to_thread(self.stream.read, self.chunk_size, False)
                        await ws.send(data)

                        try:
                            # 增大接收窗口，或者并发处理接收
                            res = await asyncio.wait_for(ws.recv(), timeout=0.005)
                            res_dict = json.loads(res)
                            
                            text = res_dict.get("text", "").strip()
                            mode = res_dict.get("mode") # '2pass-online' 或 '2pass-offline'
                            
                            if text:
                                # 将 text 和是否最终结果一起传回
                                is_final = (mode == "2pass-offline")
                                await callback(text, is_final)
                                
                        except asyncio.TimeoutError:
                            continue
            except Exception as e:
                logger.error(f"ASR Connection Error: {e}")
                await asyncio.sleep(2)

    def stop(self):
        self.is_running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
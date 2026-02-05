import base64
import requests

class VLMService:
    def __init__(self, model="llava"):
        self.url = "http://localhost:11434/api/generate"
        self.model = model

    def analyze_image(self, image_path, prompt="这张图片里有什么？"):
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [img_base64],
            "stream": False
        }
        
        try:
            response = requests.post(self.url, json=payload)
            return response.json().get("response")
        except Exception as e:
            return f"VLM推理失败: {e}"
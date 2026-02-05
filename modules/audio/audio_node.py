import speech_recognition as sr
import requests
import asyncio
import edge_tts
import os

# 1. 语音转文字 (STT)
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 听候指令中...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language='zh-CN')
        print(f"👂 我听到了: {text}")
        return text
    except:
        return None

# 2. 调用 Ollama (LLM) - 连到你的 Spirit Pro
def ask_ollama(prompt):
    url = "http://100.88.159.2:11434/api/generate" # 你的 Spirit Pro IP
    payload = {"model": "deepseek-r1:7b", "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.json().get("response")
    except Exception as e:
        return f"大脑连接失败: {e}"

# 3. 文字转语音 (TTS)
async def speak(text):
    print(f"🤖 小车说: {text}")
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await communicate.save("reply.mp3")
    os.system("mpg123 reply.mp3") # 需要 sudo apt install mpg123

async def main():
    while True:
        user_text = listen()
        if user_text:
            if "退出" in user_text: break
            answer = ask_ollama(user_text)
            await speak(answer)

if __name__ == "__main__":
    asyncio.run(main())
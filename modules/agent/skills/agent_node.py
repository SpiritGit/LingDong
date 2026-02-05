from modules.agent.skills.visual_skill import VisualSkill

class LingDongAgent:
    def __init__(self):
        self.visual_tool = VisualSkill()
        self.context = []

    def handle_command(self, user_input):
        # 简单的逻辑路由 (未来这里由 LLM 自动选择 Tool)
        if "看到" in user_input or "前面有什么" in user_input:
            result = self.visual_tool.look_and_describe()
            return f"报告主人，我‘看’到了：{result}"
        else:
            return "对不起，我还没学过这个技能。"

if __name__ == "__main__":
    agent = LingDongAgent()
    while True:
        cmd = input("👤 主人指令: ")
        response = agent.handle_command(cmd)
        print(f"🤖 灵动: {response}")
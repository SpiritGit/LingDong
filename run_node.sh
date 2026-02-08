#!/bin/bash

echo "🤖 [LingDong] 开始初始化机器人系统..."

# 1. 获取项目根目录
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_ROOT"

# 2. 检查并精准编译消息包
echo "🛠️  [Step 1/3] Syncing ROS 2 messages..."
colcon build --base-paths src --packages-select lingdong_msgs

# 加载 ROS 2 环境
source /opt/ros/humble/setup.bash
source install/setup.bash

# --- 3. 启动节点 ---
echo "🚀 [System] 正在启动各模块..."

# 4. 执行指定的 Bazel 目标
# $@ 会接收你运行脚本时跟在后面的所有参数
if [ $# -eq 0 ]; then
    echo "❓ Usage: ./ld_run.sh //modules/path:target"
    exit 1
fi

echo "🚀 [Step 2/3] Launching: $@"
echo "------------------------------------------"

# 将当前的 PYTHONPATH 强制注入 Bazel 运行环境
bazel run --action_env=PYTHONPATH=$PYTHONPATH $@
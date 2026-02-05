workspace(name = "lingdong")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# --- 1. 引入 Python 构建规则 (保持不变) ---
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
http_archive(
    name = "rules_python",
    sha256 = "841d1da97203303f87537651a134a415ea780b953d4567406c8273613a005085",
    strip_prefix = "rules_python-0.23.1",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.23.1/rules_python-0.23.1.tar.gz",
)

# --- 2. 注册特定版本的 Python 解释器 ---
load("@rules_python//python:repositories.bzl", "py_repositories", "python_register_toolchains")

py_repositories()

# 核心步骤：Bazel 会自动下载对应平台的 Python 解释器，不再依赖系统 /usr/bin/python
python_register_toolchains(
    name = "python3_10",
    python_version = "3.10.12", # 你也可以指定 3.11 等
)

load("@python3_10//:defs.bzl", "interpreter")

# --- 3. 自动安装 pip 依赖 (修改这里，绑定到上面的解释器) ---
load("@rules_python//python:pip.bzl", "pip_parse")

pip_parse(
   name = "py_deps",
   python_interpreter_target = interpreter, # 强制 pip 使用上面注册的 Python 版本
   requirements_lock = "//:requirements.txt",
)

load("@py_deps//:requirements.bzl", "install_deps")
install_deps()
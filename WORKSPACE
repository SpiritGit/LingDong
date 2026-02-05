workspace(name = "lingdong")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# --- 1. 引入 Python 构建规则 ---
http_archive(
    name = "rules_python",
    sha256 = "841d1da97203303f87537651a134a415ea780b953d4567406c8273613a005085",
    strip_prefix = "rules_python-0.23.1",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.23.1/rules_python-0.23.1.tar.gz",
)

load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()

# --- 2. 注册 Python 3 解释器 ---
# 这保证了无论系统自带什么版本，Bazel 都会用确定的版本编译
load("@rules_python//python:pip.bzl", "pip_parse")

# --- 3. 自动安装 pip 依赖 ---
pip_parse(
   name = "py_deps",
   requirements_lock = "//:requirements.txt",
)

load("@py_deps//:requirements.bzl", "install_deps")
install_deps()
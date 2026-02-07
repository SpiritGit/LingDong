load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "audio_lib",
    srcs = ["audio.py"],
    visibility = ["//visibility:public"],
    deps = [
        # 注意：这里的写法取决于 requirements.txt 里的包名
        # 规则通常是 @py_deps_包名//:pkg
        "@py_deps_websockets//:pkg",
        "@py_deps_pyaudio//:pkg",
        "@py_deps_numpy//:pkg",
    ],
)

py_binary(
    name = "audio_node",
    srcs = ["audio_node.py"],
    deps = [
        ":audio_lib",
        # 如果有消息定义，添加： "//src/lingdong_msgs:lingdong_msgs_py_proto",
    ],
)
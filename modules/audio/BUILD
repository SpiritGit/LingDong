load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "audio_lib",
    srcs = ["audio.py"],
    visibility = ["//visibility:public"],
    deps = [
        "@py_deps//websockets",
        "@py_deps//pyaudio",
        "@py_deps//numpy",
    ],
)

py_binary(
    name = "audio_node",
    srcs = ["audio_node.py"],
    deps = [
        ":audio_lib",
        "//src/lingdong_msgs:audio_result_py_proto",
    ],
)
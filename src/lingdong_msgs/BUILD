load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:proto.bzl", "py_proto_library")

package(default_visibility = ["//visibility:public"])

# 建议针对具体业务命名，方便以后扩展（比如加个 VisionResult.proto）
proto_library(
    name = "audio_result_proto",
    srcs = ["proto/AudioResult.proto"],
)

py_proto_library(
    name = "audio_result_py_proto",
    deps = [":audio_result_proto"],
)
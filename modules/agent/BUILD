py_binary(
    name = "agent_node",
    srcs = ["agent_node.py"],
    deps = [
        "@py_deps//requests", # 这里引用了 WORKSPACE 里定义的依赖
    ],
)

py_library(
    name = "visual_skill",
    srcs = ["skills/visual_skill.py"],
    deps = ["//modules/brain/vlm:vlm_service"],
)

py_binary(
    name = "agent_node",
    srcs = ["agent_node.py"],
    deps = [
        ":visual_skill",
    ],
)
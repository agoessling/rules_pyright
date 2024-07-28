py_binary(
    name = "hello_world",
    srcs = ["hello_world.py"],
    deps = [":lib"],
)

py_library(
    name = "lib",
    srcs = ["lib.py"],
    deps = ["@pip//numpy"],
)

load("@npm//:defs.bzl", "npm_link_all_packages")
load("@npm//:pyright/package_json.bzl", pyright = "bin")

npm_link_all_packages(name = "node_modules")

pyright.pyright_binary(
    name = "pyright",
    env = {"BAZEL_BINDIR": "."}, # Allow the binary to be run outside bazel
    visibility = ["//visibility:public"],
)

load("@bazel_skylib//lib:paths.bzl", "paths")
load("@bazel_skylib//lib:sets.bzl", "sets")

def _pyright_aspect_impl(target, ctx):
    if ctx.rule.kind not in ["py_binary", "py_library", "py_test"]:
        return []

    output = ctx.actions.declare_file(target.label.name + ".pyright.out")

    ctx.actions.run_shell(
        inputs = ctx.rule.files.srcs,
        outputs = [output],
        tools = [ctx.executable._pyright],
        arguments = [],
        mnemonic = "PyrightTypeCheck",
        command = "{} $@ && touch {}".format(ctx.executable._pyright.path, output.path),
    )

    return [
        OutputGroupInfo(
            pyright_output = depset([output]),
        )
    ]


def pyright_aspect(executable):
    return aspect(
        implementation = _pyright_aspect_impl,
        attrs = {
            "_pyright": attr.label(
                default = executable,
                allow_files = True,
                executable = True,
                cfg = "exec",
            ),
        },
    )

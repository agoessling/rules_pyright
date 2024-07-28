load("@bazel_skylib//lib:paths.bzl", "paths")
load("@bazel_skylib//lib:sets.bzl", "sets")

PyImportInfo = provider(
    fields = {
        'imports' : 'depset of imports'
    }
)

def _gen_config_aspect_impl(target, ctx):
    print(target)
    direct_imports = []
    transitive_imports = []
    if PyInfo in target:
        EXTERNAL_PATH = "bazel-out/../../../external"
        for imp in target[PyInfo].imports.to_list():
            direct_imports.append(paths.join(EXTERNAL_PATH, imp))

        for dep in ctx.rule.attr.deps:
            transitive_imports.append(dep[PyImportInfo].imports)

    return [PyImportInfo(imports = depset(direct = direct_imports, transitive = transitive_imports))]


gen_config_aspect = aspect(
    implementation = _gen_config_aspect_impl,
    attr_aspects = ["deps"],
    provides = [PyImportInfo],
)


def _update_pyright_config_impl(ctx):
    print(ctx)
    return []


update_pyright_config = rule(
    implementation = _update_pyright_config_impl,
    attrs = {
        "targets": attr.label_list(
            allow_empty = False,
            default = ["//..."],
            doc = "Targets used to define extra import paths.",
        ),
    },
    executable = True,
)

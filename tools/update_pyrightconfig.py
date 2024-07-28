import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Final

INCLUDES: Final = [
    '**/*.py',
]

EXCLUDES: Final = [
    'bazel-*',
]


def workspace_path() -> Path:
    '''Return path to bazel workspace.'''
    return Path(os.environ['BUILD_WORKSPACE_DIRECTORY'])


def main() -> None:
    '''Main function.'''
    parser = argparse.ArgumentParser(
        description='Create pyright config from bazel dependencies.')
    parser.add_argument(
        '--targets',
        nargs='+',
        default=['//...'],
        help='Bazel targets whose dependencies should be added.')
    parser.add_argument('--pyrightconfig',
                        default=workspace_path() / 'pyrightconfig.json',
                        type=Path,
                        help='Configuration file to update.')
    parser.add_argument('--includes',
                        nargs='*',
                        default=INCLUDES,
                        help='Entries to add to "includes".')
    parser.add_argument('--excludes',
                        nargs='*',
                        default=EXCLUDES,
                        help='Entries to add to "excludes".')

    args = parser.parse_args()

    targets: list[str] = args.targets
    config: Path = args.pyrightconfig

    if not config.is_absolute():
        config = workspace_path() / config

    if config.exists():
        config_json = json.load(config.open('r'))
    else:
        config.parent.mkdir(parents=True, exist_ok=True)
        config_json = {}

    output_base = Path(
        subprocess.check_output(['bazel', 'info', 'output_base'],
                                encoding='utf-8',
                                cwd=workspace_path(),
                                stderr=subprocess.DEVNULL).strip())

    with tempfile.NamedTemporaryFile('w') as f:
        f.write('''\
def format(target):
    for name, provider in providers(target).items():
        if name.endswith("PyInfo"):
            return provider.imports.to_list()
    return []
''')
        f.flush()

        imports = set()
        for target in targets:
            output = subprocess.check_output(
                [
                    'bazel',
                    'cquery',
                    target,
                    '--output',
                    'starlark',
                    '--starlark:file',
                    f.name,
                ],
                encoding='utf-8',
                cwd=workspace_path(),
                stderr=subprocess.DEVNULL,
            )
            matches = re.findall(r'"(\S+)"', output)
            imports.update(matches)

    extra_paths = [output_base / 'external' / x for x in imports]

    for entry in ['include', 'exclude', 'extraPaths']:
        if entry not in config_json:
            config_json[entry] = []

    for path in extra_paths:
        if path not in config_json['extraPaths']:
            config_json['extraPaths'].append(str(path))

    for include in args.includes:
        if include not in config_json['include']:
            config_json['include'].append(include)

    for exclude in args.excludes:
        if exclude not in config_json['exclude']:
            config_json['exclude'].append(exclude)

    json.dump(config_json, config.open('w'), indent=2)


if __name__ == '__main__':
    main()

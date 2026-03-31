from __future__ import annotations

import argparse
from pathlib import Path

from .engine import load_and_run_recipe
from .exceptions import PrebuildCIError
from .target import Target


def _parse_target_options(extras: list[str]) -> Target:
    """Parse ``--key=value`` or ``--key value`` extras into a Target."""
    options: dict[str, str] = {}
    it = iter(extras)
    for token in it:
        if not token.startswith("--"):
            raise SystemExit(f"Unexpected argument: {token!r}  (target options must start with --)")
        if "=" in token:
            key, _, value = token[2:].partition("=")
        else:
            try:
                value = next(it)
            except StopIteration:
                raise SystemExit(f"Option {token!r} requires a value")
            key = token[2:]
        options[key] = value
    return Target(options)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prebuildci", description="PreBuildCI build tool")
    sub = parser.add_subparsers(dest="command", required=True)

    build_cmd = sub.add_parser(
        "build",
        help="Run a build recipe",
        epilog=(
            "Target options can be passed as --key=value or --key value pairs\n"
            "and are accessible in the recipe via self.target.get('key').\n\n"
            "Examples:\n"
            "  prebuildci build recipe.py\n"
            "  prebuildci build recipe.py --os=windows --arch=x64 --config=Release"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    build_cmd.add_argument("recipe", help="Path to the recipe file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, extras = parser.parse_known_args(argv)

    target = _parse_target_options(extras)

    try:
        load_and_run_recipe(Path(args.recipe), target=target)
    except PrebuildCIError as exc:
        print(exc, flush=True)
        return 1
    return 0

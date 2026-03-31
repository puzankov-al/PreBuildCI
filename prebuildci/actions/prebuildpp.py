from __future__ import annotations

from pathlib import Path

from ..helpers.shell import run


def _target_str(target: dict[str, str]) -> str:
    """Convert a dict to ``key=value,...`` format expected by prebuildpp."""
    return ",".join(f"{k}={v}" for k, v in target.items())


def install(
    name: str,
    version: str,
    *,
    target: dict[str, str],
    output: Path | str,
    registry: str,
) -> None:
    """
    Download a prebuilt package from the registry into ``output``.

    Wraps: ``prebuildpp install <name> <version> --target <k=v,...> --output <dir> --registry <url>``

    :param name:     Package name (e.g. ``"fmt"``).
    :param version:  Package version (e.g. ``"10.1.0"``).
    :param target:   Target key-value pairs (e.g. ``{"os": "windows", "arch": "x64"}``).
    :param output:   Directory to download the package into.
    :param registry: Registry server URL.
    """
    run([
        "prebuildpp", "install", name, version,
        "--target", _target_str(target),
        "--output", str(output),
        "--registry", registry,
    ])


def publish(
    name: str,
    version: str,
    *,
    path: Path | str,
    target: dict[str, str],
    registry: str | None = None,
) -> None:
    """
    Upload a prebuilt package directory to the registry.

    Wraps: ``prebuildpp publish <name> <version> --path <dir> --target <k=v,...>``

    :param name:     Package name.
    :param version:  Package version.
    :param path:     Directory containing the prebuilt artifacts.
    :param target:   Target key-value pairs describing the binary.
    :param registry: Optional registry URL override.
    """
    cmd = [
        "prebuildpp", "publish", name, version,
        "--path", str(path),
        "--target", _target_str(target),
    ]
    if registry:
        cmd += ["--registry", registry]
    run(cmd)

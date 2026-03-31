from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ..exceptions import ShellError


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run(
    cmd: str | Sequence[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> CommandResult:
    """Run a command and capture its output."""
    args = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    print(f"$ {' '.join(args)}", flush=True)
    proc = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=env,
    )
    stdout = proc.stdout.decode(errors="replace").strip()
    stderr = proc.stderr.decode(errors="replace").strip()
    result = CommandResult(proc.returncode, stdout, stderr)

    if check and proc.returncode != 0:
        raise ShellError(" ".join(args), proc.returncode, stderr or stdout)

    return result


def capture(cmd: str | Sequence[str], **kwargs) -> str:
    """Run a command and return its stdout as a string."""
    return run(cmd, **kwargs).stdout


def stream(
    cmd: str | Sequence[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    prefix: str = "",
) -> None:
    """Run a command and print its output line-by-line in real time."""
    args = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    print(f"$ {' '.join(args)}", flush=True)
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        env=env,
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        print(f"{prefix}{line.decode(errors='replace').rstrip()}", flush=True)
    proc.wait()
    if proc.returncode != 0:
        raise ShellError(" ".join(args), proc.returncode, "")


class Shell:
    """
    Shell helper bound to a working directory and environment.
    Instantiated as ``self.shell`` on every ``BuildRecipe``.
    """

    def __init__(self, cwd: Path | str, env: dict[str, str] | None = None) -> None:
        self._cwd = str(cwd)
        self._env = env

    def run(self, cmd: str | Sequence[str], *, cwd: str | Path | None = None, **kwargs) -> CommandResult:
        return run(cmd, cwd=str(cwd) if cwd else self._cwd, env=self._env, **kwargs)

    def capture(self, cmd: str | Sequence[str], *, cwd: str | Path | None = None, **kwargs) -> str:
        return capture(cmd, cwd=str(cwd) if cwd else self._cwd, env=self._env, **kwargs)

    def stream(self, cmd: str | Sequence[str], *, cwd: str | Path | None = None, **kwargs) -> None:
        stream(cmd, cwd=str(cwd) if cwd else self._cwd, env=self._env, **kwargs)

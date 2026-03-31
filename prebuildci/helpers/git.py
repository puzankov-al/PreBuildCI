from __future__ import annotations

from pathlib import Path

from .shell import run, capture


def clone(
    url: str,
    dest: Path | str,
    *,
    branch: str | None = None,
    depth: int | None = None,
) -> Path:
    """
    Clone a git repository to dest.

    :param url: Remote URL to clone from.
    :param dest: Local destination path.
    :param branch: Branch or tag to clone.
    :param depth: Shallow clone depth (e.g. 1 for fastest checkout).
    :returns: Resolved destination path.
    """
    dest = Path(dest)
    cmd = ["git", "clone"]
    if branch:
        cmd += ["--branch", branch]
    if depth:
        cmd += ["--depth", str(depth)]
    cmd += [url, str(dest)]
    run(cmd)
    return dest.resolve()


def checkout(branch_or_sha: str, *, cwd: Path | str) -> None:
    """Check out a branch, tag, or commit SHA in an existing repo."""
    run(["git", "checkout", branch_or_sha], cwd=str(cwd))


def fetch(remote: str = "origin", *, cwd: Path | str) -> None:
    """Fetch from a remote."""
    run(["git", "fetch", remote], cwd=str(cwd))


def pull(
    remote: str = "origin",
    branch: str = "HEAD",
    *,
    cwd: Path | str,
) -> None:
    """Pull from a remote branch."""
    run(["git", "pull", remote, branch], cwd=str(cwd))


def current_branch(cwd: Path | str) -> str:
    """Return the name of the currently checked-out branch."""
    return capture(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(cwd))


def current_sha(cwd: Path | str, *, short: bool = False) -> str:
    """Return the current HEAD commit SHA."""
    args = ["git", "rev-parse"]
    if short:
        args.append("--short")
    args.append("HEAD")
    return capture(args, cwd=str(cwd))


def is_clean(cwd: Path | str) -> bool:
    """Return True if the working tree has no uncommitted changes."""
    result = run(["git", "status", "--porcelain"], cwd=str(cwd), check=False)
    return result.stdout == ""


def tag(name: str, message: str | None = None, *, cwd: Path | str) -> None:
    """Create a git tag at HEAD."""
    if message:
        run(["git", "tag", "-a", name, "-m", message], cwd=str(cwd))
    else:
        run(["git", "tag", name], cwd=str(cwd))


class Git:
    """
    Git helper bound to a working directory.
    Instantiated as ``self.git`` on every ``BuildRecipe``.
    """

    def __init__(self, cwd: Path | str) -> None:
        self._cwd = str(cwd)

    def checkout(self, branch_or_sha: str) -> None:
        checkout(branch_or_sha, cwd=self._cwd)

    def fetch(self, remote: str = "origin") -> None:
        fetch(remote, cwd=self._cwd)

    def pull(self, remote: str = "origin", branch: str = "HEAD") -> None:
        pull(remote, branch, cwd=self._cwd)

    def current_branch(self) -> str:
        return current_branch(self._cwd)

    def current_sha(self, *, short: bool = False) -> str:
        return current_sha(self._cwd, short=short)

    def is_clean(self) -> bool:
        return is_clean(self._cwd)

    def tag(self, name: str, message: str | None = None) -> None:
        tag(name, message, cwd=self._cwd)

from __future__ import annotations

import re
from pathlib import Path

from ..helpers import git
from ..helpers.shell import run


_SHA_RE = re.compile(r"^[0-9a-f]{4,40}$", re.IGNORECASE)


def _is_sha(ref: str) -> bool:
    return bool(_SHA_RE.match(ref))


def checkout(
    repo: str,
    ref: str,
    dest: Path | str,
    *,
    token: str | None = None,
    depth: int = 1,
    submodules: bool = False,
    fetch_tags: bool = False,
) -> Path:
    """
    Clone and checkout a repository — mirrors the behaviour of actions/checkout@v4.

    Handles branches, tags, and commit SHAs transparently.

    :param repo: ``owner/repo`` or a full URL.
    :param ref: Branch name, tag, or commit SHA.  Defaults to the remote HEAD.
    :param dest: Local destination path.  Defaults to the repo name.
    :param token: Optional GitHub token for private repos.
    :param depth: Shallow-clone depth.  Pass ``0`` for a full clone.
    :param submodules: Initialise and update git submodules after checkout.
    :param fetch_tags: Also fetch all tags from the remote.
    :returns: Resolved destination path.
    """
    if dest is None:
        dest = Path(repo.rstrip("/").split("/")[-1].removesuffix(".git"))
    dest = Path(dest)

    # ------------------------------------------------------------------ token
    if token is None:
        from ..env import env
        token = env("GITHUB_TOKEN")

    # ------------------------------------------------------------------ URL
    if repo.startswith(("https://", "git@", "ssh://")):
        url = repo
    else:
        if token:
            url = f"https://x-access-token:{token}@github.com/{repo}.git"
        else:
            url = f"https://github.com/{repo}.git"

    # ------------------------------------------------------------------ clone
    # For a SHA we cannot pass it to --branch, so clone the default branch
    # first, then fetch the specific commit.
    is_sha = _is_sha(ref) and ref.upper() != "HEAD"

    clone_branch = None if is_sha or ref == "HEAD" else ref
    clone_depth = depth if depth > 0 else None

    git.clone(url, dest, branch=clone_branch, depth=clone_depth)

    cwd = dest.resolve()

    # ------------------------------------------------------------------ SHA checkout
    if is_sha:
        fetch_cmd = ["git", "fetch", "origin", ref]
        if depth > 0:
            fetch_cmd += ["--depth", str(depth)]
        run(fetch_cmd, cwd=str(cwd))
        run(["git", "checkout", ref], cwd=str(cwd))

    # ------------------------------------------------------------------ tags
    if fetch_tags:
        tag_cmd = ["git", "fetch", "--tags", "--force", "origin"]
        if depth > 0:
            tag_cmd += ["--depth", str(depth)]
        run(tag_cmd, cwd=str(cwd))

    # ------------------------------------------------------------------ submodules
    if submodules:
        run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=str(cwd),
        )

    return cwd


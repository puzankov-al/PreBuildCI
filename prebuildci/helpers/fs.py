from __future__ import annotations

import glob as _glob_mod
import shutil
import tempfile
from pathlib import Path


def mkdir(path: Path | str, *, parents: bool = True, exist_ok: bool = True) -> Path:
    """Create a directory (and parents by default). Returns resolved path."""
    p = Path(path)
    p.mkdir(parents=parents, exist_ok=exist_ok)
    return p.resolve()


def clean(path: Path | str) -> None:
    """Remove a file or directory tree. No-op if path does not exist."""
    p = Path(path)
    if not p.exists():
        return
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()


def copy(src: Path | str, dest: Path | str, *, overwrite: bool = True) -> Path:
    """
    Copy a file or directory tree from src to dest.

    :param overwrite: If False, raise FileExistsError when dest already exists.
    :returns: Resolved destination path.
    """
    src, dest = Path(src), Path(dest)
    if dest.exists() and not overwrite:
        raise FileExistsError(f"{dest} already exists (overwrite=False)")
    if src.is_dir():
        result = shutil.copytree(src, dest, dirs_exist_ok=overwrite)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        result = shutil.copy2(src, dest)
    return Path(result).resolve()


def glob(pattern: str, *, root: Path | str | None = None) -> list[Path]:
    """
    Return a sorted list of paths matching the pattern.

    :param pattern: Glob pattern (supports ``**`` for recursive matching).
    :param root: If given, treat pattern as relative to this directory using
                 ``pathlib.Path.glob``; otherwise use ``glob.glob``.
    """
    if root:
        return sorted(Path(root).glob(pattern))
    return sorted(Path(p) for p in _glob_mod.glob(pattern, recursive=True))


def temp_dir(prefix: str = "prebuildci_") -> Path:
    """Create a temporary directory and return its resolved path."""
    return Path(tempfile.mkdtemp(prefix=prefix)).resolve()


def move(src: Path | str, dest: Path | str) -> Path:
    """Move a file or directory. Returns resolved destination path."""
    src, dest = Path(src), Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = shutil.move(str(src), str(dest))
    return Path(result).resolve()


class Fs:
    """
    Filesystem helper bound to a root directory.
    Instantiated as ``self.fs`` on every ``BuildRecipe``.
    Relative paths are resolved against the bound root.
    """

    def __init__(self, root: Path | str) -> None:
        self._root = Path(root)

    def _resolve(self, path: Path | str) -> Path:
        p = Path(path)
        return p if p.is_absolute() else self._root / p

    def mkdir(self, path: Path | str, *, parents: bool = True, exist_ok: bool = True) -> Path:
        return mkdir(self._resolve(path), parents=parents, exist_ok=exist_ok)

    def clean(self, path: Path | str) -> None:
        clean(self._resolve(path))

    def copy(self, src: Path | str, dest: Path | str, *, overwrite: bool = True) -> Path:
        return copy(self._resolve(src), self._resolve(dest), overwrite=overwrite)

    def move(self, src: Path | str, dest: Path | str) -> Path:
        return move(self._resolve(src), self._resolve(dest))

    def glob(self, pattern: str, *, root: Path | str | None = None) -> list[Path]:
        return glob(pattern, root=self._resolve(root) if root else self._root)

    def temp_dir(self, prefix: str = "prebuildci_") -> Path:
        return temp_dir(prefix=prefix)

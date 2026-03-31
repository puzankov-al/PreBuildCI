from pathlib import Path

from .checkout import checkout as _checkout
from .prebuildpp import install as _install, publish as _publish


class Actions:
    """
    Aggregates all built-in actions. Instantiated as ``self.actions`` on
    every ``BuildRecipe``. Relative paths are resolved against the workspace.

    Add new actions by creating a module under ``prebuildci/actions/``
    and exposing it as a method here.
    """

    def __init__(self, workspace: Path) -> None:
        self._workspace = workspace

    def _resolve(self, path: Path | str) -> Path:
        p = Path(path)
        return p if p.is_absolute() else self._workspace / p

    def checkout(self, repo: str, ref: str, dest: Path | str, **kwargs):
        return _checkout(repo, ref, self._resolve(dest), **kwargs)

    def install(self, name: str, version: str, *, output: Path | str, **kwargs):
        return _install(name, version, output=self._resolve(output), **kwargs)

    def publish(self, name: str, version: str, *, path: Path | str, **kwargs):
        return _publish(name, version, path=self._resolve(path), **kwargs)

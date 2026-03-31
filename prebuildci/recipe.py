from __future__ import annotations

from pathlib import Path

from .exceptions import PrebuildCIError
from .actions import Actions
from .helpers.fs import Fs
from .helpers.git import Git
from .helpers.shell import Shell
from .target import Target


class BuildRecipe:
    name: str | None = None
    version: str | None = None
    description: str | None = None

    def __init__(self) -> None:
        self._target: Target = Target({})
        self._workspace: Path | None = None
        self.shell: Shell | None = None
        self.fs: Fs | None = None
        self.git: Git | None = None
        self.actions: Actions | None = None

    @property
    def workspace(self) -> Path:
        if self._workspace is None:
            raise PrebuildCIError("Recipe has not been initialised yet")
        return self._workspace

    @property
    def target(self) -> Target:
        return self._target

    def layout(self) -> None:
        pass

    def fetch(self) -> None:
        pass

    def build(self) -> None:
        pass

    def test(self) -> None:
        pass

    def package(self) -> None:
        pass

    def publish(self) -> None:
        pass

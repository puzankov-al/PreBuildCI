from __future__ import annotations

from pathlib import Path

import pytest

from prebuildci import BuildRecipe, RecipeLoadError, PhaseError, load_recipe, run_recipe


def write_recipe(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def test_load_recipe_discovers_single_subclass(tmp_path: Path) -> None:
    recipe_file = write_recipe(
        tmp_path / "demo.py",
        """
from prebuildci import BuildRecipe

class Demo(BuildRecipe):
    name = "demo"
""".strip(),
    )

    recipe = load_recipe(recipe_file)

    assert isinstance(recipe, BuildRecipe)
    assert recipe.name == "demo"


def test_load_recipe_rejects_missing_recipe_class(tmp_path: Path) -> None:
    recipe_file = write_recipe(tmp_path / "demo.py", "VALUE = 1\n")

    with pytest.raises(RecipeLoadError):
        load_recipe(recipe_file)


def test_run_recipe_executes_lifecycle_in_order(tmp_path: Path) -> None:
    events: list[str] = []

    class Demo(BuildRecipe):
        name = "demo"

        def layout(self) -> None:
            events.append("layout")

        def fetch(self) -> None:
            events.append("fetch")

        def build(self) -> None:
            events.append("build")

        def test(self) -> None:
            events.append("test")

        def package(self) -> None:
            events.append("package")

        def publish(self) -> None:
            events.append("publish")

    assert run_recipe(Demo(), workspace=tmp_path) is True
    assert events == ["layout", "fetch", "build", "test", "package", "publish"]


def test_run_recipe_raises_phase_error(tmp_path: Path) -> None:
    class Demo(BuildRecipe):
        name = "demo"

        def build(self) -> None:
            raise RuntimeError("boom")

    with pytest.raises(PhaseError) as exc_info:
        run_recipe(Demo(), workspace=tmp_path, phases=["build"])

    assert exc_info.value.phase_name == "build"

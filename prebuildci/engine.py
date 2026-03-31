from __future__ import annotations

import importlib.util
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterable

from .exceptions import PhaseError, RecipeLoadError
from .actions import Actions
from .helpers.fs import Fs
from .helpers.git import Git
from .helpers.shell import Shell
from .logging import log, print_step, print_summary
from .recipe import BuildRecipe
from .target import Target

DEFAULT_PHASES = ("layout", "fetch", "build", "test", "package", "publish")


@dataclass(slots=True)
class PhaseResult:
    name: str
    status: str
    duration: float


def load_recipe(path: str | Path) -> BuildRecipe:
    recipe_path = Path(path).resolve()
    if not recipe_path.is_file():
        raise RecipeLoadError(f"Recipe file does not exist: {recipe_path}")

    module = _load_module(recipe_path)
    recipe_classes = [
        obj
        for obj in vars(module).values()
        if isinstance(obj, type) and issubclass(obj, BuildRecipe) and obj is not BuildRecipe
    ]

    if not recipe_classes:
        raise RecipeLoadError(f"No BuildRecipe subclass found in {recipe_path}")
    if len(recipe_classes) > 1:
        names = ", ".join(cls.__name__ for cls in recipe_classes)
        raise RecipeLoadError(f"Expected exactly one BuildRecipe subclass in {recipe_path}, found: {names}")

    recipe = recipe_classes[0]()
    if not recipe.name:
        recipe.name = recipe_classes[0].__name__
    return recipe


def _init_recipe(
    recipe: BuildRecipe,
    *,
    workspace: Path,
    recipe_path: Path | None = None,
) -> None:
    recipe._workspace = workspace.resolve()
    recipe.shell   = Shell(recipe._workspace)
    recipe.fs      = Fs(recipe._workspace)
    recipe.git     = Git(recipe._workspace)
    recipe.actions = Actions(recipe._workspace)


def run_recipe(
    recipe: BuildRecipe,
    *,
    workspace: Path | None = None,
    phases: Iterable[str] | None = None,
    target: Target | None = None,
) -> bool:
    if workspace is not None:
        _init_recipe(recipe, workspace=workspace)
    elif recipe._workspace is None:
        raise RecipeLoadError("Workspace is required to run a recipe")

    recipe._target = target or Target({})
    selected_phases = tuple(phases or DEFAULT_PHASES)
    _validate_phases(recipe, selected_phases)

    results: list[PhaseResult] = []
    recipe_name = recipe.name or recipe.__class__.__name__
    label = f"{recipe_name}/{recipe.version}" if recipe.version else recipe_name

    log(f"Build recipe '{label}' starting  ({len(selected_phases)} phases)")

    for phase_name in selected_phases:
        start = time.monotonic()
        try:
            getattr(recipe, phase_name)()
            status = "ok"
        except Exception as exc:
            duration = time.monotonic() - start
            results.append(PhaseResult(phase_name, "failed", duration))
            print_step(phase_name, "failed", duration)
            print_summary(label, results, success=False)
            raise PhaseError(phase_name, exc) from exc

        duration = time.monotonic() - start
        results.append(PhaseResult(phase_name, status, duration))
        print_step(phase_name, status, duration)

    print_summary(label, results, success=True)
    return True


def load_and_run_recipe(
    path: str | Path,
    *,
    workspace: Path | None = None,
    phases: Iterable[str] | None = None,
    target: Target | None = None,
) -> bool:
    recipe = load_recipe(path)
    recipe_path = Path(path).resolve()
    _init_recipe(recipe, workspace=workspace or recipe_path.parent, recipe_path=recipe_path)
    return run_recipe(recipe, phases=phases, target=target)


def _load_module(path: Path) -> ModuleType:
    module_name = f"_prebuildci_recipe_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RecipeLoadError(f"Could not import recipe from {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _validate_phases(recipe: BuildRecipe, phases: Iterable[str]) -> None:
    for phase_name in phases:
        phase = getattr(recipe, phase_name, None)
        if phase is None or not callable(phase):
            raise RecipeLoadError(f"Recipe '{recipe.__class__.__name__}' does not define phase '{phase_name}'")

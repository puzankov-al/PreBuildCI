from __future__ import annotations

from pathlib import Path

from prebuildci import Target, load_recipe, run_recipe

RECIPES_DIR = Path(__file__).parent / "recipes"


def run(recipe_file: Path, tmp_path: Path, target: Target | None = None) -> bool:
    recipe = load_recipe(recipe_file)
    return run_recipe(recipe, workspace=tmp_path, target=target)


def test_hello_recipe(tmp_path: Path) -> None:
    result = run(RECIPES_DIR / "hello_recipe.py", tmp_path)

    assert result is True
    assert (tmp_path / "build" / "hello.txt").exists()
    assert (tmp_path / "package" / "hello.txt").exists()


def test_target_recipe_defaults(tmp_path: Path) -> None:
    run(RECIPES_DIR / "target_recipe.py", tmp_path)

    content = (tmp_path / "build" / "target.txt").read_text(encoding="utf-8")
    assert "os=unknown" in content
    assert "config=Release" in content


def test_target_recipe_with_options(tmp_path: Path) -> None:
    target = Target({"os": "windows", "arch": "x64", "config": "Debug"})
    run(RECIPES_DIR / "target_recipe.py", tmp_path, target=target)

    content = (tmp_path / "build" / "target.txt").read_text(encoding="utf-8")
    assert "os=windows" in content
    assert "arch=x64" in content
    assert "config=Debug" in content

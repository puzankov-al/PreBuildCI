from __future__ import annotations

from pathlib import Path

from prebuildci.cli import main


def test_cli_build_executes_recipe(tmp_path: Path, capsys) -> None:
    recipe_file = tmp_path / "demo.py"
    recipe_file.write_text(
        """
from prebuildci import BuildRecipe

class Demo(BuildRecipe):
    name = "demo"

    def build(self) -> None:
        print("building")
""".strip(),
        encoding="utf-8",
    )

    exit_code = main(["build", str(recipe_file)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "building" in captured.out
    assert "SUCCEEDED" in captured.out


def test_cli_build_passes_target_options(tmp_path: Path, capsys) -> None:
    recipe_file = tmp_path / "demo.py"
    recipe_file.write_text(
        """
from prebuildci import BuildRecipe

class Demo(BuildRecipe):
    name = "demo"

    def build(self) -> None:
        print(f"os={self.target.os} arch={self.target.arch}")
""".strip(),
        encoding="utf-8",
    )

    exit_code = main(["build", str(recipe_file), "--os=windows", "--arch=x64"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "os=windows" in captured.out
    assert "arch=x64" in captured.out


def test_cli_build_returns_non_zero_for_invalid_recipe(tmp_path: Path, capsys) -> None:
    recipe_file = tmp_path / "demo.py"
    recipe_file.write_text("VALUE = 1\n", encoding="utf-8")

    exit_code = main(["build", str(recipe_file)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No BuildRecipe subclass found" in captured.out

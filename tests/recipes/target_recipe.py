from prebuildci import BuildRecipe


class TargetRecipe(BuildRecipe):
    """Recipe that reads target options (os, arch, config) and writes them to a file."""

    name = "target-demo"

    def layout(self) -> None:
        self.fs.mkdir("build")

    def build(self) -> None:
        os_name = self.target.get("os", "unknown")
        arch    = self.target.get("arch", "unknown")
        config  = self.target.get("config", "Release")

        output = self.workspace / "build" / "target.txt"
        output.write_text(
            f"os={os_name}\narch={arch}\nconfig={config}\n",
            encoding="utf-8",
        )

    def test(self) -> None:
        output = self.workspace / "build" / "target.txt"
        if not output.exists():
            raise RuntimeError("target.txt was not created")

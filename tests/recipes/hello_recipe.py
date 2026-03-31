from prebuildci import BuildRecipe


class HelloRecipe(BuildRecipe):
    """Minimal recipe — creates a text artifact and verifies it."""

    name = "hello"
    version = "1.0.0"

    def layout(self) -> None:
        self.fs.mkdir("build")
        self.fs.mkdir("package")

    def build(self) -> None:
        output = self.workspace / "build" / "hello.txt"
        output.write_text("hello from PreBuildCI\n", encoding="utf-8")

    def test(self) -> None:
        artifact = self.workspace / "build" / "hello.txt"
        if not artifact.exists():
            raise RuntimeError(f"Expected artifact not found: {artifact}")
        content = artifact.read_text(encoding="utf-8")
        if "hello" not in content:
            raise RuntimeError(f"Unexpected artifact content: {content!r}")

    def package(self) -> None:
        self.fs.copy("build/hello.txt", "package/hello.txt")

from prebuildci import BuildRecipe

VERSION = "12.1.0"


class FmtRecipe(BuildRecipe):
    name = "fmt"
    version = VERSION

    def layout(self) -> None:
        self.fs.mkdir("source")
        self.fs.mkdir("build")
        self.fs.mkdir("install")

    def fetch(self) -> None:
        self.actions.checkout("fmtlib/fmt", VERSION, "source")

    def build(self) -> None:
        arch   = self.target.get("arch",   "x64")
        config = self.target.get("config", "Release")

        self.shell.stream([
            "cmake",
            f"-S{self.workspace / 'source'}",
            f"-B{self.workspace / 'build'}",
            f"-A{arch}",
            "-DCMAKE_CXX_STANDARD=20",
            f"-DCMAKE_INSTALL_PREFIX={self.workspace / 'install'}",
            f"-DCMAKE_BUILD_TYPE={config}",
            "-DFMT_DOC=OFF",
            "-DFMT_TEST=OFF",
        ])
        self.shell.stream([
            "cmake", "--build", str(self.workspace / "build"),
            "--config", config,
            "--parallel",
        ])

    def package(self) -> None:
        config = self.target.get("config", "Release")
        self.shell.stream([
            "cmake", "--install", str(self.workspace / "build"),
            "--config", config,
        ])

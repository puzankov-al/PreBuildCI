# PreBuildCI

A lightweight Python framework for running CI builds from a recipe class. The framework owns the lifecycle. Your recipe
fills in the hooks.

Requires Python 3.12+.

## Installation

```bash
pip install git+https://github.com/puzankov-al/PreBuildCI.git
```

## Quick Start

Create a recipe file in your repository:

```python
from prebuildci import BuildRecipe


class MyLibRecipe(BuildRecipe):
    name = "mylib"
    version = "1.0.0"

    def layout(self) -> None:
        self.fs.mkdir("build")
        self.fs.mkdir("package")

    def fetch(self) -> None:
        self.actions.checkout("myorg/mylib", "v1.0.0", "source")

    def build(self) -> None:
        self.shell.stream("cmake -Ssource -Bbuild -DCMAKE_BUILD_TYPE=Release")
        self.shell.stream("cmake --build build --parallel")

    def package(self) -> None:
        self.shell.stream("cmake --install build --prefix package")

    def publish(self) -> None:
        self.actions.publish(
            self.name, self.version,
            path="package",
            target={"os": "windows", "arch": "x64", "build_type": "Release"},
        )
```

Run it:

```bash
prebuildci build recipe.py
```

With target options:

```bash
prebuildci build recipe.py --os=windows --arch=x64 --config=Release
```

Example output:

```
Build recipe 'mylib/1.0.0' starting  (5 phases)
  [OK] layout                         (0.00s)
  [OK] fetch                          (0.88s)
  [OK] build                          (12.4s)
  [OK] package                        (0.21s)
  [OK] publish                        (0.10s)

Build recipe 'mylib/1.0.0' SUCCEEDED  (13.6s total)
```

## Lifecycle

PreBuildCI loads the recipe class and runs phases in this fixed order:

```
layout → fetch → build → test → package → publish
```

Override only the phases you need. Empty phases are skipped automatically.

## Recipe Properties

Every `BuildRecipe` instance exposes:

| Property         | Type             | Description                                     |
|------------------|------------------|-------------------------------------------------|
| `self.workspace` | `Path`           | Resolved root directory for the build           |
| `self.target`    | `Target`         | Options passed via CLI (`--key=value`)          |
| `self.env`       | `dict[str, str]` | Environment variables                           |
| `self.shell`     | `Shell`          | Run shell commands, bound to workspace          |
| `self.fs`        | `Fs`             | Filesystem helpers, bound to workspace          |
| `self.git`       | `Git`            | Git helpers, bound to workspace                 |
| `self.actions`   | `Actions`        | High-level actions (checkout, install, publish) |

## Target Options

Pass arbitrary key-value options from the CLI:

```bash
prebuildci build recipe.py --os=windows --arch=x64 --config=Release
```

Read them in the recipe:

```python
def build(self) -> None:
    os         = self.target.require("os")                # raises if missing
    arch       = self.target.get("arch")                  # None if not passed
    build_type = self.target.get("build-type", "Release") # with default
```

## Shell

`self.shell` is bound to `self.workspace`. Relative `cwd` is resolved against it.

```python
self.shell.stream("cmake --build build --parallel")
self.shell.stream(["cmake", "--install", "build"], cwd="subdir")
output = self.shell.capture("git rev-parse --short HEAD")
result = self.shell.run("cmake --version", check=False)
```

## Filesystem

`self.fs` is bound to `self.workspace`. Relative paths are resolved against it.

```python
self.fs.mkdir("build")
self.fs.clean("build")
self.fs.copy("src/file.txt", "package/file.txt")
self.fs.move("build/out", "dist/out")
files = self.fs.glob("**/*.h", root="source/include")
tmp = self.fs.temp_dir()
```

## Git

`self.git` is bound to `self.workspace`.

```python
sha = self.git.current_sha(short=True)
branch = self.git.current_branch()
clean = self.git.is_clean()
self.git.fetch()
self.git.tag("v1.0.0", message="Release")
```

## Actions

`self.actions` provides high-level operations. Relative paths are resolved against `self.workspace`.

### `checkout`

Clone and checkout any Git repository. Handles branches, tags, and commit SHAs.

```python
self.actions.checkout("myorg/myrepo", "main", "source")
self.actions.checkout("myorg/myrepo", "v1.2.3", "source")
self.actions.checkout("myorg/myrepo", "abc1234f", "source")
self.actions.checkout("myorg/myrepo", "main", "source", depth=0, submodules=True)
```

`GITHUB_TOKEN` is read from the environment automatically for private repos.

| Parameter    | Default        | Description                              |
|--------------|----------------|------------------------------------------|
| `repo`       | —              | `owner/repo` or full URL                 |
| `ref`        | —              | Branch, tag, or commit SHA               |
| `dest`       | —              | Destination path (relative to workspace) |
| `token`      | `GITHUB_TOKEN` | GitHub auth token                        |
| `depth`      | `1`            | Shallow clone depth; `0` = full clone    |
| `submodules` | `False`        | Init and update submodules               |
| `fetch_tags` | `False`        | Fetch all tags                           |

### `install`

Download a prebuilt package from a PreBuildPP registry.

```python
self.actions.install(
    "fmt", "10.1.0",
    target={"os": "windows", "arch": "x64", "build_type": "Release"},
    output="deps/fmt",
    registry="https://registry.example.com",
)
```

### `publish`

Upload a prebuilt package directory to a PreBuildPP registry.

```python
self.actions.publish(
    self.name, self.version,
    path="install",
    target={"os": "windows", "arch": "x64", "build_type": "Release"},
    registry="https://registry.example.com",
)
```

## Environment

Read environment variables and secrets from anywhere in a recipe:

```python
token = self.env.get("GITHUB_TOKEN")
value = self.env.get("MY_VAR", "default")
```

## Project Structure

```
prebuildci/
├── recipe.py      — BuildRecipe base class
├── engine.py      — recipe loader and lifecycle executor
├── cli.py         — command-line entry point (prebuildci build)
├── target.py      — Target options
├── exceptions.py
├── logging.py
├── helpers/
│   ├── shell.py   — run, capture, stream + Shell class
│   ├── git.py     — clone, checkout, fetch, … + Git class
│   ├── artifacts.py — LocalArtifactStore, S3ArtifactStore
│   └── fs.py      — mkdir, clean, copy, move, glob + Fs class
└── actions/
    ├── checkout.py   — checkout()
    └── prebuildpp.py — install(), publish()
```

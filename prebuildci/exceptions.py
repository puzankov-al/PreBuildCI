class PrebuildCIError(Exception):
    """Base for all framework errors."""


class RecipeLoadError(PrebuildCIError):
    """Raised when a recipe cannot be loaded or validated."""


class PhaseError(PrebuildCIError):
    def __init__(self, phase_name: str, cause: Exception):
        self.phase_name = phase_name
        self.cause = cause
        super().__init__(f"[{phase_name}] {cause}")


class StepError(PhaseError):
    """Backward-compatible alias for older pipeline terminology."""


class ShellError(PrebuildCIError):
    def __init__(self, cmd: str, returncode: int, output: str):
        self.cmd = cmd
        self.returncode = returncode
        super().__init__(f"Command '{cmd}' exited {returncode}: {output}")


class ArtifactError(PrebuildCIError):
    """Raised by artifact helpers."""

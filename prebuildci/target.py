from __future__ import annotations


class Target:
    """
    Holds target options passed on the command line, e.g.
    ``--os=windows --arch=x64 --config=Release``.

    Values are accessed via ``get`` (optional) or ``require`` (mandatory)::

        os   = self.target.require("os")               # raises if missing
        arch = self.target.get("arch")                 # None if missing
        cfg  = self.target.get("build-type", "Release") # with default
    """

    def __init__(self, options: dict[str, str]) -> None:
        self._options = options

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._options.get(key, default)

    def require(self, key: str) -> str:
        """Return the value for *key* or raise if it was not provided."""
        if key not in self._options:
            raise KeyError(f"Required target option '--{key}' was not provided")
        return self._options[key]

    def __getattr__(self, key: str) -> str | None:
        try:
            return self._options[key]
        except KeyError:
            return None

    def __repr__(self) -> str:
        pairs = ", ".join(f"{k}={v!r}" for k, v in self._options.items())
        return f"Target({pairs})"

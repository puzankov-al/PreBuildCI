from __future__ import annotations

def log(message: str) -> None:
    print(message, flush=True)


def print_step(name: str, status: str, duration: float) -> None:
    icon = "[OK]" if status == "ok" else ("[--]" if status == "ignored" else "[!!]")
    print(f"  {icon} {name:<30} ({duration:.2f}s)", flush=True)


def print_summary(build_name: str, results: list[object], success: bool) -> None:
    total = sum(result.duration for result in results)
    status = "SUCCEEDED" if success else "FAILED"
    failed_step = next((result.name for result in results if result.status == "failed"), None)
    if failed_step:
        print(f"\nBuild recipe '{build_name}' {status} at phase '{failed_step}'  ({total:.2f}s total)", flush=True)
    else:
        print(f"\nBuild recipe '{build_name}' {status}  ({total:.2f}s total)", flush=True)

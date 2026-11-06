"""Shared helpers for all verifier modules. Pure functions of their arguments."""

from pathlib import Path


def result(valid: bool, message: str, *, score: float | None = None, **details) -> dict:
    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def path_problem(file_path: str) -> str | None:
    """return a reason string if file_path is unsafe, else None"""
    p = Path(file_path)
    if p.is_absolute():
        return "file_path must be relative to the workspace, not absolute"
    if ".." in p.parts:
        return "file_path must not escape the workspace with '..'"
    if not p.parts:
        return "file_path must not be empty"
    return None


def expected_matches(workspace: Path, file_path: str, target: str) -> list[str] | None:
    """lines containing target from the file, or None if the file is missing"""
    path = workspace / file_path
    if not path.is_file():
        return None
    return [line for line in path.read_text(encoding="utf-8").splitlines() if target in line]

"""Core logic: read a workspace file and return lines containing the target keyword."""

from pathlib import Path

from contract import FilterInput, FilterOutput


def filter_lines(input: FilterInput, workspace: Path) -> FilterOutput:
    # resolve path inside workspace; raises if file is missing
    path = workspace / input.file_path
    text = path.read_text(encoding="utf-8")
    # keep lines whose text contains the target as an exact substring
    matches = [line for line in text.splitlines() if input.target in line]
    return FilterOutput(matches=matches)

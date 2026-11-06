"""
Standalone local test runner — no RUSH Lab access required.

Mocks agent output directly and runs every verifier branch.
Run from the plugin root:

    uv run python test_local.py

Each test prints PASS or FAIL and exits with code 1 on any failure.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import verifier
from contract import FilterInput, FilterOutput

# ── fixture data (mirrors data/social_media_sample.txt) ──────────────────────

SAMPLE_LINES = [
    "that party was hella fun last night",
    "no cap this is the best pizza i ever had",
    "she hella smart for that one",
    "bruh i aint even tryna go out rn",
    "hella good vibes only",
    "its giving main character energy fr",
    "i was hella tired after work today",
    "the weather is so nice today",
    "on god thats wild",
    "she said hella like five times in one sentence",
]

TARGET = "hella"
EXPECTED = [line for line in SAMPLE_LINES if TARGET in line]  # ground truth

FAILURES: list[str] = []


# ── helpers ───────────────────────────────────────────────────────────────────

def make_workspace(lines: list[str] | None = None, filename: str = "social_media_sample.txt") -> str:
    """create a temp dir, write the sample file, and return the dir path as str"""
    d = tempfile.mkdtemp()
    content = "\n".join(lines if lines is not None else SAMPLE_LINES)
    (Path(d) / filename).write_text(content, encoding="utf-8")
    return d


def run(name: str, valid: bool, result: dict) -> None:
    """assert the expected validity and print PASS / FAIL"""
    ok = result["valid"] is valid
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}: {result['message']}")
    if not ok:
        FAILURES.append(name)


def check_task(workspace: str, matches: list[str], target: str = TARGET) -> dict:
    args = FilterInput(file_path="social_media_sample.txt", target=target)
    out = FilterOutput(matches=matches)
    return verifier.verify_task("regional-keyword-filter", args, out, None, workspace)


def check_input(file_path: str = "social_media_sample.txt", target: str = TARGET) -> dict:
    return verifier.verify_input("filter_lines", FilterInput(file_path=file_path, target=target))


# ── correct case ──────────────────────────────────────────────────────────────

def test_correct_output() -> None:
    ws = make_workspace()
    run("correct output", True, check_task(ws, EXPECTED))


# ── incorrect cases ───────────────────────────────────────────────────────────

def test_wrong_lines() -> None:
    ws = make_workspace()
    # agent returned a non-matching line
    run("wrong lines", False, check_task(ws, ["no cap this is the best pizza i ever had"]))


def test_partial_matches() -> None:
    ws = make_workspace()
    # agent returned only the first two matching lines, missing the rest
    run("partial matches", False, check_task(ws, EXPECTED[:2]))


def test_extra_lines() -> None:
    ws = make_workspace()
    # agent returned correct matches plus a non-matching bonus line
    run("extra lines", False, check_task(ws, EXPECTED + ["bruh i aint even tryna go out rn"]))


# ── missing case ──────────────────────────────────────────────────────────────

def test_empty_output_when_matches_exist() -> None:
    ws = make_workspace()
    run("empty output (matches exist)", False, check_task(ws, []))


# ── malformed input cases ─────────────────────────────────────────────────────

def test_empty_target() -> None:
    run("empty target", False, check_input(target=""))


def test_absolute_path() -> None:
    run("absolute file_path", False, check_input(file_path="/etc/passwd"))


def test_path_traversal() -> None:
    run("path traversal", False, check_input(file_path="../secret.txt"))


def test_empty_file_path() -> None:
    run("empty file_path", False, check_input(file_path=""))


# ── boundary cases ─────────────────────────────────────────────────────────────

def test_empty_file() -> None:
    ws = make_workspace(lines=[])
    run("empty file → empty output", True, check_task(ws, []))


def test_no_matches_in_file() -> None:
    ws = make_workspace(lines=["totally neutral text", "nothing to see here"])
    run("no matches → empty output", True, check_task(ws, []))


def test_missing_file_in_workspace() -> None:
    # workspace dir exists but file was never written
    d = tempfile.mkdtemp()
    args = FilterInput(file_path="social_media_sample.txt", target=TARGET)
    out = FilterOutput(matches=[])
    r = verifier.verify_task("regional-keyword-filter", args, out, None, d)
    run("missing file in workspace", False, r)


def test_single_line_match() -> None:
    ws = make_workspace(lines=["hella rare single line"])
    run("single matching line", True, check_task(ws, ["hella rare single line"]))


def test_different_target_keyword() -> None:
    # verifier must generalise beyond "hella"
    ws = make_workspace()
    expected_cap = [line for line in SAMPLE_LINES if "cap" in line]
    args = FilterInput(file_path="social_media_sample.txt", target="cap")
    out = FilterOutput(matches=expected_cap)
    r = verifier.verify_task("regional-keyword-filter", args, out, None, ws)
    run("different target keyword (cap)", True, r)


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n── Regional Keyword Filter — local verifier tests ──\n")

    print("Correct:")
    test_correct_output()

    print("\nIncorrect:")
    test_wrong_lines()
    test_partial_matches()
    test_extra_lines()

    print("\nMissing:")
    test_empty_output_when_matches_exist()

    print("\nMalformed input:")
    test_empty_target()
    test_absolute_path()
    test_path_traversal()
    test_empty_file_path()

    print("\nBoundary:")
    test_empty_file()
    test_no_matches_in_file()
    test_missing_file_in_workspace()
    test_single_line_match()
    test_different_target_keyword()

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} test(s) — {', '.join(FAILURES)}")
        sys.exit(1)
    else:
        print(f"All {14} tests passed.")

"""Pytest tests covering correct, incorrect, missing, malformed, and boundary verifier cases."""

from __future__ import annotations

from pathlib import Path

import verifier
from contract import FilterInput, FilterOutput

# the bundled sample lines — mirrors data/social_media_sample.txt exactly
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
# ground-truth matches: only lines containing "hella"
EXPECTED = [line for line in SAMPLE_LINES if TARGET in line]


def _make_workspace(tmp_path: Path, lines: list[str] | None = None, filename: str = "social_media_sample.txt") -> Path:
    """write sample lines into tmp_path and return the workspace path"""
    content = "\n".join(lines if lines is not None else SAMPLE_LINES)
    (tmp_path / filename).write_text(content, encoding="utf-8")
    return tmp_path


def _args(file_path: str = "social_media_sample.txt", target: str = TARGET) -> FilterInput:
    return FilterInput(file_path=file_path, target=target)


def _out(matches: list[str]) -> FilterOutput:
    return FilterOutput(matches=matches)


# ── correct case ──────────────────────────────────────────────────────────────

def test_approves_correct_matches(tmp_path: Path) -> None:
    ws = _make_workspace(tmp_path)
    r = verifier.verify_task("regional-keyword-filter", _args(), _out(EXPECTED), None, str(ws))
    assert r["valid"] is True
    assert r["score"] == 1.0
    assert "correct" in r["message"]


# ── incorrect case ────────────────────────────────────────────────────────────

def test_refuses_wrong_lines(tmp_path: Path) -> None:
    ws = _make_workspace(tmp_path)
    # agent returned a line that does NOT contain "hella"
    wrong = ["no cap this is the best pizza i ever had"]
    r = verifier.verify_task("regional-keyword-filter", _args(), _out(wrong), None, str(ws))
    assert r["valid"] is False
    assert r["details"]["expected"] == len(EXPECTED)
    assert r["details"]["got"] == 1


# ── missing case ──────────────────────────────────────────────────────────────

def test_refuses_empty_list_when_matches_exist(tmp_path: Path) -> None:
    ws = _make_workspace(tmp_path)
    # agent returned nothing despite matches being present
    r = verifier.verify_task("regional-keyword-filter", _args(), _out([]), None, str(ws))
    assert r["valid"] is False
    assert r["details"]["expected"] == len(EXPECTED)
    assert r["details"]["got"] == 0


# ── extra lines case ──────────────────────────────────────────────────────────

def test_refuses_extra_lines_beyond_expected(tmp_path: Path) -> None:
    ws = _make_workspace(tmp_path)
    # agent returned a correct line plus a non-matching extra line
    extra = EXPECTED + ["bruh i aint even tryna go out rn"]
    r = verifier.verify_task("regional-keyword-filter", _args(), _out(extra), None, str(ws))
    assert r["valid"] is False
    assert r["details"]["got"] == len(EXPECTED) + 1


# ── malformed input cases ─────────────────────────────────────────────────────

def test_refuses_empty_target() -> None:
    # empty target is meaningless and must be rejected at input validation
    r = verifier.verify_input("filter_lines", _args(target=""))
    assert r["valid"] is False
    assert "non-empty" in r["message"]


def test_refuses_absolute_file_path() -> None:
    r = verifier.verify_input("filter_lines", _args(file_path="/etc/passwd"))
    assert r["valid"] is False
    assert "absolute" in r["message"]


def test_refuses_path_traversal() -> None:
    r = verifier.verify_input("filter_lines", _args(file_path="../outside.txt"))
    assert r["valid"] is False
    assert ".." in r["message"]


def test_refuses_empty_file_path() -> None:
    r = verifier.verify_input("filter_lines", _args(file_path=""))
    assert r["valid"] is False


# ── boundary cases ─────────────────────────────────────────────────────────────

def test_approves_empty_list_for_empty_file(tmp_path: Path) -> None:
    # empty file → no matches → correct answer is []
    _make_workspace(tmp_path, lines=[])
    r = verifier.verify_task("regional-keyword-filter", _args(), _out([]), None, str(tmp_path))
    assert r["valid"] is True
    assert r["details"]["count"] == 0


def test_approves_empty_list_when_no_lines_match(tmp_path: Path) -> None:
    # file has content but none of the lines contain the target
    _make_workspace(tmp_path, lines=["totally neutral text", "nothing interesting here"])
    r = verifier.verify_task("regional-keyword-filter", _args(), _out([]), None, str(tmp_path))
    assert r["valid"] is True
    assert r["details"]["count"] == 0


def test_refuses_when_file_is_missing_from_workspace(tmp_path: Path) -> None:
    # workspace exists but the requested file was never written
    r = verifier.verify_task("regional-keyword-filter", _args(), _out([]), None, str(tmp_path))
    assert r["valid"] is False
    assert "not found" in r["message"]


def test_approves_single_line_file_with_match(tmp_path: Path) -> None:
    # boundary: file is one line and it matches
    _make_workspace(tmp_path, lines=["hella rare edge case"])
    r = verifier.verify_task("regional-keyword-filter", _args(), _out(["hella rare edge case"]), None, str(tmp_path))
    assert r["valid"] is True
    assert r["details"]["count"] == 1


def test_approves_different_target_keyword(tmp_path: Path) -> None:
    # verifier is not hardcoded to "hella"; it works for any target
    _make_workspace(tmp_path)
    args = _args(target="cap")
    expected = [line for line in SAMPLE_LINES if "cap" in line]
    r = verifier.verify_task("regional-keyword-filter", args, _out(expected), None, str(tmp_path))
    assert r["valid"] is True

"""Deterministic checks for the filter_lines tool and regional-keyword-filter task."""

from pathlib import Path

from .checks import expected_matches, path_problem, result


def verify_input(value) -> dict:
    # target must be a non-empty string
    if not value.target:
        return result(False, "target must be a non-empty string")
    # file_path must stay inside the workspace
    problem = path_problem(value.file_path)
    if problem:
        return result(False, problem)
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace: str) -> dict:
    expected = expected_matches(Path(workspace), input_value.file_path, input_value.target)
    # file must exist in the workspace
    if expected is None:
        return result(False, "file not found in workspace")
    # matches must be exactly the lines containing the target, in order
    if output_value.matches != expected:
        return result(
            False,
            f"matches do not equal the expected lines",
            expected=len(expected),
            got=len(output_value.matches),
        )
    return result(True, "all matches are correct", count=len(expected))


def verify_task(arguments, output, reference, workspace: str) -> dict:
    # task output is identical in shape to the tool output; reuse the same check
    return verify_output(arguments, output, workspace)

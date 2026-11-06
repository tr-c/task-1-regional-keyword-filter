"""The deterministic verifier: each tool's checks live in filter.py, on contract instances."""

from contract import Task, Tool

from . import filter as _filter

# map each tool to its verifier module
TOOLS = {Tool.FILTER_LINES: _filter}
# map each task to its verify_task function
TASKS = {Task.REGIONAL_KEYWORD_FILTER: _filter.verify_task}


def verify_input(tool: str, value) -> dict:
    return TOOLS[Tool(tool)].verify_input(value)


def verify_output(tool: str, input_value, output_value, workspace: str) -> dict:
    return TOOLS[Tool(tool)].verify_output(input_value, output_value, workspace)


def verify_task(task: str, arguments, output, reference, workspace: str) -> dict:
    return TASKS[Task(task)](arguments, output, reference, workspace)

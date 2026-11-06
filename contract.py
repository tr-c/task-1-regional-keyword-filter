"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    FILTER_LINES = "filter_lines"


class Task(Enum):
    REGIONAL_KEYWORD_FILTER = "regional-keyword-filter"


# input: a workspace-relative file path and the target keyword
@dataclass
class FilterInput(Output):
    file_path: Annotated[str, "Path to the text file to search, relative to the plugin workspace"]
    target: Annotated[str, "Keyword to find; matched as an exact substring of each line"]


# output: every line from the file that contains the target, in original order
@dataclass
class FilterOutput(Output):
    matches: Annotated[list[str], "Lines that contain the target keyword, in the order they appear in the file"]


TOOLS = {Tool.FILTER_LINES: (FilterInput, FilterOutput)}
TASKS = {Task.REGIONAL_KEYWORD_FILTER: (FilterInput, FilterOutput)}

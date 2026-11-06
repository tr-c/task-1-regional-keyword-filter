"""The MCP server: each call's input built into its contract class, its output checked against its own."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import anyio
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from slimconfig import build_output, output_schema, plain_output

from contract import TOOLS, Tool
from plugin import filter_lines

server = Server("regional-keyword-filter")

# nanoagent passes the plugin's private workspace folder via this var
WORKSPACE_ENV = "NANOAGENT_WORKSPACE"

# bundled sample file ships with the plugin in data/
_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_SAMPLE_FILE = "social_media_sample.txt"

# each tool's implementation: (FilterInput, workspace) -> FilterOutput
IMPLEMENTATIONS = {Tool.FILTER_LINES: filter_lines}


def _seed_workspace(workspace: Path) -> None:
    """copy bundled data files into the workspace on startup so the agent can read them"""
    dest = workspace / _SAMPLE_FILE
    if not dest.exists():
        shutil.copy(_DATA_DIR / _SAMPLE_FILE, dest)


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(name=tool.value, inputSchema=output_schema(given), outputSchema=output_schema(made))
        for tool, (given, made) in TOOLS.items()
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    # a failure raises; the mcp server returns it as an error result
    tool = Tool(name)
    given, made = TOOLS[tool]
    workspace = Path(os.environ[WORKSPACE_ENV])
    output = IMPLEMENTATIONS[tool](build_output(arguments, given), workspace)
    if not isinstance(output, made):
        raise TypeError(f"{name} returned {type(output).__name__}, not {made.__name__}")
    return plain_output(output)


def main() -> None:
    if WORKSPACE_ENV not in os.environ:
        raise SystemExit(f"{WORKSPACE_ENV} is not set: nanoagent passes the plugin workspace folder")
    if set(IMPLEMENTATIONS) != set(Tool):
        raise SystemExit("IMPLEMENTATIONS must cover every contract.Tool")

    workspace = Path(os.environ[WORKSPACE_ENV])
    _seed_workspace(workspace)  # place sample file before the agent runs

    async def run() -> None:
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    anyio.run(run)


if __name__ == "__main__":
    main()

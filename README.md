# Regional Keyword Filter

A `nanoagent.plugin/v0001` plugin for **Autono-Linguist** (COMP 580).

Given a social media text file and a target sociolinguistic variable (e.g. the
Bay Area marker *hella*), the agent extracts every line that contains it as an
exact substring. This is Task 1 of five evaluation environments for the
Autono-Linguist Count-Min Sketch agent.

## Tools

| Tool | Does | Code |
|---|---|---|
| `filter_lines` | Read a workspace file and return every line containing the target | `src/plugin/filter.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `regional-keyword-filter` | Extract lines containing a sociolinguistic keyword | `tool`, with `filter_lines` |

## Layout

```text
.
├── nanoagent.yaml          # manifest: id, runtime, permissions, tools, tasks
├── contract.py             # typed FilterInput / FilterOutput; TOOLS and TASKS dicts
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env
├── data/
│   └── social_media_sample.txt   # bundled 10-line sociolinguistic fixture
├── src/plugin/             # MCP server + filter_lines implementation
├── tests/                  # pytest suite (correct, incorrect, missing, malformed, boundary)
├── test_local.py           # standalone runner; no RUSH Lab needed
├── ui/                     # page renderers
├── product/                # marketplace listing
└── verifier/               # deterministic verifier package
```

## Develop and run

```bash
# install dependencies (generates uv.lock)
uv sync --extra dev

# run the full pytest suite
uv run pytest

# run the standalone local tests without pytest
uv run python test_local.py
```

Publishing checks every plugin rule: push the plugin to a public GitHub
repository and run `rush publish <server> <github-url>`.

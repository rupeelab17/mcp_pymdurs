"""CLI entry: ``python -m mcp_pymdurs`` or ``uv run mcp-pymdurs``."""

from __future__ import annotations

import os

from mcp_pymdurs.app import app


def main() -> None:
    host = os.environ.get("MCP_PYMDURS_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PYMDURS_PORT", "8080"))
    app.start(host=host, port=port)


if __name__ == "__main__":
    main()

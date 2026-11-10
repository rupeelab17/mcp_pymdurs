# MCP Server for pymdurs

HTTP MCP server ([Robyn](https://robyn.tech/documentation/en/api_reference/mcps)) that exposes [pymdurs](https://github.com/rupeelab17/pymdurs/) geometric collectors to AI clients (Claude Desktop, curl, …).

Inspired by [mcp_pymdu](https://github.com/rupeelab17/mcp_pymdu), rewritten for **uv + Python 3.14 + Robyn + pymdurs**.

> Robyn MCP is experimental. Transport is **HTTP JSON-RPC** on `/mcp` (not FastMCP stdio).

Request bodies for REST helpers use [Robyn Pydantic integration](https://robyn.tech/documentation/en/api_reference/pydantic) (`robyn[pydantic]`). MCP tool `input_schema` is generated from the same Pydantic models in [`mcp_pymdurs/schemas.py`](mcp_pymdurs/schemas.py).

Invalid REST bodies return **422** with Pydantic error details. Models live in `schemas.py`; `app.py` must keep real (non-stringified) type annotations so Robyn can detect `BaseModel` parameters.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.14
- Network access to IGN / data.gouv.fr for live fetches

## Setup

```bash
uv sync
```

## Run

```bash
uv run python -m mcp_pymdurs
# or
uv run mcp-pymdurs
```

Server listens on `0.0.0.0:8080` by default. Override with `MCP_PYMDURS_HOST` / `MCP_PYMDURS_PORT`.

- Health: `GET http://localhost:8080/`
- Defaults: `GET http://localhost:8080/defaults`
- MCP: `POST http://localhost:8080/mcp`
- REST (Pydantic-validated): `POST /api/bbox`, `/api/buildings`, `/api/dem`, `/api/lcz`, `/api/cadastre`, `/api/roads`, `/api/water`
- OpenAPI: `http://localhost:8080/openapi.json` · Docs: `http://localhost:8080/docs`

## Tools

| Tool | Purpose |
|------|---------|
| `get_bbox_area` | Square WGS84 bbox from lat/lon + area (km²) |
| `fetch_buildings` | IGN buildings → JSON GeoJSON summary or Plotly HTML (`as_html`) |
| `fetch_dem` | DEM / MNT → TIFF + mask paths |
| `fetch_lcz` | Local Climate Zones (data.gouv zip + pymdurs) |
| `fetch_cadastre` | Cadastre parcels |
| `fetch_roads` | IGN roads |
| `fetch_water` | IGN water bodies |
| `pymdu_building_to_image` | mcp_pymdu alias → buildings Plotly HTML |
| `pymdu_lcz_to_image` | mcp_pymdu alias → LCZ Plotly HTML |

Default bbox (La Rochelle): `[-1.152704, 46.181627, -1.139893, 46.18699]` (WGS84). Collectors reproject to EPSG:2154 by default.

## Resource / prompt

- Resource `pymdurs://defaults/bbox` — default bbox / CRS / output path
- Prompt `urban_explore` — suggested agent workflow

## Quick MCP checks

With the server running:

```bash
bash examples/curl_mcp.sh
```

Example:

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Claude Desktop

Claude Desktop `claude_desktop_config.json` is **stdio-only**. Do **not** put a `"url"` field there (it can wipe `mcpServers`). Bridge HTTP with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote).

1. Start the server: `uv run python -m mcp_pymdurs`
2. Edit config:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
3. Add (merge into existing `mcpServers` if any):

```json
{
  "mcpServers": {
    "pymdurs": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://127.0.0.1:8080/mcp"]
    }
  }
}
```

4. Fully quit and reopen Claude Desktop. Needs Node.js (`npx`).

Alternative with [`mcp-proxy`](https://github.com/sparfenyuk/mcp-proxy):

```json
{
  "mcpServers": {
    "pymdurs": {
      "command": "uvx",
      "args": [
        "mcp-proxy",
        "--transport",
        "streamablehttp",
        "http://127.0.0.1:8080/mcp"
      ]
    }
  }
}
```

Clients that support HTTP MCP natively (e.g. Claude Code) can use `"type": "http"` + `"url": "http://127.0.0.1:8080/mcp"` instead of a bridge.

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).

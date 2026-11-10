# mcp_pymdurs

**Urban geometry for AI agents** — an HTTP MCP server that wraps [pymdurs](https://github.com/rupeelab17/pymdurs/) collectors (buildings, DEM, LCZ, cadastre, roads, water) behind [Robyn](https://robyn.tech/documentation/en/api_reference/mcps) JSON-RPC.

Inspired by [mcp_pymdu](https://github.com/rupeelab17/mcp_pymdu), rebuilt for **uv · Python 3.14 · Robyn · pymdurs**.

[![Python 3.14](https://img.shields.io/badge/python-3.14-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/packaging-uv-DE5FE9?style=flat-square)](https://docs.astral.sh/uv/)
[![Robyn](https://img.shields.io/badge/MCP-Robyn_HTTP-0A7EA4?style=flat-square)](https://robyn.tech/documentation/en/api_reference/mcps)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0--or--later-blue?style=flat-square)](LICENSE)

> Robyn MCP is experimental. Transport is **HTTP JSON-RPC** on `/mcp` (not FastMCP stdio). All tools are **async**.

---

## Why

| Need | What you get |
|------|----------------|
| Give Claude / agents French urban layers | One MCP endpoint, nine tools |
| Plotly HTML maps | `pymdurs_building_to_image` / `pymdurs_lcz_to_image` |
| Typed contracts | Same Pydantic models for MCP `input_schema` and REST `/api/*` |
| Interactive maps | Plotly HTML via `as_html=true` |

Default study area: **La Rochelle**  
`[-1.152704, 46.181627, -1.139893, 46.18699]` (WGS84) → collectors reproject to **EPSG:2154**.

---

## Quick start

```bash
uv sync
uv run python -m mcp_pymdurs
# or: uv run mcp-pymdurs
```

| | |
|--|--|
| Listen | `0.0.0.0:8080` (`MCP_PYMDURS_HOST` / `MCP_PYMDURS_PORT`) |
| Health | [`GET /`](http://localhost:8080/) |
| Defaults | [`GET /defaults`](http://localhost:8080/defaults) |
| MCP | [`POST /mcp`](http://localhost:8080/mcp) |
| Docs | [`/docs`](http://localhost:8080/docs) · [`/openapi.json`](http://localhost:8080/openapi.json) |

Smoke test:

```bash
bash examples/curl_mcp.sh
```

```bash
curl -sS -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

---

## Architecture

```
┌──────────────┐     JSON-RPC      ┌─────────────┐     pymdurs      ┌─────────────┐
│ Claude / curl│ ───────────────▶  │  Robyn :8080│ ───────────────▶ │ IGN / gouv  │
│ mcp-remote   │   POST /mcp       │  async tools│   Building, Dem… │ data.gouv   │
└──────────────┘                   └──────┬──────┘                  └─────────────┘
                                          │
                                   POST /api/*  (Pydantic → 422 on bad body)
```

Schemas live in [`mcp_pymdurs/schemas.py`](mcp_pymdurs/schemas.py).  
**Note:** `app.py` must keep real (non-stringified) type annotations — no `from __future__ import annotations` — so Robyn can detect `BaseModel` params.

---

## MCP tools

| Tool | Returns |
|------|---------|
| `get_bbox_area` | Square WGS84 bbox from `lat` / `lon` / `bbox_area` (km²) |
| `fetch_buildings` | Buildings JSON summary, or Plotly HTML if `as_html` |
| `fetch_dem` | DEM / MNT TIFF + mask paths |
| `fetch_lcz` | Local Climate Zones (data.gouv zip + pymdurs) |
| `fetch_cadastre` | Cadastre parcels |
| `fetch_roads` | IGN roads |
| `fetch_water` | IGN water bodies |
| `pymdurs_building_to_image` | Buildings Plotly HTML |
| `pymdurs_lcz_to_image` | LCZ Plotly HTML via pymdurs |

Also registered:

- **Resource** `pymdurs://defaults/bbox` — default bbox / CRS / output path  
- **Prompt** `urban_explore` — suggested agent workflow  

### REST mirrors

Same payloads, Pydantic-validated (`robyn[pydantic]`):

`POST /api/bbox` · `/api/buildings` · `/api/dem` · `/api/lcz` · `/api/cadastre` · `/api/roads` · `/api/water`

---

## Claude Desktop

Claude Desktop config is **stdio-only**. Do **not** put a `"url"` field in `claude_desktop_config.json` (it can wipe `mcpServers`). Bridge with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote):

1. Start the server: `uv run python -m mcp_pymdurs`
2. Edit config  
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`  
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
3. Merge:

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

4. Fully quit and reopen Claude Desktop (needs Node.js / `npx`).

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

Clients with native HTTP MCP (e.g. Claude Code) can use `"type": "http"` + `"url": "http://127.0.0.1:8080/mcp"` — no bridge.

---

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python **3.14**
- Network access to IGN / [data.gouv.fr](https://www.data.gouv.fr/) for live fetches

---

## License

**GPL-3.0-or-later** — see [LICENSE](LICENSE).

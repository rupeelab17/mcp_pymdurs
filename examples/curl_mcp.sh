#!/usr/bin/env bash
# Smoke-test Robyn MCP JSON-RPC at http://localhost:8080/mcp
set -euo pipefail

BASE_URL="${MCP_PYMDURS_URL:-http://localhost:8080/mcp}"

rpc() {
  local payload="$1"
  curl -sS -X POST "$BASE_URL" \
    -H "Content-Type: application/json" \
    -d "$payload"
  echo
}

echo "== resources/list =="
rpc '{"jsonrpc":"2.0","id":1,"method":"resources/list","params":{}}'

echo "== tools/list =="
rpc '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

echo "== prompts/list =="
rpc '{"jsonrpc":"2.0","id":3,"method":"prompts/list","params":{}}'

echo "== tools/call get_bbox_area =="
rpc '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_bbox_area","arguments":{"lat":46.18,"lon":-1.15,"bbox_area":1.0}}}'

HTTP_BASE="${MCP_PYMDURS_HTTP:-http://localhost:8080}"

echo "== REST POST /api/bbox (Pydantic) =="
curl -sS -X POST "$HTTP_BASE/api/bbox" \
  -H "Content-Type: application/json" \
  -d '{"lat":46.18,"lon":-1.15,"bbox_area":1.0}'
echo

echo "== REST POST /api/bbox invalid (expect 422) =="
curl -sS -o /tmp/mcp_pymdurs_422.json -w "HTTP %{http_code}\n" -X POST "$HTTP_BASE/api/bbox" \
  -H "Content-Type: application/json" \
  -d '{"lat":46.18,"lon":-1.15,"bbox_area":"nope"}'
cat /tmp/mcp_pymdurs_422.json
echo

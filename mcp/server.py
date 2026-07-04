from __future__ import annotations

"""Minimal stdio MCP-style server for restricted Source2Study tools."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp.schemas import list_tools
from mcp.tools import call_tool


INSTRUCTIONS = (
    "Source2Study MCP exposes only low-risk, auditable tools: policy, inspect, ingest local, "
    "build index, generate, validate, and eval. Do not request cookies, browser profiles, "
    "login sessions, shell commands, arbitrary file reads, arbitrary URLs, or platform bypasses."
)


def list_mcp_tools() -> list[dict]:
    return list_tools()


def handle_message(message: dict[str, Any]) -> dict[str, Any]:
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "source2study", "version": "1.0.0a0"},
                "instructions": INSTRUCTIONS,
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": list_tools()}}
    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        result = call_tool(str(name), arguments)
        is_error = result.get("status") not in {"pass", "degraded"}
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "structuredContent": result,
                "isError": is_error,
            },
        }
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Unsupported method: {method}"},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the restricted Source2Study MCP stdio server.")
    parser.add_argument("--list-tools", action="store_true", help="print tool schemas and exit")
    args = parser.parse_args(argv)
    if args.list_tools:
        print(json.dumps({"tools": list_tools()}, ensure_ascii=False, indent=2))
        return 0

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            response = handle_message(message)
        except Exception as exc:  # noqa: BLE001 - protocol errors must be serialized.
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""A minimal Model Context Protocol (MCP) server over stdio, using only the Python standard library.

MCP is JSON-RPC 2.0, one JSON message per line on stdin/stdout. This implements the parts a
tools-only server needs: initialize, tools/list, tools/call, and ping.
"""
from __future__ import annotations

import inspect
import json
import sys
import traceback
from typing import Any, Callable, Dict

PROTOCOL_VERSION = "2025-06-18"


class Server:
    def __init__(self, name: str, version: str = "0.1.0"):
        self.name, self.version = name, version
        self.tools: Dict[str, dict] = {}

    def tool(self, description: str, schema: dict):
        """Register a function as a tool. `schema` maps parameter names to JSON Schema snippets."""
        def deco(fn: Callable[..., Any]):
            params = inspect.signature(fn).parameters
            required = [n for n, p in params.items() if p.default is inspect.Parameter.empty]
            self.tools[fn.__name__] = {
                "fn": fn,
                "spec": {
                    "name": fn.__name__,
                    "description": description,
                    "inputSchema": {"type": "object", "properties": schema, "required": required},
                },
            }
            return fn
        return deco

    def _handle(self, msg: dict):
        method, mid = msg.get("method"), msg.get("id")
        if mid is None:  # notifications (e.g. notifications/initialized) get no reply
            return None
        if method == "initialize":
            client_version = (msg.get("params") or {}).get("protocolVersion", PROTOCOL_VERSION)
            result = {
                "protocolVersion": client_version,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": self.name, "version": self.version},
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": [t["spec"] for t in self.tools.values()]}
        elif method == "tools/call":
            params = msg.get("params") or {}
            tool = self.tools.get(params.get("name"))
            if not tool:
                return _error(mid, -32602, f"unknown tool {params.get('name')!r}")
            try:
                out = tool["fn"](**(params.get("arguments") or {}))
                text = out if isinstance(out, str) else json.dumps(out, indent=1, ensure_ascii=False)
                result = {"content": [{"type": "text", "text": text}], "isError": False}
            except Exception as e:  # report tool failures to the model rather than crashing
                traceback.print_exc(file=sys.stderr)
                result = {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
        else:
            return _error(mid, -32601, f"method not found: {method}")
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def run(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                reply = self._handle(json.loads(line))
            except json.JSONDecodeError:
                reply = _error(None, -32700, "parse error")
            if reply is not None:
                sys.stdout.write(json.dumps(reply) + "\n")
                sys.stdout.flush()


def _error(mid, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

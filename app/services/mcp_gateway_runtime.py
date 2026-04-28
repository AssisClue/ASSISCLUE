from __future__ import annotations

_MCP_SERVER = None


def get_mcp_server():
    global _MCP_SERVER
    if _MCP_SERVER is None:
        from app.mcp.server import create_mcp_server
        _MCP_SERVER = create_mcp_server()
    return _MCP_SERVER


def reset_mcp_server() -> None:
    global _MCP_SERVER
    _MCP_SERVER = None
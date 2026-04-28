from __future__ import annotations

from app.mcp.server import create_mcp_server


def test_webautomation_tools_are_registered() -> None:
    server = create_mcp_server()
    snapshot = server.get_registry_snapshot()
    tool_names = {tool.name for tool in snapshot.tools}

    expected = {
        "web_open_url",
        "web_get_title",
        "web_extract_text",
        "web_capture_page",
        "web_save_page_html",
        "web_save_page_text",
        "web_search_duckduckgo",
        "web_click",
        "web_type",
        "web_press_key",
        "web_open_and_capture",
        "web_type_and_press",
        "web_search_and_capture",
        "web_search_and_extract",
        "web_session_start",
        "web_session_stop",
        "web_session_info",
        "web_session_open_url",
        "web_session_type",
        "web_session_click",
        "web_session_press_key",
        "web_session_extract_text",
        "web_session_capture_page",
        "web_session_list",
        "web_session_stop_all",
    }

    missing = expected - tool_names
    assert not missing, f"Missing webautomation tools: {sorted(missing)}"


def test_web_session_list_and_stop_all() -> None:
    server = create_mcp_server()

    start_result = server.call_tool("web_session_start", url="https://duckduckgo.com/")
    assert start_result.ok is True
    assert start_result.tool_name == "web_session_start"

    list_result = server.call_tool("web_session_list")
    assert list_result.ok is True
    assert list_result.tool_name == "web_session_list"
    assert list_result.data["count"] >= 1

    stop_all_result = server.call_tool("web_session_stop_all")
    assert stop_all_result.ok is True
    assert stop_all_result.tool_name == "web_session_stop_all"
    assert stop_all_result.data["closed_count"] >= 1
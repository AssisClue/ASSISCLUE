from __future__ import annotations

from app.mcp.server import create_mcp_server


EXPECTED_TOOLS = {
    "search_memory",
    "get_recent_context",
    "get_live_context",
    "get_user_profile_context",
    "get_task_context",
    "list_user_spaces",
    "get_user_space",
    "read_system_runtime_state",
    "read_llm_runtime_state",
    "read_recent_chat_history",
    "read_latest_response",
    "read_latest_tts",
    "read_latest_decision",
    "capture_screenshot",
    "capture_full_screenshot",
    "analyze_latest_screenshot",
    "analyze_current_screen",
    "read_text_file",
    "read_text_file_safe",
    "read_python_file",
    "read_json_file",
    "append_note",
    "overwrite_note",
    "read_context_snapshot",
    "read_memory_snapshot",
    "read_world_state",
    "read_context_runner_status",
    "read_context_runner_cursor",
    "list_capabilities",
    "get_capability_by_action_name",
    "list_personas",
    "get_persona",
    "get_active_persona_id",



}



def main() -> None:
    server = create_mcp_server()
    snapshot = server.get_registry_snapshot()
    names = {tool.name for tool in snapshot.tools}

    print(f"server={snapshot.server_name}")
    print(f"total_tools={snapshot.total_tools}")

    missing = sorted(EXPECTED_TOOLS - names)
    extra = sorted(names - EXPECTED_TOOLS)

    print(f"missing={missing}")
    print(f"extra={extra}")

    assert snapshot.total_tools == len(EXPECTED_TOOLS), (
        f"Expected {len(EXPECTED_TOOLS)} tools, got {snapshot.total_tools}"
    )
    assert not missing, f"Missing tools: {missing}"

    system_state_result = server.call_tool("read_system_runtime_state")
    assert getattr(system_state_result, "tool_name", "") == "read_system_runtime_state"

    safe_file_result = server.call_tool("read_text_file_safe", path="README.md")
    assert getattr(safe_file_result, "tool_name", "") == "read_text_file_safe"

    print("smoke_test=ok")


if __name__ == "__main__":
    main()
from __future__ import annotations

from pathlib import Path

from app.bootstrap import bootstrap_app
from app.context_memory import MemoryStorage, SessionMemory, UserProfileMemory
from app.schemas.memory_record import MemoryRecord
from app.services.assistant_service import answer_user
from app.memory.memory_service import maybe_store_memory
from app.services.mode_service import (
    get_runtime_mode_description,
    get_runtime_mode_flags,
)
from app.system_support.llm_runtime_state import load_llm_runtime_state
from app.system_support.runtime_files import (
    build_runtime_message_payload,
    write_runtime_json,
)
from app.system_support.runtime_jsonl import (
    append_runtime_jsonl,
    build_chat_history_item,
)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    result = bootstrap_app(project_root)

    print(result.message)
    print(f"ok={result.ok}")
    print(f"mode={result.runtime_state.current_mode}")
    print(f"persona={result.runtime_state.active_persona}")

    if not result.ok:
        return

    print(f"mode_description={get_runtime_mode_description(result.runtime_state.current_mode)}")
    print(f"mode_flags={get_runtime_mode_flags(result.runtime_state.current_mode)}")

    llm_state = load_llm_runtime_state(
        result.config.paths.runtime_dir / "state" / "llm_runtime_state.json"
    )
    if llm_state:
        print(f"llm_provider={llm_state.provider}")
        print(f"llm_model={llm_state.model_name}")
        print(f"llm_status={llm_state.status}")
        print(f"llm_error={llm_state.error or 'none'}")

    storage = MemoryStorage(
        result.config.paths.data_dir / "memory" / "memory_records.json"
    )
    session_memory = SessionMemory(session_id="demo_session")
    user_profile = UserProfileMemory()

    user_profile.add("Prefers short and organized answers.")
    user_profile.add("Likes clear structure.")
    session_memory.add_event("Assistant started successfully.")
    session_memory.add_event("User opened the app.")
    session_memory.add_event(f"Persona active: {result.runtime_state.active_persona}")
    session_memory.add_event(f"Mode active: {result.runtime_state.current_mode}")

    user_text = "Hello assistant, what do you know about how I like answers?"

    records: list[MemoryRecord] = storage.load_records()
    records = maybe_store_memory(
        "User likes concise, organized replies.",
        records,
        source="user_profile",
    )
    storage.save_records(records)

    append_runtime_jsonl(
        result.config.paths.runtime_dir / "output" / "chat_history.jsonl",
        build_chat_history_item(
            "user",
            user_text,
            persona=result.runtime_state.active_persona,
            source="main_demo",
        ),
    )

    write_runtime_json(
        result.config.paths.runtime_dir / "state" / "last_user_input.json",
        build_runtime_message_payload(
            user_text,
            extra={
                "source": "main_demo",
                "mode": result.runtime_state.current_mode,
                "persona": result.runtime_state.active_persona,
            },
        ),
    )

    answer = answer_user(
        user_text=user_text,
        persona_settings=result.config.persona,
        model_settings=result.config.models,
        session_events=session_memory.get_recent(),
        profile_items=user_profile.get_all(),
        memory_records=records,
        screenshot_notes=[],
    )

    write_runtime_json(
        result.config.paths.runtime_dir / "output" / "latest_response.json",
        build_runtime_message_payload(
            answer,
            extra={
                "mode": result.runtime_state.current_mode,
                "persona": result.runtime_state.active_persona,
                "model_name": result.config.models.llm_model_name,
            },
        ),
    )

    append_runtime_jsonl(
        result.config.paths.runtime_dir / "output" / "chat_history.jsonl",
        build_chat_history_item(
            "assistant",
            answer,
            persona=result.runtime_state.active_persona,
            model_name=result.config.models.llm_model_name,
            source="main_demo",
        ),
    )

    write_runtime_json(
        result.config.paths.runtime_dir / "state" / "session_snapshot.json",
        {
            "mode": result.runtime_state.current_mode,
            "persona": result.runtime_state.active_persona,
            "pending_tasks": result.runtime_state.pending_tasks,
            "memory_count": len(records),
            "profile_items": user_profile.get_all(),
            "recent_events": session_memory.get_recent(),
        },
    )

    print("\n--- RESPONSE ---")
    print(answer)


if __name__ == "__main__":
    main()
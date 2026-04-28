from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeServiceSpec:
    service_id: str
    display_name: str
    pid_key: str
    running_key: str
    process_needles: tuple[str, ...]
    panel_visible: bool = True
    status_relpath: tuple[str, ...] | None = None


UI_SERVICE_SPEC = RuntimeServiceSpec(
    service_id="ui",
    display_name="UI",
    pid_key="ui_pid",
    running_key="ui_running",
    process_needles=("uvicorn", "app.ui_local.app:app"),
    panel_visible=False,
)


BACKEND_SERVICE_SPECS: tuple[RuntimeServiceSpec, ...] = (
    RuntimeServiceSpec(
        service_id="inputfeed_to_text",
        display_name="InputFeed",
        pid_key="inputfeed_to_text_pid",
        running_key="inputfeed_to_text_running",
        process_needles=("app.inputfeed_to_text.inputfeed_to_text_service",),
        status_relpath=("status", "inputfeed_to_text_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="assembled_transcript_builder",
        display_name="Assembler",
        pid_key="assembled_transcript_builder_pid",
        running_key="assembled_transcript_builder_running",
        process_needles=("app.inputfeed_to_text.assembled_transcript_builder",),
        status_relpath=("status", "assembled_transcript_builder_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="primary_listener",
        display_name="Primary Listener",
        pid_key="primary_listener_pid",
        running_key="primary_listener_running",
        process_needles=("app.live_listeners.primary_listener.primary_listener_service",),
        status_relpath=("status", "primary_listener_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="administrative_listener",
        display_name="Admin Listener",
        pid_key="administrative_listener_pid",
        running_key="administrative_listener_running",
        process_needles=("app.live_listeners.administrative_listener.administrative_listener_service",),
        status_relpath=("status", "administrative_listener_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="browser_service",
        display_name="Browser",
        pid_key="browser_service_pid",
        running_key="browser_service_running",
        process_needles=("app.web_tools.browser.browser_service",),
        status_relpath=("status", "browser", "status.json"),
    ),
    RuntimeServiceSpec(
        service_id="raw_interrupt_listener",
        display_name="Raw Interrupt",
        pid_key="raw_interrupt_listener_pid",
        running_key="raw_interrupt_listener_running",
        process_needles=("app.live_listeners.primary_listener.raw_interrupt_listener",),
        status_relpath=("status", "raw_interrupt_listener_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="router_dispatch",
        display_name="Router",
        pid_key="router_dispatch_pid",
        running_key="router_dispatch_running",
        process_needles=("app.router_dispatch.router_service",),
        status_relpath=("status", "router_dispatch", "router_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="display_action_router",
        display_name="Display Actions",
        pid_key="display_action_router_pid",
        running_key="display_action_router_running",
        process_needles=("app.display_actions.runners.display_action_router",),
        status_relpath=("display_actions", "status", "display_action_runner_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="spoken_query_router",
        display_name="Spoken Queries",
        pid_key="spoken_query_router_pid",
        running_key="spoken_query_router_running",
        process_needles=("app.spoken_queries.runners.spoken_query_router",),
        status_relpath=("status", "spoken_queries", "spoken_query_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="context_memory_runtime",
        display_name="Context Memory",
        pid_key="context_memory_runtime_pid",
        running_key="context_memory_runtime_running",
        process_needles=("app.context_memory.runtime.context_memory_runtime_service",),
        status_relpath=("status", "memory", "context_memory_runtime_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="speech_queue_writer",
        display_name="Speech Queue",
        pid_key="speech_queue_writer_pid",
        running_key="speech_queue_writer_running",
        process_needles=("app.speech_out.speech_queue_writer",),
        status_relpath=("status", "speech_out", "speech_queue_writer_status.json"),
    ),
    RuntimeServiceSpec(
        service_id="speaker_service",
        display_name="TTS",
        pid_key="speaker_service_pid",
        running_key="speaker_service_running",
        process_needles=("app.speech_out.speaker_service",),
        status_relpath=("status", "speech_out", "speaker_status.json"),
    ),
)


def backend_service_specs(*, panel_only: bool = False) -> tuple[RuntimeServiceSpec, ...]:
    if not panel_only:
        return BACKEND_SERVICE_SPECS
    return tuple(spec for spec in BACKEND_SERVICE_SPECS if spec.panel_visible)


def stack_process_needles(*, include_ui: bool) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    if include_ui:
        for needle in UI_SERVICE_SPEC.process_needles:
            lowered = needle.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            ordered.append(needle)

    for spec in BACKEND_SERVICE_SPECS:
        for needle in spec.process_needles:
            lowered = needle.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            ordered.append(needle)

    return ordered


def expected_root_process_count(*, include_ui: bool) -> int:
    return len(BACKEND_SERVICE_SPECS) + (1 if include_ui else 0)


def starter_chain_text(*, include_ui: bool) -> str:
    labels: list[str] = []
    if include_ui:
        labels.append(UI_SERVICE_SPEC.service_id)
    labels.extend(spec.service_id for spec in BACKEND_SERVICE_SPECS)
    return " + ".join(labels)

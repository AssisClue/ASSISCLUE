from __future__ import annotations

from .capability_spec import CapabilitySpec


DEFAULT_CAPABILITIES: tuple[CapabilitySpec, ...] = (
    CapabilitySpec(
        capability_id="display.take_screenshot",
        action_name="take_screenshot",
        block_id="display_actions",
        target_queue="action_queue",
        target_runner="display_actions",
        handler_key="screenshot_capture",
    ),
    CapabilitySpec(
        capability_id="display.take_full_screenshot",
        action_name="take_full_screenshot",
        block_id="display_actions",
        target_queue="action_queue",
        target_runner="display_actions",
        handler_key="screenshot_capture",
    ),
    CapabilitySpec(
        capability_id="display.browser_screenshot",
        action_name="browser_screenshot",
        block_id="display_actions",
        target_queue="action_queue",
        target_runner="display_actions",
        handler_key="browser_screenshot",
    ),
    CapabilitySpec(
        capability_id="display.analyze_last_screenshot",
        action_name="analyze_last_screenshot",
        block_id="display_actions",
        target_queue="action_queue",
        target_runner="display_actions",
        handler_key="screenshot_analyze",
    ),
    CapabilitySpec(
        capability_id="system_controls.show_runtime_status",
        action_name="show_runtime_status",
        block_id="display_actions",
        target_queue="action_queue",
        target_runner="display_actions",
        handler_key="show_runtime_status",
    ),
    CapabilitySpec(
        capability_id="speech.stop_talking",
        action_name="stop_talking",
        block_id="speech_out",
        target_queue="action_queue",
        target_runner="display_actions",
        handler_key="stop_talking",
    ),
)
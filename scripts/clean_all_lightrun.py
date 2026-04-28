from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"


EMPTY_FILES = [
    "sacred/live_transcript_raw.jsonl",
    "sacred/live_transcript_history.jsonl",
    "queues/router_dispatch/router_input_queue.jsonl",
    "queues/router_dispatch/action_queue.jsonl",
    "queues/router_dispatch/response_queue.jsonl",
    "display_actions/results/display_action_results.jsonl",
    "queues/spoken_queries/spoken_query_results.jsonl",
    "queues/speech_out/speech_queue.jsonl",
    "queues/speech_out/spoken_history.jsonl",
]

EMPTY_JSON = [
    "sacred/live_transcript_raw_latest.json",
    "sacred/live_transcript_latest.json",
    "status/assembled_transcript_builder_status.json",
    "status/inputfeed_to_text_status.json",
    "status/primary_listener_status.json",
    "status/raw_interrupt_listener_status.json",
    "state/live_listeners/primary_listener_cursor.json",
    "state/live_listeners/raw_interrupt_listener_cursor.json",
    "state/live_listeners/administrative_listener_cursor.json",
    "state/live_listeners/context_runner_cursor.json",
    "status/router_dispatch/router_status.json",
    "display_actions/status/display_action_runner_status.json",
    "status/spoken_queries/spoken_query_status.json",
    "queues/speech_out/latest_tts.json",
    "state/speech_out/playback_state.json",
    "status/speech_out/speech_queue_writer_status.json",
    "status/speech_out/speaker_status.json",
    "output/latest_response.json",
    "state/session_snapshot.json",
]

DELETE_GLOBS = [
    "queues/speech_out/audio/*.wav",
    "queues/speech_out/audio/*.mp3",
    "queues/speech_out/audio/*.ogg",
    "input/audio_chunks/*.wav",
    "input/audio_chunks/*.json",
    "input/audio_chunks/*.txt",
]


def write_file(relative_path: str, content: str) -> None:
    path = RUNTIME / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"Cleaned: {path.relative_to(ROOT)}")


def main() -> None:
    print("LIGHT CLEAN RUNTIME")
    for relative_path in EMPTY_FILES:
        write_file(relative_path, "")
    for relative_path in EMPTY_JSON:
        write_file(relative_path, "{}")
    for pattern in DELETE_GLOBS:
        for path in RUNTIME.glob(pattern):
            path.unlink(missing_ok=True)
            print(f"Deleted: {path.relative_to(ROOT)}")
    print("LIGHT CLEAN COMPLETE")


if __name__ == "__main__":
    main()

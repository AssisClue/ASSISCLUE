from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any

import sounddevice as sd
from moonshine_voice import get_model_for_language
from moonshine_voice.mic_transcriber import MicTranscriber
from moonshine_voice.transcriber import TranscriptEventListener


def _device_matches(device: dict[str, Any], wanted: str) -> bool:
    if not wanted:
        return True
    return wanted.lower() in str(device.get("name", "")).lower()


def _candidate_devices(wanted: str) -> list[tuple[int, dict[str, Any]]]:
    preferred_hostapis = {3: 0, 2: 1, 1: 2, 0: 3}
    devices: list[tuple[int, dict[str, Any]]] = []
    for index, raw in enumerate(sd.query_devices()):
        device = dict(raw)
        if int(device.get("max_input_channels", 0) or 0) < 1:
            continue
        if not _device_matches(device, wanted):
            continue
        devices.append((index, device))
    devices.sort(key=lambda item: (preferred_hostapis.get(int(item[1].get("hostapi", 99)), 99), item[0]))
    return devices


def _can_open_input(index: int, device: dict[str, Any]) -> bool:
    try:
        stream = sd.InputStream(
            device=index,
            samplerate=int(float(device.get("default_samplerate", 16000) or 16000)),
            channels=1,
            dtype="float32",
            callback=lambda indata, frames, time_info, status: None,
            blocksize=1024,
        )
        stream.start()
        time.sleep(0.15)
        stream.stop()
        stream.close()
        return True
    except Exception:
        return False


def pick_input_device() -> tuple[int | None, int]:
    wanted = os.getenv("WINDOWS_MIC_DEVICE_NAME", "").strip()

    candidates = _candidate_devices(wanted)
    if not candidates and wanted:
        candidates = _candidate_devices("")

    for index, device in candidates:
        if _can_open_input(index, device):
            sample_rate = int(float(device.get("default_samplerate", 16000) or 16000))
            return index, sample_rate

    default_input, _default_output = sd.default.device
    return default_input, 16000


class PrintCompletedLines(TranscriptEventListener):
    def on_line_completed(self, event: Any) -> None:
        text = str(getattr(getattr(event, "line", None), "text", "") or "").strip()
        if text:
            print(text, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Moonshine mic runner with safe device selection.")
    parser.add_argument("--language", type=str, default="en")
    args = parser.parse_args()

    model_path, model_arch = get_model_for_language(wanted_language=args.language, wanted_model_arch=None)
    device_index, sample_rate = pick_input_device()

    transcriber = MicTranscriber(
        model_path=model_path,
        model_arch=model_arch,
        device=device_index,
        samplerate=sample_rate,
        channels=1,
        blocksize=1024,
    )
    transcriber.add_listener(PrintCompletedLines())
    transcriber.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        transcriber.stop()
        transcriber.close()


if __name__ == "__main__":
    main()

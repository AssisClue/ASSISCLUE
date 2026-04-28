from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioPlaybackError(RuntimeError):
    pass


def stop_playback() -> None:
    # Stops audio started by this process (PortAudio stream).
    try:
        sd.stop()
    except Exception:
        pass


def list_output_devices() -> list[dict]:
    devices = sd.query_devices()
    result: list[dict] = []

    for index, device in enumerate(devices):
        if int(device.get("max_output_channels", 0)) > 0:
            result.append(
                {
                    "index": index,
                    "name": str(device.get("name", "")),
                    "hostapi": device.get("hostapi"),
                    "max_output_channels": int(device.get("max_output_channels", 0)),
                    "default_samplerate": device.get("default_samplerate"),
                }
            )
    return result


def find_output_device_index(device_name_substring: Optional[str]) -> Optional[int]:
    devices = list_output_devices()

    if not device_name_substring:
        return None

    wanted = device_name_substring.strip().lower()

    for device in devices:
        if device["name"].strip().lower() == wanted:
            return int(device["index"])

    for device in devices:
        if wanted in device["name"].lower():
            return int(device["index"])

    return None


def play_wav_file(
    wav_path: str | Path,
    device_name_substring: Optional[str] = None,
    blocking: bool = True,
    gain: float = 1.0,
) -> dict:
    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise AudioPlaybackError(f"WAV not found: {wav_path}")

    data, samplerate = sf.read(str(wav_path), dtype="float32", always_2d=False)

    if gain != 1.0:
        data = np.clip(data * float(gain), -1.0, 1.0)

    device_index = find_output_device_index(device_name_substring)
    if device_name_substring and device_index is None:
        raise AudioPlaybackError(f"Output device not found: {device_name_substring}")

    try:
        sd.play(data, samplerate=samplerate, device=device_index, blocking=blocking)
    except Exception as exc:
        raise AudioPlaybackError(
            f"Failed to play WAV on device '{device_name_substring}': {exc}"
        ) from exc

    return {
        "ok": True,
        "wav_path": str(wav_path),
        "device_name_substring": device_name_substring,
        "device_index": device_index,
        "blocking": blocking,
        "gain": gain,
        "samplerate": samplerate,
    }

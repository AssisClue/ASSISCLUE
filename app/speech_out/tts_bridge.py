from __future__ import annotations

import time
import wave
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from kokoro import KPipeline

from app.services.audio_playback import stop_playback
from app.services.audio_playback import play_wav_file
from app.services.speech_service import prepare_tts_text, should_skip_tts
from app.config import AppConfig
from app.settings.tts_settings import TTSSettings


_KOKORO_PIPELINES: dict[str, KPipeline] = {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        __import__("json").dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _stop_requested_after(path: Path, after_ts: float) -> float | None:
    stop_path = path.parent / "stop_request.json"
    if not stop_path.exists():
        return None
    try:
        # Tolerate an accidental UTF-8 BOM (e.g., if written by PowerShell).
        payload = __import__("json").loads(stop_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    try:
        ts = float(payload.get("ts", 0.0) or 0.0)
    except Exception:
        return None
    return ts if ts > float(after_ts or 0.0) else None


def _get_kokoro_pipeline(lang_code: str) -> KPipeline:
    pipeline = _KOKORO_PIPELINES.get(lang_code)
    if pipeline is None:
        pipeline = KPipeline(lang_code=lang_code)
        _KOKORO_PIPELINES[lang_code] = pipeline
    return pipeline


def _wav_duration_seconds(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as handle:
            frames = handle.getnframes()
            rate = handle.getframerate()
            if rate <= 0:
                return 0.0
            return frames / float(rate)
    except Exception:
        try:
            info = sf.info(str(path))
            if info.samplerate > 0:
                return float(info.frames) / float(info.samplerate)
        except Exception:
            return 0.0
    return 0.0


def _synthesize_with_kokoro(
    *,
    text: str,
    output_path: Path,
    lang_code: str,
    voice: str,
    sample_rate: int,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pipeline = _get_kokoro_pipeline(lang_code)
    generator = pipeline(text, voice=voice)

    audio_chunks: list[np.ndarray] = []
    for _, _, audio in generator:
        audio_chunks.append(np.asarray(audio, dtype=np.float32))

    if not audio_chunks:
        raise RuntimeError("Kokoro returned no audio.")

    final_audio = np.concatenate(audio_chunks)
    sf.write(str(output_path), final_audio, sample_rate)

    return {
        "backend": "kokoro",
        "voice": voice,
        "lang_code": lang_code,
        "sample_rate": sample_rate,
        "output_path": str(output_path),
        "audio_samples": int(final_audio.shape[0]),
    }


def synthesize_and_play_speech(
    *,
    config: AppConfig,
    tts_settings: TTSSettings,
    text: str,
    output_path: Path,
    latest_tts_path: Path,
    playback_state_path: Path,
) -> dict[str, Any]:
    started_at = time.time()
    cleaned_text = prepare_tts_text(text)

    if should_skip_tts(cleaned_text):
        record = {
            "ts": started_at,
            "status": "skipped",
            "reason": "empty_text",
            "text": text,
            "spoken_text": "",
            "output_path": "",
            "elapsed_seconds": 0.0,
            "playback_result": {
                "ok": False,
                "backend": "none",
                "blocking": True,
                "error": "Empty text.",
            },
        }
        _write_json(latest_tts_path, record)
        _write_json(
            playback_state_path,
            {
                "ts": started_at,
                "status": "idle",
                "spoken_text": "",
                "text": text,
                "updated_at": started_at,
            },
        )
        return record

    _write_json(
        playback_state_path,
        {
            "ts": started_at,
            "status": "synthesizing",
            "spoken_text": cleaned_text,
            "text": text,
            "output_path": str(output_path),
            "updated_at": started_at,
        },
    )

    synth_info = _synthesize_with_kokoro(
        text=cleaned_text,
        output_path=output_path,
        lang_code=tts_settings.kokoro_lang_code,
        voice=tts_settings.kokoro_voice,
        sample_rate=tts_settings.sample_rate,
    )

    stop_ts = _stop_requested_after(playback_state_path, started_at)
    if stop_ts is not None:
        try:
            (playback_state_path.parent / "stop_request.json").unlink()
        except Exception:
            pass
        finished_at = time.time()
        record = {
            "ts": finished_at,
            "status": "stopped",
            "reason": "stop_requested_before_playback",
            "text": text,
            "spoken_text": cleaned_text,
            "output_path": str(output_path),
            "elapsed_seconds": round(finished_at - started_at, 4),
            "duration_seconds": 0.0,
            "backend": synth_info["backend"],
            "voice": synth_info["voice"],
            "lang_code": synth_info["lang_code"],
            "sample_rate": synth_info["sample_rate"],
            "blocking": bool(config.audio.tts_playback_blocking),
            "playback_result": {"ok": True, "backend": "stopped", "blocking": bool(config.audio.tts_playback_blocking)},
        }
        _write_json(latest_tts_path, record)
        _write_json(
            playback_state_path,
            {
                "ts": finished_at,
                "status": "idle",
                "spoken_text": cleaned_text,
                "text": text,
                "output_path": str(output_path),
                "updated_at": finished_at,
                "stopped_by_user": True,
                "stop_request_ts": stop_ts,
            },
        )
        return record

    duration_seconds = _wav_duration_seconds(output_path)
    playing_started_at = time.time()

    _write_json(
        playback_state_path,
        {
            "ts": playing_started_at,
            "status": "playing",
            "spoken_text": cleaned_text,
            "text": text,
            "output_path": str(output_path),
            "updated_at": playing_started_at,
            "started_at": playing_started_at,
            "until_ts": playing_started_at + duration_seconds,
            "duration_seconds": duration_seconds,
            "backend": synth_info["backend"],
            "voice": synth_info["voice"],
            "lang_code": synth_info["lang_code"],
            "blocking": bool(config.audio.tts_playback_blocking),
        },
    )

    if bool(config.audio.tts_playback_enabled):
        stop_ts = _stop_requested_after(playback_state_path, started_at)
        if stop_ts is not None:
            try:
                (playback_state_path.parent / "stop_request.json").unlink()
            except Exception:
                pass
            playback_result = {
                "ok": True,
                "backend": "stopped",
                "blocking": bool(config.audio.tts_playback_blocking),
                "stop_request_ts": stop_ts,
            }
        else:
            playback_result = play_wav_file(
                output_path,
                device_name_substring=config.audio.tts_output_device_name or None,
                blocking=False,
                gain=float(config.audio.tts_output_gain),
            )
            if bool(config.audio.tts_playback_blocking):
                while time.time() < (playing_started_at + duration_seconds):
                    stop_ts = _stop_requested_after(playback_state_path, started_at)
                    if stop_ts is not None:
                        stop_playback()
                        playback_result = {
                            **playback_result,
                            "stopped_by_user": True,
                            "stop_request_ts": stop_ts,
                        }
                        try:
                            (playback_state_path.parent / "stop_request.json").unlink()
                        except Exception:
                            pass
                        break
                    time.sleep(0.05)
    else:
        playback_result = {
            "ok": True,
            "backend": "disabled",
            "blocking": bool(config.audio.tts_playback_blocking),
            "device_name_substring": config.audio.tts_output_device_name,
            "gain": float(config.audio.tts_output_gain),
            "samplerate": synth_info["sample_rate"],
        }

    finished_at = time.time()

    _write_json(
        playback_state_path,
        {
            "ts": finished_at,
            "status": "idle",
            "spoken_text": cleaned_text,
            "text": text,
            "output_path": str(output_path),
            "updated_at": finished_at,
            "started_at": playing_started_at,
            "until_ts": playing_started_at + duration_seconds,
            "duration_seconds": duration_seconds,
            "backend": synth_info["backend"],
            "voice": synth_info["voice"],
            "lang_code": synth_info["lang_code"],
            "blocking": bool(config.audio.tts_playback_blocking),
            "playback_result": playback_result,
        },
    )

    record = {
        "ts": finished_at,
        "status": "ok" if playback_result.get("ok") else "playback_error",
        "text": text,
        "spoken_text": cleaned_text,
        "output_path": str(output_path),
        "elapsed_seconds": round(finished_at - started_at, 4),
        "duration_seconds": duration_seconds,
        "backend": synth_info["backend"],
        "voice": synth_info["voice"],
        "lang_code": synth_info["lang_code"],
        "sample_rate": synth_info["sample_rate"],
        "blocking": bool(config.audio.tts_playback_blocking),
        "playback_result": playback_result,
    }
    _write_json(latest_tts_path, record)
    return record

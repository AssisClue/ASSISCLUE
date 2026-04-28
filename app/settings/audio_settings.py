from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class AudioSettings:
    enable_mic: bool = True
    enable_system_audio: bool = True
    wake_word: str = "hey assistant"

    silence_timeout: float = 0.75
    audio_chunk_seconds: float = 0.3
    vad_enabled: bool = True
    # Fix language to reduce garbage / wrong-language guesses in live mic.
    stt_language: str = "en"

    input_sample_rate: int = 16000
    input_channels: int = 1

    stt_device: str = "auto"
    stt_compute_type: str = "auto"
    stt_beam_size: int = 1

    tts_output_format: str = "wav"
    tts_rate: int = 180

    ## TV AUDIO SPEAKER
    tts_playback_enabled: bool = True
    tts_output_device_name: str = "1 - HISENSE (AMD High Definition Audio Device)" if os.name == "nt" else ""
    tts_playback_blocking: bool = True
    tts_output_gain: float = 1.0


    # LIVE CAPTURE TUNABLES
    stt_live_enabled: bool = True
    stt_live_source: str = "mic"  # system | mic | wav /"Microphone (AudioPro X5 Microphone)"
    stt_live_chunk_seconds: float = 1.4
    stt_live_chunk_overlap_seconds: float = 0.35
    stt_live_temp_dir_name: str = "audio_chunks"
    stt_live_keep_temp_files: bool = False
    stt_live_max_queue_size: int = 6
    stt_live_frames_per_buffer: int = 1024
    stt_live_input_gain: float = 2.1
    stt_live_consumer_poll_seconds: float = 0.05
    stt_live_silence_finalize_seconds: float = 0.8
    stt_live_max_turn_seconds: float = 8.0
    stt_live_voice_peak_dbfs: float = -72.0
    stt_live_short_phrase_confidence: float = 0.42
    stt_live_short_phrase_peak_dbfs: float = -78.0

    # LIVE TRANSCRIPT QUALITY GATES (to reduce TV/noise garbage)
    stt_live_min_confidence: float = 0.2
    stt_live_min_letters: int = 3
    stt_live_min_words: int = 1
    stt_live_max_nonalpha_ratio: float = 0.7
    stt_live_vad_style_gate_enabled: bool = True
    stt_live_voice_start_min_peak_dbfs: float = -71.0
    stt_live_voice_continue_min_peak_dbfs: float = -78.0
    stt_live_voice_start_min_confidence: float = 0.22
    stt_live_voice_start_chunks_required: int = 1
    stt_live_voice_end_silence_seconds: float = 0.9

    # WINDOWS CAPTURE TUNABLES
    windows_input_device_name: str = "" ## "1 - HISENSE (AMD High Definition Audio Device) [Loopback]"
    # Use a substring that exists in the Windows device list (stable match).
    # This prevents Windows "default mic" surprises.
    windows_mic_device_name: str = "AudioPro X5" if os.name == "nt" else ""
    windows_loopback_enabled: bool = True
    windows_exclusive_mode: bool = False

    # FALLBACKS
    stt_fallback_to_wav_file: bool = True

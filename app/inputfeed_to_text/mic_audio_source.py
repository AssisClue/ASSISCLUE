from __future__ import annotations

import audioop
from dataclasses import dataclass
from typing import Any

from .audio_settings import InputFeedAudioSettings
from .preprocess.rnnoise_preprocessor import RNNoisePreprocessor


@dataclass(slots=True)
class PCMChunkResult:
    pcm_bytes: bytes
    sample_rate: int
    channels: int
    sample_width: int
    metadata: dict[str, Any]


class WasapiMicAudioSource:
    def __init__(self, settings: InputFeedAudioSettings | None = None) -> None:
        import pyaudiowpatch as pyaudio  # type: ignore

        self.settings = settings or InputFeedAudioSettings()
        self._pyaudio = pyaudio
        self._pa = pyaudio.PyAudio()
        self._stream = None
        self._device_info: dict[str, Any] | None = None
        self._device_rate = self.settings.input_sample_rate
        self._device_channels = self.settings.input_channels
        self._rnnoise = RNNoisePreprocessor(enabled=self.settings.enable_rnnoise)
        self._rnnoise_bypass_min_raw_rms = 180
        self._rnnoise_bypass_max_ratio = 0.35

    def _list_devices(self) -> list[dict[str, Any]]:
        devices: list[dict[str, Any]] = []
        count = self._pa.get_device_count()

        for index in range(count):
            try:
                info = self._pa.get_device_info_by_index(index)
                devices.append(
                    {
                        "index": info.get("index", index),
                        "name": str(info.get("name", "")),
                        "maxInputChannels": int(info.get("maxInputChannels", 0) or 0),
                        "defaultSampleRate": int(float(info.get("defaultSampleRate", self.settings.input_sample_rate))),
                    }
                )
            except Exception:
                continue

        return devices

    def _resolve_mic_device(self) -> dict[str, Any]:
        wanted = self.settings.windows_mic_device_name.strip().lower()

        if wanted:
            for device in self._list_devices():
                name = str(device.get("name", ""))
                max_inputs = int(device.get("maxInputChannels", 0) or 0)
                if wanted in name.lower() and max_inputs > 0:
                    return device

        return self._pa.get_default_input_device_info()

    def open(self) -> None:
        if self._stream is not None:
            return

        device_info = self._resolve_mic_device()
        device_index = int(device_info["index"])
        device_rate = int(float(device_info.get("defaultSampleRate", self.settings.input_sample_rate)))
        input_channels = int(device_info.get("maxInputChannels", 1) or 1)
        input_channels = max(1, min(input_channels, 2))

        self._stream = self._pa.open(
            format=self._pyaudio.paInt16,
            channels=input_channels,
            rate=device_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.settings.frames_per_buffer,
        )

        self._device_info = dict(device_info)
        self._device_rate = device_rate
        self._device_channels = input_channels

    def read_chunk(self, chunk_seconds: float) -> bytes:
        chunk = self.read_chunk_result(chunk_seconds)
        return chunk.pcm_bytes

    def read_chunk_result(self, chunk_seconds: float) -> PCMChunkResult:
        self.open()

        assert self._stream is not None
        assert self._device_info is not None

        total_frames = int(self._device_rate * chunk_seconds)
        frames: list[bytes] = []
        remaining = total_frames

        while remaining > 0:
            current = min(self.settings.frames_per_buffer, remaining)
            data = self._stream.read(current, exception_on_overflow=False)
            frames.append(data)
            remaining -= current

        raw_pcm = b"".join(frames)
        pcm = raw_pcm
        channels = self._device_channels

        if self._device_channels == 2 and self.settings.input_channels == 1:
            pcm = audioop.tomono(raw_pcm, self.settings.sample_width, 0.5, 0.5)
            channels = 1

        if self._device_rate != self.settings.input_sample_rate:
            pcm, _ = audioop.ratecv(
                pcm,
                self.settings.sample_width,
                channels,
                self._device_rate,
                self.settings.input_sample_rate,
                None,
            )

        if self.settings.input_gain != 1.0 and pcm:
            pcm = audioop.mul(pcm, self.settings.sample_width, self.settings.input_gain)

        rnnoise_result = self._rnnoise.process_pcm_bytes(
            pcm,
            sample_rate=self.settings.input_sample_rate,
            channels=self.settings.input_channels,
            sample_width=self.settings.sample_width,
        )
        raw_rms = audioop.rms(pcm, self.settings.sample_width) if pcm else 0
        denoised_pcm = rnnoise_result.pcm_bytes
        denoised_rms = audioop.rms(denoised_pcm, self.settings.sample_width) if denoised_pcm else 0

        rnnoise_backend = rnnoise_result.backend
        rnnoise_error = rnnoise_result.error
        rnnoise_active = rnnoise_result.active

        if (
            rnnoise_result.active
            and raw_rms >= self._rnnoise_bypass_min_raw_rms
            and (denoised_rms / max(raw_rms, 1)) < self._rnnoise_bypass_max_ratio
        ):
            rnnoise_active = False
            rnnoise_backend = "rnnoise_bypass_low_energy"
            rnnoise_error = ""
        else:
            pcm = denoised_pcm

        return PCMChunkResult(
            pcm_bytes=pcm,
            sample_rate=self.settings.input_sample_rate,
            channels=self.settings.input_channels,
            sample_width=self.settings.sample_width,
            metadata={
                "device_name": str(self._device_info.get("name", "")),
                "device_default_sample_rate": self._device_rate,
                "frames_per_buffer": self.settings.frames_per_buffer,
                "input_gain": self.settings.input_gain,
                "source_backend": self.settings.source_backend,
                "rnnoise_enabled": self.settings.enable_rnnoise,
                "rnnoise_available": self._rnnoise.available,
                "rnnoise_active": rnnoise_active,
                "rnnoise_backend": rnnoise_backend,
                "rnnoise_error": rnnoise_error,
                "rnnoise_speech_prob_mean": rnnoise_result.speech_prob_mean,
                "rnnoise_raw_rms": raw_rms,
                "rnnoise_denoised_rms": denoised_rms,
            },
        )

    def close(self) -> None:
        if self._stream is not None:
            try:
                self._stream.stop_stream()
            except Exception:
                pass
            try:
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        try:
            self._pa.terminate()
        except Exception:
            pass


class SoundDeviceMicAudioSource:
    def __init__(self, settings: InputFeedAudioSettings | None = None) -> None:
        import sounddevice as sd

        self.settings = settings or InputFeedAudioSettings()
        self._sd = sd
        self._stream = None
        self._device_info: dict[str, Any] | None = None
        self._device_rate = self.settings.input_sample_rate
        self._device_channels = self.settings.input_channels
        self._rnnoise = RNNoisePreprocessor(enabled=self.settings.enable_rnnoise)

    def _resolve_mic_device(self) -> tuple[int | None, dict[str, Any]]:
        wanted = self.settings.windows_mic_device_name.strip().lower()
        devices = [dict(raw) for raw in self._sd.query_devices()]
        for index, device in enumerate(devices):
            name = str(device.get("name", ""))
            if int(device.get("max_input_channels", 0) or 0) > 0 and (not wanted or wanted in name.lower()):
                return index, device
        default_input, _default_output = self._sd.default.device
        index = int(default_input) if default_input is not None else None
        return index, dict(devices[index]) if index is not None and 0 <= index < len(devices) else {}

    def open(self) -> None:
        if self._stream is not None:
            return

        device_index, device_info = self._resolve_mic_device()
        device_rate = int(float(device_info.get("default_samplerate", self.settings.input_sample_rate) or self.settings.input_sample_rate))
        channels = min(max(int(device_info.get("max_input_channels", 1) or 1), 1), 2)
        self._stream = self._sd.RawInputStream(
            device=device_index,
            samplerate=device_rate,
            channels=channels,
            dtype="int16",
            blocksize=self.settings.frames_per_buffer,
        )
        self._stream.start()
        self._device_info = {"index": device_index, "name": str(device_info.get("name", ""))}
        self._device_rate = device_rate
        self._device_channels = channels

    def read_chunk(self, chunk_seconds: float) -> bytes:
        return self.read_chunk_result(chunk_seconds).pcm_bytes

    def read_chunk_result(self, chunk_seconds: float) -> PCMChunkResult:
        self.open()
        assert self._stream is not None
        assert self._device_info is not None

        data, overflowed = self._stream.read(int(self._device_rate * chunk_seconds))
        pcm = bytes(data)
        channels = self._device_channels

        if channels == 2 and self.settings.input_channels == 1:
            pcm = audioop.tomono(pcm, self.settings.sample_width, 0.5, 0.5)
            channels = 1
        if self._device_rate != self.settings.input_sample_rate:
            pcm, _ = audioop.ratecv(
                pcm,
                self.settings.sample_width,
                channels,
                self._device_rate,
                self.settings.input_sample_rate,
                None,
            )
        if self.settings.input_gain != 1.0 and pcm:
            pcm = audioop.mul(pcm, self.settings.sample_width, self.settings.input_gain)

        rnnoise_result = self._rnnoise.process_pcm_bytes(
            pcm,
            sample_rate=self.settings.input_sample_rate,
            channels=self.settings.input_channels,
            sample_width=self.settings.sample_width,
        )
        raw_rms = audioop.rms(pcm, self.settings.sample_width) if pcm else 0
        pcm = rnnoise_result.pcm_bytes

        return PCMChunkResult(
            pcm_bytes=pcm,
            sample_rate=self.settings.input_sample_rate,
            channels=self.settings.input_channels,
            sample_width=self.settings.sample_width,
            metadata={
                "device_name": str(self._device_info.get("name", "")),
                "device_default_sample_rate": self._device_rate,
                "frames_per_buffer": self.settings.frames_per_buffer,
                "input_gain": self.settings.input_gain,
                "source_backend": self.settings.source_backend,
                "read_overflowed": bool(overflowed),
                "rnnoise_enabled": self.settings.enable_rnnoise,
                "rnnoise_available": self._rnnoise.available,
                "rnnoise_active": rnnoise_result.active,
                "rnnoise_backend": rnnoise_result.backend,
                "rnnoise_error": rnnoise_result.error,
                "rnnoise_speech_prob_mean": rnnoise_result.speech_prob_mean,
                "rnnoise_raw_rms": raw_rms,
                "rnnoise_denoised_rms": audioop.rms(pcm, self.settings.sample_width) if pcm else 0,
            },
        )

    def close(self) -> None:
        if self._stream is None:
            return
        try:
            self._stream.stop()
            self._stream.close()
        except Exception:
            pass
        self._stream = None


def create_mic_audio_source(settings: InputFeedAudioSettings | None = None) -> WasapiMicAudioSource | SoundDeviceMicAudioSource:
    resolved = settings or InputFeedAudioSettings()
    if resolved.source_backend == "windows_wasapi_mic":
        return WasapiMicAudioSource(resolved)
    return SoundDeviceMicAudioSource(resolved)

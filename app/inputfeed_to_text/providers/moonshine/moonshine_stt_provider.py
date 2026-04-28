from __future__ import annotations

import subprocess
import sys
import time

from ...inputfeed_settings import (
    INPUTFEED_DEDUP_SECONDS,
    TRANSCRIPT_SESSION_ID,
    TRANSCRIPT_SOURCE_NAME,
    TRANSCRIPT_SOURCE_TYPE,
)
from ...transcript_runtime import (
    append_raw_transcript_line,
    archive_and_reset_live_transcript,
    write_inputfeed_status,
)
from ..base_stt_provider import BaseSTTProvider
from .moonshine_settings import MoonshineSettings


class MoonshineSTTProvider(BaseSTTProvider):
    def __init__(self) -> None:
        self.settings = MoonshineSettings()
        self._running = False
        self._process: subprocess.Popen[str] | None = None
        self._last_written_text = ""
        self._last_written_ts = 0.0
        self.session_id = TRANSCRIPT_SESSION_ID

    def _normalize_line(self, raw: str) -> str:
        text = (raw or "").strip()
        if not text:
            return ""

        ignored_prefixes = (
            "Listening to the microphone",
            "adapter.ort:",
            "cross_kv.ort:",
            "decoder_kv.ort:",
            "decoder_kv_with_attention.ort:",
            "encoder.ort:",
            "frontend.ort:",
            "streaming_config.json:",
            "tokenizer.bin:",
        )
        if text.startswith(ignored_prefixes):
            return ""

        if text.startswith("MicTranscriber: input overflow"):
            return ""

        if ":" in text and text.startswith("Speaker #"):
            text = text.split(":", 1)[1].strip()

        return " ".join(text.split())

    def _should_skip_text(self, text: str) -> bool:
        if not text:
            return True

        now_ts = time.time()
        if text == self._last_written_text and (now_ts - self._last_written_ts) < INPUTFEED_DEDUP_SECONDS:
            return True

        return False

    def run_forever(self) -> None:
        self._running = True

        write_inputfeed_status(
            "starting",
            session_id=self.session_id,
            source=TRANSCRIPT_SOURCE_NAME,
            source_type=TRANSCRIPT_SOURCE_TYPE,
            language=self.settings.language,
            stt_backend="moonshine",
            provider_mode="external_mic_transcriber",
        )

        try:
            cmd = [
                sys.executable,
                "-u",
                "-m",
                "moonshine_voice.mic_transcriber",
                "--language",
                self.settings.language,
            ]

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            write_inputfeed_status(
                "running",
                session_id=self.session_id,
                source=TRANSCRIPT_SOURCE_NAME,
                source_type=TRANSCRIPT_SOURCE_TYPE,
                language=self.settings.language,
                stt_backend="moonshine",
                provider_mode="external_mic_transcriber",
                last_event="moonshine_started",
            )

            assert self._process.stdout is not None

            for raw_line in self._process.stdout:
                if not self._running:
                    break

                line = self._normalize_line(raw_line)
                if not line:
                    if "input overflow" in raw_line.lower():
                        write_inputfeed_status(
                            "running",
                            session_id=self.session_id,
                            source=TRANSCRIPT_SOURCE_NAME,
                            stt_backend="moonshine",
                            last_event="input_overflow",
                        )
                    continue

                if self._should_skip_text(line):
                    write_inputfeed_status(
                        "running",
                        session_id=self.session_id,
                        source=TRANSCRIPT_SOURCE_NAME,
                        stt_backend="moonshine",
                        last_event="dedup_text",
                        last_text=line,
                    )
                    continue

                record = append_raw_transcript_line(
                    source=TRANSCRIPT_SOURCE_NAME,
                    session_id=self.session_id,
                    text=line,
                    language=self.settings.language,
                    metadata={
                        "model_name": "moonshine",
                        "source_type": TRANSCRIPT_SOURCE_TYPE,
                        "stt_backend": "moonshine",
                    },
                )

                self._last_written_text = record["text"]
                self._last_written_ts = float(record["ts"] or time.time())

                write_inputfeed_status(
                    "running",
                    session_id=self.session_id,
                    source=TRANSCRIPT_SOURCE_NAME,
                    source_type=TRANSCRIPT_SOURCE_TYPE,
                    language=self.settings.language,
                    stt_backend="moonshine",
                    last_event="transcript_written",
                    last_event_id=record["event_id"],
                    last_text=record["text"],
                )

            returncode = self._process.wait(timeout=1.0)
            if self._running and returncode != 0:
                raise RuntimeError(f"Moonshine exited with code {returncode}")

        except KeyboardInterrupt:
            write_inputfeed_status(
                "stopped",
                session_id=self.session_id,
                source=TRANSCRIPT_SOURCE_NAME,
                reason="keyboard_interrupt",
                stt_backend="moonshine",
            )

        except Exception as exc:
            write_inputfeed_status(
                "error",
                session_id=self.session_id,
                source=TRANSCRIPT_SOURCE_NAME,
                stt_backend="moonshine",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise

        finally:
            self.stop()
            archive_info = archive_and_reset_live_transcript(session_id=self.session_id)
            write_inputfeed_status(
                "stopped",
                session_id=self.session_id,
                source=TRANSCRIPT_SOURCE_NAME,
                stt_backend="moonshine",
                archived=bool(archive_info),
                archive_path=archive_info.get("raw_archive_path"),
            )

    def stop(self) -> None:
        self._running = False
        if self._process is not None:
            try:
                self._process.terminate()
            except Exception:
                pass
            self._process = None
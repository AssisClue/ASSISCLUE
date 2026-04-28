# speech_out

## Que hace

Este modulo hace una sola cosa:
texto final -> audio (TTS) -> lo reproduce.

No decide que decir. No hace router. No hace memoria.

## Cadena (simple)

1) `speech_queue_writer.py` lee resultados y arma la cola
2) `speaker_service.py` consume la cola
3) `tts_bridge.py` sintetiza (Kokoro) y reproduce (playback)

## Archivos

- `speech_queue_writer.py`: escribe `runtime/queues/speech_out/speech_queue.jsonl`
- `speaker_service.py`: lee `speech_queue.jsonl`, genera wav, actualiza status
- `tts_bridge.py`: TTS (Kokoro) + playback usando `app/services/audio_playback.py`
- `schemas/speech_queue_schema.py`: schema de los items de cola

## Runtime (archivos que aparecen)

- `runtime/queues/speech_out/speech_queue.jsonl` (cola)
- `runtime/queues/speech_out/spoken_history.jsonl` (historial de lo hablado)
- `runtime/queues/speech_out/latest_tts.json` (ultimo TTS)
- `runtime/state/speech_out/playback_state.json` (estado: synthesizing/playing/idle)
- `runtime/queues/speech_out/audio/*.wav` (wavs generados)
- `runtime/status/speech_out/speech_queue_writer_status.json`
- `runtime/status/speech_out/speaker_status.json`

## Nombres parecidos (no se pisan)

- `app/services/speech_service.py` NO es un proceso: solo limpia texto (helper).
- `app/speech_out/speaker_service.py` SI es el servicio que habla (proceso).

## Settings (lo minimo)

- TTS (env): `ASSISCLUE_TTS_BACKEND`, `ASSISCLUE_KOKORO_LANG`, `ASSISCLUE_KOKORO_VOICE`, `ASSISCLUE_TTS_SAMPLE_RATE`
- Playback (codigo): `app/settings/audio_settings.py` via `AppConfig` (device, gain, blocking, enabled)

# inputfeed_to_text

## Que es

Este modulo convierte audio -> texto (transcript) en vivo.

Flujo:
1) lee audio (ej: microfono Windows WASAPI)
2) arma chunks
3) STT (por backend): `moonshine` o `whisper` (faster-whisper)
4) escribe runtime (history + latest) y status
5) al cerrar: archiva y limpia los live files

No hace wakeword, comandos, router, memoria, TTS, ni logica de negocio. Termina en "texto".

## Archivos importantes

- `inputfeed_to_text_service.py`: loop principal (lee audio, VAD/streaming, STT, escribe runtime/status)
- `mic_audio_source.py`: fuente de audio + preprocesado RNNoise (opcional)
- `vad/silero_vad_gate.py`: gate VAD Silero (opcional)
- `streaming/whisper_stream_adapter.py`: modo streaming (opcional)
- `transcript_runtime.py`: escribe/archiva `jsonl/json` del runtime
- `inputfeed_settings.py`: variables ENV + paths de runtime
- `providers/moonshine/moonshine_stt_provider.py`: backend "moonshine" (proceso externo)

## Runtime que genera

- `runtime/sacred/live_transcript_history.jsonl` (append-only)
- `runtime/sacred/live_transcript_latest.json` (ultimo evento)
- `runtime/status/inputfeed_to_text_status.json` (estado: running/error + metadata)
- `runtime/stt_archive/YYYY/MM/DD/session_<session_id>__HH-MM-SS.jsonl` (archivo al cerrar)

## Variables ENV (las mas utiles)

- `INPUTFEED_STT_BACKEND`: `moonshine` (default) o `whisper`
- `INPUTFEED_USE_STREAMING`: `true/false`
- `INPUTFEED_ENABLE_SILERO_VAD`: `true/false`
- `INPUTFEED_ENABLE_RNNOISE`: `1/0`
- `STT_MODEL`, `STT_LANGUAGE`, `STT_COMPUTE_TYPE`, `STT_BEAM_SIZE`, `STT_VAD_FILTER`
- `TRANSCRIPT_SESSION_ID`, `TRANSCRIPT_SOURCE_NAME`, `TRANSCRIPT_SOURCE_TYPE`
- `WINDOWS_MIC_DEVICE_NAME`, `INPUTFEED_SOURCE_BACKEND`

## Schema (cada linea del history .jsonl)

```json
{"event_id":"evt_...","ts":1712345678.901,"session_id":"session_...","source":"audio_input","text":"hello","language":"en","metadata":{"stt_backend":"whisper","model_name":"medium","chunk_seconds":1.2}}
```

## Notas rapidas

- En Windows no importa el nombre de carpeta. En Linux SI: `inputfeed_to_Text` y `inputfeed_to_text` son distintos.
- `providers/whisper/` hoy esta vacio: whisper se usa directo con `faster_whisper` en el servicio/stream adapter.
- Existe `inputfeed_to_text_service copy.py`: parece archivo viejo/copia; no lo uses como fuente de verdad.

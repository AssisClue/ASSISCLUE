# inputfeed_to_text

## Que es

Este modulo convierte audio en texto vivo.

Piensa en este bloque como el "oido" del app:

1. abre el microfono
2. lee audio en pedazos pequenos
3. limpia o filtra ruido si esta activado
4. manda el audio al STT
5. escribe transcript en `runtime/sacred`
6. escribe status en `runtime/status`

No decide comandos, memoria, persona, router, HELP, ni TTS. Este modulo solo produce texto.

## Flujo real

```txt
microfono
  -> mic_audio_source.py
  -> RNNoise opcional
  -> Silero VAD opcional
  -> Moonshine o Whisper
  -> transcript_runtime.py
  -> runtime/sacred/*.jsonl y *.json
  -> assembled_transcript_builder.py une frases cercanas
```

## Archivos principales

- `inputfeed_to_text_service.py`: servicio principal de STT vivo.
- `assembled_transcript_builder.py`: une pedazos cortos de transcript en frases mas utiles.
- `mic_audio_source.py`: abre microfono por `windows_wasapi_mic` o `sounddevice_mic`.
- `inputfeed_settings.py`: ENV, paths de runtime y tunables.
- `source_config.py`: exporta settings ya resueltos para el servicio.
- `transcript_runtime.py`: crea carpetas, escribe transcript/status y archiva sesiones.
- `audio_settings.py`: snapshot simple de audio para esta parte.

## Carpetas importantes

- `providers/`: backends STT.
- `providers/moonshine/`: backend Moonshine real.
- `providers/whisper/`: carpeta existe, pero Whisper se usa directo desde `faster_whisper`.
- `streaming/`: buffer y adaptador streaming para Whisper.
- `vad/`: gate de Silero VAD.
- `preprocess/`: RNNoise opcional.

## Runtime que escribe

- `runtime/sacred/live_transcript_raw.jsonl`
- `runtime/sacred/live_transcript_raw_latest.json`
- `runtime/sacred/live_transcript_history.jsonl`
- `runtime/sacred/live_transcript_latest.json`
- `runtime/sacred/live_transcript_assembled.jsonl`
- `runtime/sacred/live_transcript_assembled_latest.json`
- `runtime/status/inputfeed_to_text_status.json`
- `runtime/status/assembled_transcript_builder_status.json`
- `runtime/stt_archive/YYYY/MM/DD/session_<id>__raw__HH-MM-SS.jsonl`
- `runtime/stt_archive/YYYY/MM/DD/session_<id>__assembled__HH-MM-SS.jsonl`

## ENV mas utiles

Audio:

- `INPUTFEED_SOURCE_BACKEND`: `windows_wasapi_mic` en Windows, `sounddevice_mic` en Linux.
- `WINDOWS_MIC_DEVICE_NAME`: nombre o parte del nombre del microfono.
- `INPUTFEED_SAMPLE_RATE`
- `INPUTFEED_CHANNELS`
- `INPUTFEED_FRAMES_PER_BUFFER`
- `INPUTFEED_INPUT_GAIN`

STT:

- `INPUTFEED_STT_BACKEND`: `moonshine` o `whisper`.
- `MOONSHINE_LANGUAGE`: idioma para Moonshine.
- `STT_MODEL`
- `STT_LANGUAGE`
- `STT_COMPUTE_TYPE`
- `STT_BEAM_SIZE`
- `STT_CHUNK_MS`
- `STT_VAD_FILTER`

Filtro y streaming:

- `INPUTFEED_ENABLE_RNNOISE`
- `INPUTFEED_ENABLE_SILERO_VAD`
- `INPUTFEED_MIN_RMS`
- `INPUTFEED_SILERO_THRESHOLD`
- `INPUTFEED_USE_STREAMING`
- `INPUTFEED_STREAM_STEP_SECONDS`
- `INPUTFEED_STREAM_OVERLAP_SECONDS`
- `INPUTFEED_STREAM_MAX_BUFFER_SECONDS`

Assembler:

- `ASSEMBLER_MERGE_WINDOW_SECONDS`
- `ASSEMBLER_FLUSH_IDLE_SECONDS`
- `ASSEMBLER_MAX_BUFFER_PARTS`

Transcript:

- `TRANSCRIPT_SESSION_ID`
- `TRANSCRIPT_SOURCE_NAME`
- `TRANSCRIPT_SOURCE_TYPE`

## Schema basico

Raw transcript:

```json
{
  "event_id": "evt_...",
  "ts": 1712345678.901,
  "session_id": "session_...",
  "source": "audio_input",
  "text": "hello",
  "language": "en",
  "metadata": {
    "stt_backend": "whisper",
    "model_name": "medium"
  }
}
```

Assembled transcript:

```json
{
  "event_id": "asmb_...",
  "source": "assembled_transcript_builder",
  "text": "hello how are you",
  "source_event_ids": ["evt_1", "evt_2"],
  "part_count": 2
}
```

## Como correrlo

Normalmente lo arranca `scripts/start_main_stack.py`.

Para probar solo este modulo:

```powershell
python -m app.inputfeed_to_text.inputfeed_to_text_service
python -m app.inputfeed_to_text.assembled_transcript_builder
```

## Notas rapidas

- En Windows, el backend default es `windows_wasapi_mic`.
- En Linux, el backend default es `sounddevice_mic`.
- `old broke/` es codigo viejo de referencia. No usar como fuente principal.
- Si no escucha, revisar primero `WINDOWS_MIC_DEVICE_NAME`, `INPUTFEED_SOURCE_BACKEND`, y `runtime/status/inputfeed_to_text_status.json`.
- Si escucha palabras cortadas, revisar streaming, VAD, `STT_CHUNK_MS`, y el assembler.

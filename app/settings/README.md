# settings

## Que es

Settings = "perillas" (valores) que usa la app.
La config principal se arma en `app/config.py` con `AppConfig.build(...)`.

## Archivos

- `app_settings.py`: switches generales (modo, debug panel, offline, etc)
- `audio_settings.py`: microfono + STT live + device de salida TTS (playback)
- `play_settings.py`: que loops se encienden y defaults de UI/persona
- `tts_settings.py`: settings de TTS por ENV (Kokoro)
- `llm_settings.py`: settings de LLM por ENV (Ollama / modelos / timeouts)

## ENV (los mas usados)

- LLM: `LLM_PROVIDER`, `OLLAMA_BASE_URL` (o `OLLAMA_HOST`), `LLM_TEXT_MODEL`, `LLM_VISION_MODEL`
- TTS: `ASSISCLUE_TTS_BACKEND`, `ASSISCLUE_KOKORO_LANG`, `ASSISCLUE_KOKORO_VOICE`, `ASSISCLUE_TTS_SAMPLE_RATE`

Si queres cambiar defaults sin ENV: edita los `.py` de esta carpeta.

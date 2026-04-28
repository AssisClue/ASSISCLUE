# services

## Que es

Esta carpeta tiene helpers "de servicio" para el sistema (cosas tecnicas).

Ojo: aca hay un archivo que se llama `speech_service.py`, pero NO es el "speaker" que habla.
El que habla esta en `app/speech_out/speaker_service.py`.

## Archivos (hoy)

- `speech_service.py`: limpia/normaliza texto (para STT/TTS)
- `audio_playback.py`: reproduce wav en un device de audio
- `activity_status_service.py`: status general (runtime)
- `settings_summary_service.py`: resumen simple de settings (runtime/UI)
- `mode_service.py`: modo del sistema (ej: passive/listening_light)
- `capture_loop_service.py`: loop basico de captura (placeholder)

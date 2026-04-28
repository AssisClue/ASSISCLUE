# runtime

`runtime` guarda archivos vivos de la app: memoria, colas, estado, historial y archivos temporales.


## Carpetas importantes para usar

### memory/

Esta es una de las carpetas mas importantes.

Guarda memoria que puede servir para responder mejor.

Archivos importantes:

- `memory/memory_items.json`  
  Memorias automaticas reales. Aqui se guardan cosas que el asistente cree importantes.

- `memory/profile/user_profile.json`  
  Resumen sobre el usuario: gustos, preferencias, proyectos activos y datos estables.

- `memory/user_spaces/`  
  Zona editable/manual. Aqui van notas, reglas, prompts, ayuda u otras memorias que el usuario controla mas directamente.

No meter aqui status, logs o caches tecnicos.

### knowledge_library/

Esta carpeta es para conocimiento/documentos.

Sirve para textos guardados, mapas, resumenes, archivos parseados y cosas que el asistente puede leer como biblioteca.

Ejemplos:

- textos guardados desde browser
- mapas de biblioteca
- resumenes de archivos
- indices o manifests relacionados con documentos

No es lo mismo que `memory/`:  
`memory/` recuerda cosas sobre ti o el trabajo.  
`knowledge_library/` guarda material/documentos para consultar.

### output/

Historial y salidas finales.

Importante:

- `output/chat_history.jsonl`  
  Historial del chat usuario/asistente.

- `output/latest_response.json`  
  Ultima respuesta guardada.

### sacred/

Transcripts y momentos vivos.

Aqui cae texto de voz/STT y eventos vivos que luego otros servicios leen.

Importante para entender que escucho o detecto el asistente.

## Colas

### queues/router_dispatch/

Colas principales del router.

- `router_input_queue.jsonl`
- `action_queue.jsonl`
- `response_queue.jsonl`

Sirven para mover eventos entre listener, router, acciones y respuestas.

### queues/spoken_queries/

Resultado de preguntas habladas.

- `spoken_query_results.jsonl`

Lo escribe spoken queries y lo lee speech out para hablar.

### queues/speech_out/

Salida de voz.

- `speech_queue.jsonl`
- `spoken_history.jsonl`
- `latest_tts.json`
- `audio/`

Aqui van la cola de voz, historial hablado y audios generados.

## Estado y status

### state/

Estado actual del sistema.

Ejemplos:

- `state/system_runtime.json`
- `state/llm_runtime_state.json`
- `state/memory/`
- `state/live_listeners/`
- `state/speech_out/playback_state.json`

No es memoria de usuario; es estado tecnico actual.

### status/

Status de servicios.

Ejemplos:

- `status/router_dispatch/router_status.json`
- `status/spoken_queries/spoken_query_status.json`
- `status/speech_out/speaker_status.json`
- `status/memory/context_memory_runtime_status.json`

Sirve para saber si algo esta corriendo, apagado o fallo.

## Otras carpetas

### queues/browser/

Colas del browser service.

- `request_queue.jsonl`
- `result_queue.jsonl`

### status/browser/

Status del browser service.

- `status.json`

### browser/

Archivos propios del browser service que no son cola ni status.

### display_actions/

Acciones visuales, resultados y screenshots de acciones en pantalla.

### qdrant/

Base/index local para busqueda vectorial. Puede estar vacia.

### stt_archive/

Archivo historico de STT. Normalmente no se edita.

### web/

Archivos temporales o guardados por herramientas web.




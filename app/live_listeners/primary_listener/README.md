# primary_listener

Es el oído rápido del sistema.

Lee el transcript sagrado y detecta solo cosas claras y urgentes.

## Qué hace

- leer líneas nuevas del transcript
- detectar wakeword
- detectar comandos claros
- detectar preguntas rápidas
- emitir evento simple

## Qué no hace

- no responde
- no ejecuta acciones
- no usa LLM
- no arma contexto grande
- no decide cosas profundas

## Archivos

### primary_listener_service.py
Loop principal; lee transcript nuevo y coordina detección.

### primary_listener_config.py
Tunables del listener: wakewords, límites, poll interval.

### wakeword_matcher.py
Detecta si aparece el wakeword o alias.

### command_catalog.json
Catálogo declarativo de comandos y aliases.

### command_matcher.py
Compara texto contra el catálogo y detecta comandos.

### quick_question_matcher.py
Detecta preguntas cortas/directas.

### primary_listener_event_builder.py
Arma el evento de salida con formato estable.

### primary_listener_cursor.json
Cursor propio del listener.
Nunca se comparte.

## Regla principal

Lee rápido.
Detecta rápido.
Emite rápido.

No toca el transcript.
No pisa a otros listeners.





PRIMARY LSITEN STEPS :
live_transcript_history.jsonl
-> TranscriptReader.read_new_records()
   -> usa primary_listener_cursor.json
   -> lee solo líneas nuevas
-> primary_listener_service.process_record()
   -> toma text del record
-> wakeword_matcher
   -> detecta si nombraron al asistente
-> command_matcher
   -> compara contra command_catalog.json
   -> si hay comando claro, gana primero
-> quick_question_matcher
   -> si no hubo comando, mira si es pregunta corta/directa
-> primary_listener_event_builder
   -> arma evento limpio y estable
-> write primary_listener_status.json
-> output del listener
   -> command event
   -> quick question event
   -> wakeword only event
-> espera próximo poll
-> sigue leyendo desde su cursor





PRIMARY LISTEN STEPS PROCESS EVENT WHEN SEND :

audio
-> inputfeed_to_text_service
-> transcript_runtime.append_transcript_line()
   -> live_transcript_history.jsonl
   -> live_transcript_latest.json

live_transcript_history.jsonl
-> TranscriptReader.read_new_records()
   -> usa primary_listener_cursor.json
   -> lee solo líneas nuevas
-> primary_listener_service.process_record()
   -> toma text del record
-> wakeword_matcher
   -> detecta si nombraron al asistente
-> command_matcher
   -> compara contra command_catalog.json
   -> si hay comando claro, gana primero
-> quick_question_matcher
   -> si no hubo comando, mira si es pregunta corta/directa
-> primary_listener_event_builder
   -> arma evento limpio
   -> command event / quick question event / wakeword only event
-> primary_listener output
   -> por ahora print / evento detectado
-> después
   -> router_dispatch
      -> action_queue o response_queue
-> después
   -> action_runner o response_runner
-> después
   -> speech_queue
-> después
   -> tts / speaker

example 2 : "hey rick what did he say?"

live_transcript_history.jsonl
-> TranscriptReader.read_new_records()
-> primary_listener_service.process_record()
-> wakeword_matcher
   -> sí
-> command_matcher
   -> no encuentra comando
-> quick_question_matcher
   -> sí, detecta pregunta corta
-> primary_listener_event_builder
   -> arma primary_quick_question event
-> output del primary listener
-> router_dispatch
   -> lo manda a response_queue
-> response_runner
   -> decide si responder con regla o LLM
-> speech_queue
-> tts / speaker



example call question 


runtime/sacred/live_transcript_history.jsonl
-> TranscriptReader.read_new_records()
-> primary_listener_service.process_record()
-> wakeword_matcher
-> command_matcher
   -> no hay comando
-> quick_question_matcher
   -> sí, pregunta directa
-> memory_flag_matcher
   -> detecta "use memory"
-> primary_listener_event_builder
   -> arma primary_quick_question event
   -> use_memory = true
-> router_dispatch
   -> decide route = spoken_query
   -> escribe runtime/queues/router_dispatch/response_queue.jsonl
-> spoken_queries/runners/spoken_query_router
   -> ve use_memory = true
   -> manda a memory_question_runner
-> memory_question_runner
   -> consulta memoria/contexto
   -> usa llm si hace falta
-> response_result
-> runtime/queues/speech_out/speech_queue.jsonl
-> tts_bridge
-> speaker_service

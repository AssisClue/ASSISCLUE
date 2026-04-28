Archivos actuales: qué dejaría y qué cambiaría
1. spoken_query_router.py

Hoy: es el centro de todo. Lee queue, guarda status, decide runner, maneja command result, persona, chat history y loop.

Problema: hace demasiado.

2.0: lo dividiría.

spoken_query_router.py

Debería quedar solo como:

recibir request
→ clasificar intención
→ llamar runner correcto
→ devolver result

Lo demás va afuera.

2. request_text.py

Hoy: tiene 5 líneas, pero sirve. Toma texto desde text, cleaned_text o transcript_text.

¿Para qué sirve?

Sirve para que todos los runners lean el texto igual.

Sin ese archivo, cada runner haría esto diferente y habría bugs.

2.0: lo dejaría, pero renombrado mejor:

request_access.py

Y tendría helpers como:

get_request_text()
get_request_flags()
get_source_event_id()
get_routed_event_id()
3. memory_required_matcher.py

Hoy: decide si una frase debe ir a memoria. Pero también detecta explain, o sea HELP.

Problema: HELP no debería estar dentro de “memory required”.

2.0: separar:

help_query_matcher.py
memory_query_matcher.py
persona_query_matcher.py
4. memory_query_hint_parser.py

Hoy: limpia frases, detecta sources, HELP, personas, notes, rules, prompts.

Problema: tiene demasiadas misiones.

2.0: dividir:

help_query_parser.py       → explain/help/menu
memory_query_parser.py     → notes/rules/prompts/use memory
persona_query_parser.py    → personas/profile
5. memory_question_runner.py

Hoy: corre búsquedas en ContextMemoryService, pero también permite HELP implícito si source es user_spaces.help.

Problema: HELP 2.0 ya no vive en user spaces.

2.0: separar:

memory_question_runner.py  → memoria real
help_question_runner.py    → HELP/
persona_question_runner.py → personas
6. llm_direct_runner.py

Hoy: funciona, pero está gigante. Hace prefixes, wakewords, temp file hints, browser text context, LLM call, truncado de speech.

Problema: no es solo “runner LLM”, también maneja contexto de browser/temp y limpieza.

2.0: dividir:

llm_direct_runner.py
llm_prefix_parser.py
active_text_context_loader.py
speech_text_formatter.py

Así cada archivo tiene una razón clara.

7. simple_question_matcher.py

Hoy: detecta hora, fecha, presencia, modo, identidad.

Está bien.

2.0: lo dejaría casi igual, quizá con más frases y separado por intención.

8. simple_question_runner.py

Hoy: responde esas preguntas simples y lee system mode.

Está bien.

2.0: solo lo ordenaría un poco.

9. simple_refusal_runner.py

Hoy: responde “I can’t answer that yet.”

Sirve.

2.0: lo mejoraría para dar una salida útil:

I can't answer that yet. Try: HELP MENU, EXPLAIN MEMORY, or ASK RICK ...
Tree 2.0 ideal
app/spoken_queries/
│
├─ README.md
├─ spoken_query_router.py
│
├─ runtime_loop.py
├─ status_writer.py
├─ chat_history_writer.py
│
├─ contracts/
│  ├─ spoken_query_result.py
│  └─ spoken_query_intent.py
│
├─ request/
│  └─ request_access.py
│
├─ matchers/
│  ├─ help_query_matcher.py
│  ├─ memory_query_matcher.py
│  ├─ persona_query_matcher.py
│  ├─ simple_question_matcher.py
│  └─ llm_direct_matcher.py
│
├─ parsers/
│  ├─ help_query_parser.py
│  ├─ memory_query_parser.py
│  ├─ persona_query_parser.py
│  └─ llm_prefix_parser.py
│
├─ runners/
│  ├─ help_question_runner.py
│  ├─ memory_question_runner.py
│  ├─ persona_question_runner.py
│  ├─ simple_question_runner.py
│  ├─ llm_direct_runner.py
│  ├─ command_result_runner.py
│  └─ simple_refusal_runner.py
│
└─ helpers/
   ├─ result_builder.py
   ├─ speech_text_formatter.py
   └─ active_text_context_loader.py
Flujo 2.0 claro
spoken_query_router.py
→ get_request_text()
→ detect intent

IF help:
  help_question_runner.py

IF memory:
  memory_question_runner.py

IF persona:
  persona_question_runner.py

IF simple:
  simple_question_runner.py

IF llm:
  llm_direct_runner.py

ELSE:
  simple_refusal_runner.py
Qué logra esta versión 2.0
Antes
HELP parece memoria
router hace demasiado
LLM runner hace demasiado
parser mezcla help + memory + persona
Después
HELP es HELP
MEMORY es MEMORY
PERSONA es PERSONA
LLM es LLM
router solo enruta
runners solo responden
helpers hacen tareas pequeñas

Eso es el “WOW”: no más magia escondida.

Mi recomendación para seguir

Primero haría esta separación mínima:

1. Crear help_query_matcher.py
2. Crear help_query_parser.py
3. Crear help_question_runner.py
4. Sacar HELP de memory_query_hint_parser.py
5. Sacar HELP de memory_question_runner.py

Con eso ya pasás de 0.9 mezclado a una 1.5 muy sana.

Después ordenás spoken_query_router.py y llm_direct_runner.py para llegar a 2.0 real.
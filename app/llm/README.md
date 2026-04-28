# app/llm

Capa central de integración LLM para la línea nueva.

## Objetivo
Tener un punto único para:
- texto
- visión / screenshots
- prompts
- formatters
- settings
- cliente Ollama

## Archivos

- `llm_settings.py`
  - provider
  - modelos
  - timeout
  - max tokens
  - temperatura

- `llm_types.py`
  - requests / results simples

- `llm_client.py`
  - llamadas crudas a Ollama text y vision

- `llm_service.py`
  - entrypoint para respuestas de texto

- `vision_service.py`
  - entrypoint para análisis de imagen

- `llm_prompts.py`
  - prompts base

- `llm_formatters.py`
  - salida corta para UI y TTS

## Regla
Los runners no deberían hablar directo con Ollama.
Deben pasar por `app/llm/`.

## Modelos
- texto: `qwen2.5:3b`
- visión: configurable aparte
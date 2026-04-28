# personas

Este bloque define perfiles/asistentes reutilizables del sistema.

## Idea principal

- `config` decide cual `persona_id` esta activo
- `personas/` sabe cargar el perfil real
- otros bloques consumen el perfil desde un servicio, no desde strings sueltos

## Estructura

- `models/assistant_profile.py`
  - shape base del perfil
- `registry/profile_registry.py`
  - carga perfiles desde `profiles/`
- `services/persona_service.py`
  - puerta publica para obtener perfiles
- `profiles/*.json`
  - definiciones declarativas de asistentes

## Regla

Este bloque no hace routing, no hace memoria y no decide acciones.
Solo define y entrega perfiles activos de asistente.

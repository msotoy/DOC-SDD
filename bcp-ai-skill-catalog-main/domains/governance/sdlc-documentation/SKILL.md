---
name: sdlc-documentation
description: Genera y mantiene documentacion trazable de requisitos, decisiones, cambios, pruebas y evidencia.
---

# SDLC Documentation Skill

## Proposito
Mantener documentacion util para que otro rol pueda entender el cambio, reproducirlo y revisarlo.

## Entradas
- Historia de usuario o issue.
- Criterios de aceptacion.
- Archivos modificados y decisiones.
- Resultado de pruebas y revisiones.

## Salidas
- `requirements.md`, SDD o documento equivalente.
- Matriz requisito -> tarea -> archivo -> prueba.
- Decision log y preguntas abiertas.
- Enlaces a evidencia sin secretos.

## Flujo
1. Identifica alcance, fuera de alcance y supuestos.
2. Relaciona cada criterio con tareas y pruebas.
3. Registra decisiones pendientes y responsable.
4. Actualiza la documentacion del repositorio.
5. Verifica que la evidencia sea reproducible.

## Reglas obligatorias
- No inventar requisitos ni decisiones.
- No incluir secretos, tokens, PII ni datos productivos.
- Mantener version, fecha, autor y estado del documento.
- Adaptar nombres de archivos y formato al estandar del squad.

## Criterio de salida
El documento debe permitir una revision independiente y señalar explicitamente cualquier gap.

---
name: pull-request-review
description: Revisa pull requests con checklist de alcance, contrato, seguridad, calidad, pruebas, documentacion y versionamiento.
---

# Pull Request Review Skill

## Proposito
Emitir una revision consistente y accionable antes de integrar un cambio.

## Entradas
- Issue o historia de usuario.
- Pull request y diff.
- Resultado de tests y lint.
- Contratos, decisiones y evidencia.
- Politicas del repositorio.

## Salidas
- Findings ordenados por severidad.
- Checks pass/fail/skipped.
- Preguntas y riesgos residuales.
- Decision: approved, changes_requested o blocked.
- Evidencia redactada.

## Checklist
- Alcance y criterios de aceptacion.
- Compatibilidad API.
- Seguridad, secretos y PII.
- Calidad y complejidad.
- Tests y cobertura.
- Documentacion y changelog.
- Dependencias y migraciones.
- Rollback y observabilidad.

## Reglas
- Findings primero, resumen despues.
- No aprobar por intuicion ni por ausencia de errores visibles.
- No imprimir secretos.
- No ejecutar comandos destructivos ni modificar el PR durante la revision.
- Distinguir bug confirmado de recomendacion.

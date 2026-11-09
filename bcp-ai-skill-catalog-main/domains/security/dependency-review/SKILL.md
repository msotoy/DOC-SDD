---
name: dependency-review
description: Revisa dependencias, CVEs, licencias, actualizaciones y evidencia de impacto.
---

# Dependency Review Skill

## Proposito
Detectar dependencias vulnerables o innecesarias y proponer cambios compatibles con el stack.

## Flujo
1. Identifica manifest y lockfile.
2. Ejecuta el auditor disponible sin publicar secretos.
3. Clasifica severidad, explotabilidad, alcance y version corregida.
4. Propone actualizar, eliminar, sustituir o aceptar temporalmente con vencimiento.
5. Ejecuta pruebas despues del cambio y documenta el resultado.

## Comandos orientativos
- `npm audit --audit-level=moderate`.
- `yarn audit` o `pnpm audit`.
- `mvn dependency:tree` y auditor configurado por el proyecto.
- `gradle dependencies`.
- `pip-audit` si esta autorizado.

## Reglas
No actualizar mas de lo necesario, no editar lockfiles sin autorizacion, no afirmar que un CVE esta corregido sin evidencia y no incluir tokens de registries.

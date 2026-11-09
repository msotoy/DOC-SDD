---
name: versioning-quality-gate
description: Revisa versionado, changelog, commit, tag y trazabilidad de un cambio.
---

# Versioning Quality Gate Skill

## Proposito
Asegurar que un cambio publicable tenga version, historial, evidencia y rollback identificables.

## Flujo
1. Verifica estado y diff.
2. Comprueba convención de commit y referencia al issue.
3. Valida version en manifest/package/build.
4. Actualiza CHANGELOG con impacto y breaking changes.
5. Crea o verifica tag solo con autorizacion.
6. Reporta archivos y comandos reproducibles.

## Reglas
- Nunca crear tags sobre cambios no validados.
- Nunca reescribir historial sin autorizacion.
- No incluir secretos en commits, changelogs o tags.
- Adaptar la convención al repositorio, sin imponer SemVer cuando el producto use otra.

## Salida
Checklist pass/fail, gaps, version propuesta, commit recomendado, tag recomendado y evidencia.

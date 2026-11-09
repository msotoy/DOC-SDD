# S1 - Skill basico versionado: Feature Intake -> Spec Checklist

## Objetivo

Crear y versionar un Skill basico, no un prompt largo, que cualquier rol del SDLC pueda entender y reutilizar. El Skill convierte una solicitud de cambio en un paquete minimo trazable con alcance, riesgos, decisiones, criterios de aceptacion y plan de verificacion.

## Entregables

- `.github/skills/feature-intake-spec-checklist/SKILL.md`
- `.github/skills/feature-intake-spec-checklist/examples/input.sample.md`
- `.github/skills/feature-intake-spec-checklist/examples/output.sample.md`
- Un commit y un tag como `skill-feature-intake-v0.1.0`.
- `CHANGELOG.md` del Skill, opcional pero recomendado.

Sigue `STEP-BY-STEP.md` para ejecutar el laboratorio en orden. El contrato completo esta en `.github/skills/feature-intake-spec-checklist/SKILL.md`.

## Criterio de aceptacion

El Skill declara metadata, I/O, constraints, validacion y evidencia. El ejemplo de salida contiene todas las secciones, al menos tres criterios medibles, tres tareas para Tech Lead, Backend y QA, dos riesgos con mitigacion y ninguna informacion sensible.
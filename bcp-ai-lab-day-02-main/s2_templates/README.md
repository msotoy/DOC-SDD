# S2 - Skills desde el catálogo (onboarding + ciclo SDLC)

## Objetivo

Registrar tus 3 repos en el catálogo central, instalar 6 Skills vía ISSUE y simular un ciclo SDLC completo (API, Backend, Frontend, Test, Docs y Review) sobre HU-01 y HU-05, sin empezar de cero: contrato desde `docs/ENDPOINTS.md` y pruebas desde `docs/TESTING.md`.

## Materiales

- `reqflow-workspace/` con tus 3 repos propios; los comandos se ejecutan desde ahí.
- `workshop-auth-backend/.github/skills/feature-intake-spec-checklist` (S1).
- Acceso para crear ISSUES en `NTTData-Academy/bcp-ai-skill-catalog` (plantillas `repo-onboarding` y `skills-install`).
- `workshop-auth-backend/HU-01.md` (generada en S1) y `workshop-login-frontend/HU-05.md` (generada igual desde el `HALLAZGOS.md` del frontend). Solo si tu `HALLAZGOS.md` no tiene esos hallazgos "Pendiente", usa las versiones de referencia: `s1_skills/HU-01.md` y `s2_templates/HU-05.md`.

## Catálogo de Skills

Los seis Skills (más el de S1) viven en `.github/skills/`, para que Copilot los descubra automáticamente. Se solicitan al catálogo central mediante ISSUES (pasos 02-04), uno por dominio del ciclo SDLC:

- `api-contract-generation` (api): genera el contrato OpenAPI (rutas, esquemas, errores) a partir del codigo o del README;
- `quarkus-secure-endpoint` (backend): implementa HU-01 con claims minimos, expiracion coherente y secreto sin exponer;
- `frontend-feature-generation` (frontend): resuelve HU-05 generando componente, servicio y pruebas Angular sin `innerHTML` para contenido dinamico;
- `test-strategy` (test): convierte HU y criterios de aceptacion en una matriz de pruebas requisito -> escenario -> prueba -> evidencia;
- `sdlc-documentation` (governance): deja el registro trazable del ciclo en `SDLC-EVIDENCE.md`;
- `pull-request-review` (review): revisa el PR con checklist de alcance, contrato, seguridad, calidad y pruebas, con decision explicita.

No se copian artefactos externos sin validar su alcance o licencia. El catalogo central es la fuente de trabajo del laboratorio y el mecanismo de instalacion via ISSUE garantiza consistencia entre dias.

El SDD de S2 es un insumo practico para el resto del dia. No sustituye un proceso completo de SDD fuera del alcance de este laboratorio.

## Pasos

Sigue `STEP-BY-STEP.md` en orden:

| Paso | Qué hace |
| --- | --- |
| 01 | Verifica prerrequisitos: 3 repos + Skill de S1 |
| 02 | Onboarding de tus repos en el catálogo (`subscribers.json`) |
| 03 | Explora el catálogo (`SKILLS-MANIFEST.json`) |
| 04 | Instala los 6 Skills vía ISSUE |
| 05 | Sincroniza (`pull`) los Skills instalados por el bot |
| 06 | Contrato API con `api-contract-generation` |
| 07 | Backend HU-01 con `quarkus-secure-endpoint` |
| 08 | Frontend HU-05 con `frontend-feature-generation` |
| 09 | Matriz de pruebas con `test-strategy` |
| 10 | `SDLC-EVIDENCE.md` + review con decisión |
| 11 | Versiona: commit y tag `lab02-s2` |

## Evidencia mínima

- `.github/skills/` con los 6 Skills del catálogo junto al de S1 en cada repo.
- Contrato API, cambios de HU-01/HU-05, matriz de pruebas y `SDLC-EVIDENCE.md` por repo cambiado.
- Commit y tag `lab02-s2`; enlace al issue del Project ReqFlow correspondiente.

## Criterio de aceptación

Cada repo remoto contiene los 6 Skills instalados; `workshop-auth-backend` trae los cambios de HU-01 y `workshop-login-frontend` los de HU-05, cada uno con su `SDLC-EVIDENCE.md` y revisión con decisión explícita (approved, changes_requested o blocked).

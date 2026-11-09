# Evaluacion W1 - ReqFlow (Nuvexa Andina Digital)

## Instrucciones para el asistente

Recibe el requisito funcional desde un issue asignado en GitHub Project. Resuelve el requisito sobre `caso-login/backend` y `caso-login/frontend`, usando los Skills, templates, tools y MCP del Dia 2.

No cambies el contrato `POST /auth/login` salvo que el issue lo solicite y registres la decision. No uses datos productivos ni incluyas credenciales en commits, logs o evidencias.

## Flujo SDLC obligatorio

1. Leer el issue y registrar el requisito en `docs/requirements.md`.
2. Crear `docs/sdd-login.md` con contexto, impacto backend/frontend, seguridad, pruebas y aceptacion.
3. Descomponer el trabajo en `docs/tasks.md`.
4. Crear o actualizar `.github/skills/login-skill/` con version, inputs, constraints y validacion (esa carpeta es la que Copilot descubre automaticamente).
5. Implementar en backend y/o frontend segun el requisito.
6. Ejecutar tests y tools; guardar evidencia.
7. Consultar el MCP permitido y demostrar una operacion denegada.
8. Abrir pull request, completar `docs/decisions.md` y solicitar review humana.

## Rúbrica W1

| Criterio | Peso | Evidencia minima |
| --- | ---: | --- |
| Requisito y SDD | 20% | issue enlazado, alcance, criterios de aceptacion |
| Skill versionado | 20% | metadata, I/O, constraints, validacion |
| Implementacion login | 20% | cambio correcto en backend/frontend y contrato preservado |
| Tools + MCP | 20% | llamada permitida, llamada denegada y logs |
| Testing, review y trazabilidad | 20% | tests, PR, decision humana y evidence pack |

Umbral: `>= 80%`. El trainer registra la puntuacion, feedback y decision final en este archivo y en el campo `Gate W1` del GitHub Project.

## Requisito individual

Requirement ID: `{{REQUIREMENT_ID}}`

Issue: `{{GITHUB_ISSUE_URL}}`

Descripcion: `{{FUNCTIONAL_REQUIREMENT}}`

Variantes de requisitos sugeridas:

- `W1-AUTH-01`: mostrar mensaje generico ante credencial invalida sin filtrar si el usuario existe.
- `W1-AUTH-02`: validar campos vacios en el formulario sin llamar al backend.
- `W1-AUTH-03`: documentar y probar el estado de carga durante el login.
- `W1-AUTH-04`: agregar prueba de regresion para el contrato `POST /auth/login`.
- `W1-AUTH-05`: identificar y corregir un hallazgo de seguridad del flujo login, con evidencia.
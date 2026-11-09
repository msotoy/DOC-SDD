# W1 - Evaluacion practica individual

## Proposito

W1 comprueba lo aprendido en el Dia 1 y el Dia 2 mediante una simulacion acotada de un SDLC. Cada asistente debe tener un repositorio propio, con una copia del caso ReqFlow (el mismo Flujo de Login de S1-S3, ahora en un repositorio individual) y un documento de evaluacion personalizado.

## Repositorio individual

Cada repositorio generado debe contener:

```text
attendee-<id>/
|- caso-login/
|  |- backend/       # copia de workshop-auth-backend-template
|  |- frontend/      # copia de workshop-login-frontend-template
|  `- requirements-api/ # copia de workshop-requirements-api-template
|- EVALUACION-W1.md  # variante individual y criterios
|- prompts/          # prompts usados durante la evaluacion
|- docs/
|  |- requirements.md
|  |- sdd-login.md
|  |- tasks.md
|  `- decisions.md
|- .github/skills/login-skill/
|- tools/tool-run.json
|- mcp/permissions.json
|- tests/evidence/
`- .github/
   `- workflows/validate.yml
```

## GitHub Project

El trainer crea un GitHub Project por ola o por grupo y asigna a cada asistente un issue distinto. El issue es la fuente de verdad del requisito funcional de W1. El participante debe enlazar el issue, el pull request y la evidencia.

Campos recomendados: `Status`, `Assignee`, `Requirement ID`, `Priority`, `Backend`, `Frontend`, `Test`, `Review`, `Evidence`, `Gate W1`.

## Generar un repositorio

Usa `create-attendee-repo.ps1` con un issue o variante distinta por asistente.

### Que es `-TemplatesRoot`

Es la carpeta que contiene, una al lado de la otra, estas 3 carpetas de repos:

```text
<esa carpeta>/
|- workshop-auth-backend-template/
|- workshop-login-frontend-template/
`- workshop-requirements-api-template/
```

No es la carpeta de uno solo de los templates, ni la carpeta de `bcp-ai-lab-day-02`: es la carpeta **contenedora**, la que tiene a los 3 adentro.

### Comando (copiar, pegar y solo cambiar lo marcado `[EDITAR]`)

Ejecuta el script desde `w1_evaluation/`:

```powershell
.\create-attendee-repo.ps1 `
  -AttendeeId "[EDITAR: ej. jonatan-moreno-leyva]" `
  -RequirementId "[EDITAR: ej. W1-AUTH-01]" `
  -IssueUrl "[EDITAR: URL del issue de GitHub Project]" `
  -RequirementText "[EDITAR: descripcion del requisito]" `
  -TemplatesRoot "..\.."
```

Sobre `-TemplatesRoot "..\.."`:

- Si clonaste los 3 templates justo al lado de `bcp-ai-lab-day-02` (el layout normal de entrega), deja ese valor tal cual: `..\..` significa "sube 2 carpetas desde donde estoy" y llega exactamente ahi.
- Si los tienes en otro lugar, reemplaza `"..\.."` por la ruta completa a esa carpeta, por ejemplo `"C:\ruta\a\la\carpeta\con\los\3\templates"`.

Si te equivocas de carpeta, el script se detiene y te dice cual de los 3 templates no encontro.

El script copia los tres templates, crea `prompts/` y prepara un repositorio Git local. No publica repositorios ni usa tokens: el trainer lo sube por el canal aprobado.
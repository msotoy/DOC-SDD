# BCP AI Lab - Day 02

> Programa Train-the-Trainers IA - NTT DATA Peru x BCP
> Laboratorio: Agent Skills, templates SDLC y MCP.

## Objetivo del día

Convertir tus hallazgos "Pendiente" del Día 1 en historias trazables (`HU-01.md` y `HU-05.md`, cada una con su sección Origen `H-xx`), versionar e instalar Skills que Copilot descubre solo, operar un MCP local y el oficial de GitHub, y dejar el backlog creado: un issue por HU en el Project **ReqFlow**. Cierras con el tag `day2-done` y `check_handoff.py --day 2` en verde: eso es la entrada del Día 3.

## Que construye este repositorio

Tres sesiones progresivas sobre el caso **Flujo de Login**. El sistema bajo trabajo se compone de los templates tecnicos del sandbox:

- `workshop-auth-backend`: backend Java 21 + Quarkus + SQLite, `POST /auth/login`, servicio en `http://localhost:8080`.
- `workshop-login-frontend`: frontend Angular, servicio en `http://localhost:4200`, consumidor del backend.
- `workshop-requirements-api`: API FastAPI para tareas y requisitos, disponible cuando el laboratorio necesite una API adicional.

Los templates son recursos de laboratorio. Cada asistente trabaja en **su `reqflow-workspace/` del Dia 1**: los mismos tres repos propios (`<OWNER>/workshop-auth-backend`, `<OWNER>/workshop-login-frontend`, `<OWNER>/workshop-requirements-api`), no templates limpios. Clona este laboratorio **al lado** del workspace, no dentro (`git clone https://github.com/NTTData-Academy/bcp-ai-lab-day-02.git` en la carpeta del curso), y abre VS Code sobre `reqflow-workspace/`: así Copilot ve solo el producto, no las soluciones de referencia del lab.

## Entrada del dia: handoff del Dia 1

Antes de S1, verifica desde la carpeta del laboratorio que tu workspace del Dia 1 este completo (al menos 1 repo en `[OK]`):

```powershell
python tools/check_handoff.py --day 1 ../reqflow-workspace
```

| Viene del Dia 1 | Se usa en |
| --- | --- |
| `HALLAZGOS.md`, filas "Pendiente" con Id `H-xx` | S1 y S2: se generan `HU-xx.md`. S3: un issue por HU en el Project ReqFlow |
| `prompts/*.md` | S1: ejemplo de entrada del Skill (`examples/input.sample.md`) |
| `docs/ENDPOINTS.md` | S2: base del contrato API |
| `docs/TESTING.md` | S2: base de la matriz de pruebas |

Si el chequeo falla, parte de la rama `checkpoint/day1` que entrega el instructor.

| Sesion | Carpeta | Entregable |
| --- | --- | --- |
| S1 | [`s1_skills/`](s1_skills/README.md) | Skill versionado para login, con metadata, I/O, constraints y validacion |
| S2 | [`s2_templates/`](s2_templates/README.md) | Paquete de templates SDLC aplicado al flujo de login |
| S3 | [`s3_mcp/`](s3_mcp/README.md) | Servidor MCP (local y GitHub oficial) con resources, tools y permisos verificables |
| W1 | [`w1_evaluation/`](w1_evaluation/README.md) | Plantilla para un repositorio individual con caso, evaluacion y GitHub Project |

Abre [laboratory-guide.html](laboratory-guide.html) en tu navegador: es la guia interactiva del dia, con el objetivo, los pasos y el prompt de cada sesion listos para copiar.

### Historias de usuario del día

Las historias no se copian: **se generan a partir de tu `HALLAZGOS.md` del Dia 1**. `HU-01.md` sale del hallazgo de token del backend (S1, paso 06) y `HU-05.md` del hallazgo de `innerHTML` del frontend (S2). Cada HU lleva en su encabezado el Id del hallazgo de origen (`Origen: H-xx`), para trazar hallazgo → HU → issue → PR.

Cada HU vive en la raiz del repo al que pertenece: `workshop-auth-backend/HU-01.md` y `workshop-login-frontend/HU-05.md`.

Si tu `HALLAZGOS.md` no tiene ese hallazgo "Pendiente" (lo resolviste el Dia 1 o no lo encontraste), usa la version de referencia: `s1_skills/HU-01.md` y `s2_templates/HU-05.md`.

## Estructura

```text
bcp-ai-lab-day-02/
|- s1_skills/
|- s2_templates/
|- s3_mcp/
|- w1_evaluation/
|- github-project/       # Campos e issue template reproducibles
|- laboratory-guide.html
|- laboratory-flows.html
|- .env.example
|- requirements.txt
`- README.md
```

## Preparacion teorica del equipo

El equipo de cada participante debe estar preparado antes de la sesion. Estos son los requisitos tecnicos que se deben comprobar teoricamente:

- Git 2.40+;
- JDK 21;
- Maven 3.9+;
- Node.js 22.12+ y npm;
- Python 3.11+;
- VS Code con GitHub Copilot, GitHub CLI autenticado y acceso al GitHub Project de la ola;
- Docker si el issue o el stack del laboratorio lo requiere.

Durante el laboratorio no se dedica tiempo a instalar herramientas ni configurar accesos.

```powershell
cd workshop-auth-backend
mvn test
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'mvn quarkus:dev'

cd ..\workshop-login-frontend
npm install
npm start
```

Verificacion minima:

```powershell
Invoke-WebRequest http://localhost:8080/q/health
Invoke-WebRequest http://localhost:4200
```

Credenciales del laboratorio: `student / Workshop123!` y `trainer / Trainer123!`.

## Estructura del workspace del participante

```text
<carpeta-del-curso>/
|- bcp-ai-lab-day-01/               # labs: fuera del workspace
|- bcp-ai-lab-day-02/               # este laboratorio
`- reqflow-workspace/               # el mismo de los 4 dias (abre VS Code aqui)
   |- .vscode/mcp.json              # S3: servidores MCP
   |- workshop-auth-backend/        # <OWNER>/workshop-auth-backend
   |  |- .github/skills/            # Skill de S1 + Skills del catalogo (S2)
   |  |- HALLAZGOS.md, prompts/, docs/  # del Dia 1
   |  `- HU-01.md                   # S1, generada desde HALLAZGOS.md
   |- workshop-login-frontend/      # <OWNER>/workshop-login-frontend
   |  |- .github/skills/
   |  `- HU-05.md                   # S2, generada desde HALLAZGOS.md
   `- workshop-requirements-api/    # <OWNER>/workshop-requirements-api
      `- .github/skills/
```

Cada laboratorio debe indicar los archivos que se deben crear o completar. Los prompts y evidencias forman parte de la entrega.

## Secuencia del dia

| Sesion | Horario | Duracion | Contenido |
| --- | --- | --- | --- |
| S1 | 09:30-11:30 | 2 h | Anatomia de un Agent Skill; produce un Skill versionado y reutilizable para el login ([`s1_skills/`](s1_skills/README.md)) |
| *Descanso* | 11:30-11:45 | 15 min | Break |
| S2 | 11:45-13:00 | 1 h 15 | Registra tus repos en el catalogo, instala 6 Skills via ISSUE y simula el ciclo SDLC sobre HU-01 y HU-05 ([`s2_templates/`](s2_templates/README.md)) |
| *Almuerzo* | 13:00-14:00 | 1 h | Lunch |
| S3 | 14:00-15:20 | 1 h 20 | MCP local y GitHub MCP oficial: resources, tools, permisos, un issue por HU y el Project ReqFlow ([`s3_mcp/`](s3_mcp/README.md)) |
| *Descanso* | 15:20-15:30 | 10 min | Break |
| W1 | 15:30-18:00 | 2 h 30 | Evaluacion practica individual sobre ReqFlow ([`w1_evaluation/`](w1_evaluation/README.md)) |
| **Total** | **09:30-18:00** | **~8h30** | Incluye breaks y almuerzo |

W1 comprueba individualmente lo aprendido sobre **ReqFlow** (el mismo Flujo de Login, ahora en tu repositorio individual) con un requerimiento distinto por asistente; cierra el dia de 15:30 a 18:00.

Los horarios son una referencia de partida: ajusta los horarios segun el ritmo real de tu cohorte.

## Catalogo de Skills S2

S2 instala 6 Skills desde el catálogo central (uno por dominio SDLC) más el de S1; viven en `.github/skills/` para que Copilot los descubra. Catálogo, materiales, pasos y evidencia: [`s2_templates/README.md`](s2_templates/README.md).

## GitHub Project

Cada participante crea su Project **ReqFlow** bajo su `<OWNER>` (el mismo de sus tres repos). Consulta [github-project/README.md](github-project/README.md) para los campos, estados y la plantilla de issue. Los Dias 3 y 4 reutilizan ese Project: no se recrea.

## Evidencia obligatoria

Cada sesion define su propia evidencia minima (ver los `README.md` de [`s1_skills/`](s1_skills/README.md), [`s2_templates/`](s2_templates/README.md) y [`s3_mcp/`](s3_mcp/README.md)). Para W1, la lista completa de archivos y la rubrica estan en [`w1_evaluation/README.md`](w1_evaluation/README.md) y [`w1_evaluation/EVALUACION-W1.md`](w1_evaluation/EVALUACION-W1.md). En todos los casos se debe conservar el enlace al issue de GitHub Project y al pull request.

## Gate del dia

El gate del dia se registra como **W1 - Evaluacion practica individual**. El umbral es `>= 80%`, con los cinco criterios de `w1_evaluation/EVALUACION-W1.md` (20% cada uno): requisito y SDD, Skill versionado, implementacion del login, tools + MCP, y testing/review/trazabilidad. La rúbrica de S1–S3 está en [EVALUACION-D2.md](EVALUACION-D2.md). El trainer registra la puntuacion y la decision en el repositorio individual del asistente.

## Cierre del dia: handoff al Dia 3

El Dia 3 no crea backlog nuevo: abre tu Project **ReqFlow** y trabaja sobre estos artefactos. Antes de salir, verifica que existan:

- `HU-*.md` en la raiz de su repo, cada una con su seccion Origen (`H-xx`);
- un issue por HU, en el repo de la HU, agregado al Project ReqFlow con el campo `Hallazgo origen`;
- `.github/skills/` en cada repo, y `reqflow-workspace/.vscode/mcp.json`;
- `docs/mcp-evidence/mcp.json` (copia sin tokens) en cada repo que cambiaste;
- el tag `day2-done` en cada repo que cambiaste (se crea en el paso 5 de S3, junto al tag `lab02-s3`).

Verifica desde la carpeta del laboratorio (al menos 1 repo en `[OK]` y `mcp.json` presente):

```powershell
python tools/check_handoff.py --day 2 ../reqflow-workspace
```

Si el chequeo falla, el Dia 3 parte de la rama `checkpoint/day2` que entrega el instructor.

## Importante

Este repositorio es para formacion en sandbox. No usar credenciales reales, secretos, datos productivos ni repositorios productivos.

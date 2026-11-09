# 🏛️ BCP AI Lab — Day 04: Orquestación e Ingeniería de Agentes

> **Programa Train-the-Trainers IA · NTT DATA Perú × BCP**  
> *Día 4 de laboratorios prácticos: orquestación multi-agente, workflows stateful, harness engineering y guardrails de producción.*

## 🎯 Objetivo del día

Orquestar agentes que trabajan sobre **tu** backlog (Project ReqFlow, issues con `H-xx`, specs del Día 3): generar con CrewAI/LangGraph, refactorizar con el harness gobernado por la Constitución ReqFlow (R1–R6) y el contexto de tu producto, y abrir el PR que cierra el issue (`Closes #N`). Demuestras el ciclo completo hallazgo → HU → issue → spec → PR y superas el **Gate G2 (≥ 80 %)**. Rúbrica: [EVALUACION-D4.md](EVALUACION-D4.md).

---

## 🗺️ Mapa de Recursos del Laboratorio

Para que tu experiencia sea ágil y no te sientas abrumado, la documentación está organizada por propósito:

| Recurso | Formato | ¿Para qué sirve? |
| :--- | :---: | :--- |
| **[GUIA_ESTUDIANTE.md](GUIA_ESTUDIANTE.md)** | 📖 Markdown | **Manual de Terminal:** Comandos exactos, configuración de `.env`, cómo probar el código generado y solución de problemas. |
| **[laboratory-guide.html](laboratory-guide.html)** | 📊 Navegador | **Dashboard Visual:** Agenda horaria (08:00 a 17:00), materiales por paso y rúbrica formal del **Gate G2**. |
| **[laboratory-flows.html](laboratory-flows.html)** | 🔀 Navegador | **Visualizador Animado:** Diagramas interactivos del paso de mensajes entre agentes para S1, S2, S3 y S4. |
| **[Biblioteca Técnica (`docs/`)](docs/)** | 📚 Módulos | **Whitepapers de Arquitectura:** Fundamentos detallados de hexagonal, protocolo MCP, arnés y guardrails. |

---

## 🔗 Entrada del día: lo que traes de los Días 1-3

El Día 4 **no usa un caso nuevo**: los agentes trabajan sobre tu `reqflow-workspace/`, tu Project ReqFlow y tus specs. Antes de empezar, desde la carpeta del laboratorio:

```powershell
python tools/check_handoff.py --day 3 ../reqflow-workspace
```

| Viene de | Artefacto | Lo usa |
| :--- | :--- | :--- |
| Día 1 | `REGLAS.md`, `docs/GOOD_PRACTICES.md`, `docs/ENDPOINTS.md`, `HALLAZGOS.md` | S3/S4: el harness los inyecta como contexto del producto (`load_product_context`) |
| Día 2 | Project ReqFlow + issues | S1/S2: backlog vía MCP (`GITHUB_OWNER=<OWNER>`). S3/S4: `GITHUB_ISSUE` acota el alcance y el PR lo cierra |
| Día 3 | `openspec/specs/` y skill `reqflow-definition-of-done` | S3/S4: contrato y DoD dentro del contexto del harness |
| Día 3 | Issue en `Todo` dejado para hoy | S3/S4: `GITHUB_ISSUE=<N>` en el `.env` |

En cada `.env` usa `GITHUB_OWNER=<OWNER>` (tu owner) y `GITHUB_REPO=workshop-requirements-api`. Si el chequeo falla, parte de la rama `checkpoint/day3` que entrega el instructor.

---

## 🧭 Las Cuatro Sesiones del Día

El día se divide en dos grandes enfoques prácticos:
* **Mañana (Generación):** S1 y S2 leen un requerimiento bancario en vivo desde un GitHub Project vía MCP y lo implementan SOBRE tus repos de `reqflow-workspace` (rama local `agent/<slug>`, sin push). El issue manda el alcance: solo corren los agentes de los stacks involucrados (backend/frontend/api); Designer y Reviewer siempre corren (el Reviewer revisa el diff real).
* **Tarde (Refactorización):** S3 y S4 clonan un repositorio real, aplican mejoras de seguridad bajo una Constitución y abren Pull Requests auditados.

| Sesión | Enfoque | Tecnología | Concepto Clave y Entregable |
| :--- | :--- | :--- | :--- |
| **[S1 CrewAI](s1_crewai/README.md)** | Generación | `CrewAI` | **Agentes por Roles + HITL:** 4 agentes especializados (Designer, Backend, Frontend, Tech Lead), pausas humanas `[s/n/r]`, spinner en tiempo real y checkpoints reanudables. |
| **[S2 LangGraph](s2_langgraph/README.md)** | Generación | `LangGraph` | **Workflows Stateful + Hexagonal:** Grafo de estado (`StateGraph`) con `interrupt_before` y generación de backend en **7 capas hexagonales** validadas determinísticamente. |
| **[S3 Harness](s3_harness/README.md)** | Refactorización | `Harness` | **Harness Engineering + Constitución:** Refactorización de **tu** `workshop-requirements-api` acotada al issue `GITHUB_ISSUE`, gobernada por la Constitución ReqFlow (R1-R6) más tus artefactos de los Días 1-3; *Compliance Score* y PR con `Closes #N`. |
| **[S4 Guardrails](s4_guardrails/README.md)** | Gobierno | `Review Loop` | **Diálogo Dev ↔ Reviewer + Evals:** Bucle iterativo de revisión de código, guardrails de entrada (PII, tokens), guardrails de salida y suite de 10 evals sobre el repo real (**Gate G2 ≥ 80%**). |

---

## ⚡ Inicio Rápido (En 3 Pasos)

El laboratorio trabaja con **2 terminales abiertas en paralelo**:

### Paso 1: Prerrequisitos
Asegúrate de tener instalado **Python 3.11+**, **Git**, **GitHub CLI (`gh`)**, un motor de contenedores (**Podman** o **Docker Desktop**) y **VS Code con GitHub Copilot en modo Agent** (stack de IA de los 4 días).

### Paso 2: Terminal 1 — Levantar Servidor MCP Local
El servidor MCP conecta a los agentes con el backlog de GitHub Projects de forma segura:

```powershell
cd 00_support\mcp-local

# Con Podman (entorno oficial del curso):
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api"

# O con Docker Desktop (en máquina personal):
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api" -Engine docker
```
> 💡 *Deja esta terminal abierta durante todo el taller.*

### Paso 3: Terminal 2 — Activar Entorno y Ejecutar
En una segunda terminal, crea el entorno unificado para todo el día y ejecuta la sesión deseada:

```powershell
# 1. Ingresamos a la carpeta de la sesion y configuramos el env. (ejemplo S1)
cd s1_crewai
copy .env.example .env

# 2. Crear entorno
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 3. Ejecutar el pipeline
python main.py
```

> ℹ️ *Si el `list` sale vacío (el servidor solo trae proyectos vinculados al repo), el pipeline busca solo los projects de tu `GITHUB_OWNER`: uno → directo, varios → menú. Solo como último recurso pide pegar el node id. Opcional de una sola vez: vincúlalos con `link_to_repo`:*
> ```powershell
> $projId = gh project view <N> --owner "<OWNER>" --format json --jq .id
> foreach ($r in "workshop-auth-backend", "workshop-login-frontend", "workshop-requirements-api") {
>     python -c "from dotenv import load_dotenv; load_dotenv(); import mcp_projects; print(mcp_projects.call_tool('manage_project', {'action':'link_to_repo','projectId':'$projId','owner':'<OWNER>','repo':'$r'}))" | Select-Object -First 3
> }
> ```

---

## 📚 Biblioteca de Referencia Técnica (`docs/`)

Para profundizar en los fundamentos teóricos y las decisiones de diseño arquitectónico:

* 📐 **[01. Arquitectura Hexagonal](docs/01_arquitectura_hexagonal.md):** Las 7 capas, inversión de dependencias y validaciones deterministas (`OUT-HEX-01` y `OUT-HEX-02`).
* 🔌 **[02. Protocolo MCP y Servicios](docs/02_protocolo_mcp.md):** Arquitectura de `00_support`, transporte Streamable HTTP, JSON-RPC 2.0 y depuración con MCP Inspector.
* 🛡️ **[03. Harness Engineering y Constitución](docs/03_harness_y_constitucion.md):** Separación en 3 capas, inyección de la Constitución y cálculo de *Compliance Score*.
* 🧪 **[04. Guardrails de Producción y Evals](docs/04_guardrails_y_evals.md):** Ciclo iterativo `dev ↔ reviewer`, detección de PII y rúbrica formal del **Gate G2**.

---

## 🏁 Cierre del programa

El Día 4 no entrega a otro día: verifica el hilo completo. Antes de salir:

1. PR abierto desde el harness con `Closes #N` sobre tu issue (verifica `evidence/pr_url.txt`).
2. Gate G2 ≥ 80 % y rúbrica [EVALUACION-D4.md](EVALUACION-D4.md).
3. Marca el cierre en cada repo que cambiaste (`git tag day4-done && git push --follow-tags`).
4. Valida el hilo completo desde la carpeta del laboratorio:

```powershell
python tools/check_handoff.py --day 4 ../reqflow-workspace
```

El chequeo re-verifica los días 1–3 (hallazgo → HU → issue → spec) más el tag `day4-done`. Si algo falta, el reporte indica exactamente qué artefacto y en qué repo.

---

*NTT DATA Perú · Digital Architecture · Programa Train-the-Trainers IA BCP*

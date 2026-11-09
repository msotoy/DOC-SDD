# Sesión 1 — CrewAI: Orquestación Basada en Roles y HITL

> **Objetivo:** Leer una funcionalidad del backlog de un GitHub Project vía MCP y generarla con un equipo de 5 agentes CrewAI con supervisión humana (**Human-in-the-Loop**). El issue manda el alcance: solo corren los agentes de los stacks involucrados (backend/frontend/api); Designer y Reviewer siempre corren. Se trabaja SOBRE los repos de `reqflow-workspace` (rama local `agent/<slug>`, sin push).

---

## 🎯 ¿Qué hace esta sesión?

En esta sesión se orquesta un equipo de 5 agentes especializados:

1. **Software Architect & Designer:** Analiza el requerimiento y el árbol real de los repos involucrados; genera la especificación (`specs/user_story.md`).
2. **Senior Backend Engineer:** Modifica el repo `workshop-auth-backend` (Java Quarkus 3.x) en la rama de trabajo.
3. **API Developer:** Genera el scaffolding FastAPI completo en el repo `workshop-requirements-api`.
4. **Frontend Angular Developer:** Modifica el repo `workshop-login-frontend` (Angular 17).
5. **Technical Lead Reviewer:** Revisa el **diff real** de los repos y emite el veredicto (`APROBADO` o `RECHAZADO`).

Solo corren los agentes del alcance confirmado. Cada agente de código entrega archivos con encabezado `### <ruta relativa al repo>`; el pipeline los escribe en el repo (rechaza escapes y rutas protegidas como `HALLAZGOS.md`/`HU-*.md`/`.github/`). Nada commitea ni pushea.

Cada agente corre como un **Mini-Crew independiente**. Tras cada paso, el pipeline se detiene y te pide confirmación humana.

---

## 📋 Prerrequisitos para esta sesión

1. Tener corriendo el **Servidor MCP Local** en la Terminal 1 (puerto `8081`):
   ```powershell
   cd ..\00_support\mcp-local
   .\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api"
   ```
2. Tener activado el entorno virtual Python (`.venv` en esta carpeta).

---

## 🚀 Comandos para Ejecutar

### 1. Preparar las variables de entorno
```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```
Asegúrate de que en `.env` tengas configurado tu proveedor LLM y `PROJECTS_MCP_URL=http://localhost:8081`.

#### Usar tu suscripción de GitHub Copilot

S1 usa el SDK oficial de Copilot. CrewAI mantiene
los roles, el contexto entre pasos y las aprobaciones humanas. El SDK recibe
los prompts y devuelve texto; sus herramientas están deshabilitadas para que
la escritura de artefactos siga a cargo del pipeline de S1.

Requiere **Python 3.11–3.13** para estas dependencias de CrewAI, acceso a Copilot
en tu cuenta y autenticación.
Instala las dependencias de S1 como se muestra abajo. El SDK descarga su
runtime de Copilot automáticamente la primera vez. Puedes descargarlo antes:

```powershell
python -m copilot download-runtime
```

Para iniciar sesión, instala [Copilot CLI](https://github.com/features/copilot/cli),
ejecuta `copilot` y usa el comando `/login`. El SDK también admite `COPILOT_GITHUB_TOKEN`,
`GH_TOKEN` o `GITHUB_TOKEN` con acceso a Copilot. No guardes tokens en el repositorio.

Configura en tu `.env`:

```dotenv
COPILOT_MODEL=gpt-6-luna
COPILOT_REASONING_EFFORT=high
COPILOT_USE_LOGGED_IN_USER=true
```

S1 usa Copilot SDK con GPT-6 Luna y esfuerzo `high` por defecto.
Las llamadas y los reintentos consumen uso de tu plan de Copilot.
Ejecuta `python main.py` para iniciar el flujo.

### 2. Instalar dependencias (si usas venv local en esta carpeta)
En Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Iniciar el Pipeline
```powershell
python main.py
```

---

## 🎮 Interacción en Consola (Human-in-the-Loop)

1. El sistema cargará el backlog del MCP y te pedirá elegir un ítem:
   ```text
   Selecciona el número de feature [1-2]: 1
   ```
2. Verás el alcance propuesto (`Alcance: backend, frontend (...)`) y lo confirmas: Enter acepta, `b/f/a` ajusta stacks, `n` aborta. Solo los agentes involucrados corren y generan (un issue de `workshop-login-frontend` no genera backend).
3. Verás un spinner en tiempo real mientras el modelo genera el contenido:
   ```text
   [ | ] Generando con Copilot (01:23 transcurrido)...
   ```
3. Al finalizar, verás una tabla con el preview formateado y el banner de decisión:
   * **`s`** + Enter: **Aprobar** y avanzar al siguiente rol. Guarda el checkpoint en `output/.checkpoint.json`.
   * **`r`** + Enter: **Reintentar**. Podrás escribir un prompt adicional opcional (ej: *"agrega hash seguro con BCrypt"*).
   * **`n`** + Enter: **Rechazar** y abortar el flujo.
4. Si el Reviewer veredicta **RECHAZADO**, el loop no termina: **`r`** o **`c`** envían a corrección (máx 2 rondas — las observaciones vuelven a los agentes de código y se re-revisa), **`s`** acepta igual (queda registrado), **`n`** aborta (la rama y el checkpoint quedan para retomar). Todo cambio proviene de un paso aprobado: nada manual fuera del loop.

---

## 📦 Artefactos Generados

Specs por paso en `output/specs/` + archivos modificados/creados en los repos del workspace (rama `agent/<slug>`, local sin push). Solo los stacks del alcance confirmado.

```text
reqflow-workspace/
├── workshop-auth-backend/      ← modificado si backend en alcance (rama agent/...)
├── workshop-login-frontend/    ← modificado si frontend en alcance
└── workshop-requirements-api/  ← scaffolding FastAPI si api en alcance
s1_crewai/output/
├── .checkpoint.json               ← Estado + alcance + rama
└── specs/                         ← user_story.md · *_spec.md · lt_review.md
```

### ¿Cómo probar los cambios?
En cada repo tocado (rama `agent/<slug>`, sin pushear):
* **Backend Quarkus:** `mvn compile quarkus:dev` → http://localhost:8080/q/swagger-ui
* **API FastAPI:** `uvicorn app.main:app --reload` → http://localhost:8000/docs
* **Frontend Angular:** `npm install` + `npm start` → http://localhost:4200

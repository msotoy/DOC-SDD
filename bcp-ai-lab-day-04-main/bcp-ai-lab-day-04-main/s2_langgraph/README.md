# Sesión 2 — LangGraph: Workflows Stateful y Arquitectura Hexagonal

> **Objetivo:** Orquestar el mismo flujo de generación bancaria que en S1, pero sustituyendo los roles de CrewAI por un grafo de estado (**StateGraph**) con pausas controladas (`interrupt_before`). Como en S1, el issue manda el alcance y se trabaja SOBRE los repos de `reqflow-workspace` (rama local `agent/<slug>`, sin push): los nodos `backend_dev`/`api_dev`/`frontend_dev` se omiten si su stack no está involucrado.


## Modelo con GitHub Copilot SDK

Los nodos usan `github-copilot-sdk` y la sesión autenticada de Copilot CLI.
Desde la carpeta de esta sesión, instala las dependencias en Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edita `.env` con la configuración de tu repositorio y MCP. Después ejecuta:

```powershell
python main.py
```

Si Copilot no está autenticado, abre `copilot` y ejecuta `/login`.
El modelo predeterminado es `gpt-6-luna` con esfuerzo `high`. Puedes cambiarlo
con `COPILOT_MODEL` y `COPILOT_REASONING_EFFORT` en `.env`.
Antes de ejecutar `main.py`, configura en `.env` el repositorio y los valores del MCP
indicados en `.env.example`. No hace falta una API key de OpenAI.

---

## 🎯 ¿Qué hace esta sesión?

A diferencia de la orquestación basada en agentes de CrewAI, en LangGraph el flujo es un **Grafo Computacional**:

1. **`StateGraph` de 5 nodos:** `designer` → `backend_dev` → `api_dev` → `frontend_dev` → `reviewer` (solo corren los del alcance).
2. **Pausas (`interrupt_before`):** El grafo se detiene antes de cada nodo para dar el control al humano (`[s/r/n]`).
3. **Trabajo sobre repos reales:** cada nodo de código recibe el árbol del repo y entrega archivos con encabezado `### <ruta relativa>`; el pipeline los escribe en la rama local (rechaza escapes y rutas protegidas). El Reviewer recibe el diff real.
4. **Verificación determinista (`repo_report.md`):** manifiestos por stack presentes + archivos cambiados en la rama.

---

## 📋 Prerrequisitos

1. Servidor MCP de Proyectos corriendo en el puerto `8081` (Terminal 1).
2. Entorno virtual activo con `langgraph` instalado.

---

## 🚀 Comandos para Ejecutar

### 1. Configurar variables de entorno
```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

### 2. Verificar el workspace sin gastar tokens
Comprueba que el workspace por defecto resuelve (desde esta carpeta):
```powershell
python -c "from pathlib import Path; p = Path.cwd().parent.parent / 'reqflow-workspace'; print(p, p.is_dir())"
```
*Debe mostrar tu `reqflow-workspace` y `True` (o define `REQFLOW_WORKSPACE` en `.env`). El `hex_archetype.py` y `test_hex_wiring.py` quedan como referencia del diseño hexagonal original (ya no los usa el pipeline).*

### 3. Iniciar el Pipeline de LangGraph
```powershell
python main.py
```

---

## 🎮 Interacción en Consola

* Selecciona el proyecto y el feature del backlog.
* Confirma el alcance propuesto (Enter acepta, `b/f/a` ajusta, `n` aborta): los nodos fuera de alcance se omiten con evidencia, sin gastar tokens.
* El flujo ejecutará un nodo y se pausará con `interrupt_before`.
* Decisiones:
  * `s`: Continúa al siguiente nodo del grafo y guarda el estado en `output/.checkpoint.json`.
  * `r`: Reejecuta el nodo actual con nuevo contexto.
  * `n`: Cancela el grafo.
* Si el Reviewer veredicta **RECHAZADO**: `r` o `c` envían a corrección (máx 2 rondas — observaciones a los nodos y re-revisión), `s` sigue a guardar (queda registrado), `n` cancela (rama y checkpoint quedan para retomar). Todo cambio proviene de un paso aprobado: nada manual fuera del loop.
* Al finalizar, `output/repo_report.md` con manifiestos y archivos cambiados por repo.

---

## 📦 Artefactos Generados

Specs por paso en `output/` + archivos modificados/creados en los repos del workspace (rama `agent/<slug>`, local sin push). Solo los stacks del alcance confirmado.

```text
reqflow-workspace/
├── workshop-auth-backend/      ← modificado si backend en alcance
├── workshop-login-frontend/    ← modificado si frontend en alcance
└── workshop-requirements-api/  ← scaffolding FastAPI si api en alcance
s2_langgraph/output/
├── designer_spec.md · *_code.md · reviewer_report.md
├── repo_report.md                 ← manifiestos + cambiados por repo
└── .checkpoint.json
```

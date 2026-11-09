# Sesión 4 — Guardrails & Review Loop: Gobierno y Evaluación en Producción

> **Objetivo:** Implementar un **ciclo de revisión iterativo Dev ↔ Reviewer** con Pull Requests reales en GitHub, blindado por **guardrails de entrada/salida** y una suite completa de **evaluaciones deterministas (Evals)**.


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

Esta sesión cubre los dos patrones más avanzados de ingeniería de agentes en producción:

### 🔄 Pipeline A: Review Loop Iterativo (`main.py`)
En lugar de aceptar la primera respuesta del agente, se establece una conversación formal entre dos roles:
1. **Developer:** Propone los cambios de código.
2. **Reviewer:** Inspecciona la propuesta. Si tiene observaciones, devuelve el control al desarrollador indicando exactamente qué corregir.
3. El ciclo continúa de forma iterativa hasta que el código recibe aprobación limpia (o se alcanza el límite de rondas `MAX_REVIEW_ROUNDS=3`).
4. Al aprobar, publica una rama y crea el Pull Request mediante **GitHub CLI (`gh`)**.

### 🛡️ Pipeline B: Guardrails y Evaluaciones Deterministas (`evals/`)
Protege el sistema antes de gastar tokens y valida la calidad de salida:
* **Input Guardrails (`guardrails/input_check.py`):** Filtra longitud excesiva, palabras clave prohibidas y detección de información personal identificable (**PII**) antes de enviar prompts al LLM.
* **Output Guardrails (`guardrails/output_check.py`):** Verifica reglas estructurales del código generado (OUT-01 a OUT-06 y OUT-HEX).
* **Suite de Evals (`evals/eval_basic.py`):** Ejecuta 8 evaluaciones matemáticas/lógicas sobre el sistema y guarda los resultados en `evidence/eval_results.json`.

---

## 📋 Prerrequisitos

1. **GitHub CLI (`gh`)** autenticado (`gh auth login`).
2. Configurar `.env` a partir de `.env.example`.

---

## 🚀 Comandos para Ejecutar

### 1. Configurar variables de entorno
```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

### 2. Ejecutar el Review Loop y abrir el PR (Pipeline A)
```powershell
python main.py
```
*Observarás en la consola las rondas de feedback `dev ↔ reviewer` y la creación del Pull Request final en GitHub.*

### 3. Ejecutar la Suite de Guardrails y Evals (Pipeline B)
Para validar el sistema con las 10 pruebas deterministas y el Gate G2 sin depender del ciclo de PR:
```powershell
python evals/eval_basic.py
```
*Los resultados detallados se escribirán en `evidence/eval_results.json`.*

---

## 📦 Artefactos Generados en `evidence/` y `output/`

* `output/analysis.md`: Diagnóstico del repositorio.
* `output/chapter_plan.md`: Plan del Chapter Lead.
* `output/backend_refactor_r<N>.md`: Versiones del código por ronda de revisión.
* `output/reviewer_report_r<N>.md`: Feedback y veredicto por ronda.
* `evidence/eval_results.json`: Informe de las 8 evaluaciones deterministas.

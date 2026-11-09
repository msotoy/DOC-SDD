# Sesión 3 — Harness Engineering: Constitución y Pipeline de Refactorización

> **Objetivo:** Clonar un repositorio GitHub real, analizar sus vulnerabilidades de código con IA, inyectar una **Constitución de Seguridad** para guiar la refactorización, medir el cumplimiento de reglas deterministas y abrir un **Pull Request** automáticamente.


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

En esta sesión pasamos de generar código nuevo a **gobernar y refactorizar código existente**.

1. **Separación de Responsabilidades:**
   * **`graph/`**: Contiene los 5 nodos de trabajo (`analyze → chapter → backend → frontend → reviewer`). Es el **único** lugar donde vive el LLM.
   * **`harness/`**: Carga la constitución (`constitution.md`) y las políticas (`allowed_tools.json`), siembra el estado, orquesta las pausas y mide el cumplimiento de seguridad.
   * **`main.py`**: Clona el repositorio con Git, pide confirmación humana, extrae los cambios, hace commit y abre el Pull Request (vía MCP Git o `gh` CLI).
2. **Constitución de Seguridad (`harness/context/constitution.md`):**
   * Define las 6 reglas innegociables de ReqFlow (R1-R6): contratos preservados, secretos fuera del código, SQL parametrizado y contraseñas hasheadas, token firmado con expiración, errores genéricos y pruebas con trazabilidad al issue (`#N`) y al hallazgo (`H-xx`).
   * Se complementa con los artefactos de **tu** repo de los Días 1-3 (`REGLAS.md`, `docs/GOOD_PRACTICES.md`, `docs/ENDPOINTS.md`, `HALLAZGOS.md`, `openspec/specs/`): si son más específicos, prevalecen.
3. **Medición de Compliance (`compare()`):**
   * Evalúa el código resultante con 6 verificaciones deterministas (R1-R6) y genera el reporte `evidence/compliance_report.json`.

---

## 📋 Prerrequisitos

1. **GitHub CLI (`gh`)** autenticado (`gh auth login`) con permisos para clonar y abrir PRs en la organización configurada.
2. Servidor MCP Git (o fallback local con `gh`).
3. Variables de entorno configuradas en `.env`.

---

## 🚀 Comandos para Ejecutar

### 1. Configurar variables de entorno
```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```
Verifica que en `.env` tengas configurado el repositorio objetivo:
```env
GITHUB_OWNER=NTTData-Academy
GITHUB_REPO=workshop-requirements-api-template
GIT_BASE_BRANCH=main
```

### 2. Verificar el Grafo y el Harness (Sin gastar tokens del LLM)
Puedes comprobar que el grafo y el harness funcionan en tu máquina sin llamar a la API:
```powershell
python test_graph_hitl.py
python test_harness_flow.py
```

### 3. Iniciar el Pipeline de Refactorización
```powershell
python main.py
```

---

## 🎮 Flujo de Ejecución

1. El pipeline clona el repositorio en una carpeta temporal y toma un snapshot de su código.
2. El nodo `analyze` evalúa la calidad y detecta problemas de seguridad.
3. El nodo `chapter` arma el plan de refactorización según la Constitución.
4. Los nodos `backend` y `frontend` aplican las mejoras.
5. El nodo `reviewer` inspecciona el resultado. Si detecta incumplimientos, se activa un **retry automático** (hasta 3 rondas).
6. Una vez aprobado, crea una rama, hace commit, sube los cambios y abre el Pull Request en GitHub.

---

## 📦 Artefactos Generados en `evidence/` y `output/`

* `output/analysis.md`: Diagnóstico inicial del repositorio.
* `output/chapter_plan.md`: Plan de refactorización aprobado.
* `output/reviewer_report.md`: Veredicto del Tech Lead.
* `evidence/compliance_report.json`: Puntuación sobre las 5 reglas de la Constitución.

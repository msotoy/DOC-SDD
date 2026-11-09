# 🎓 Guía del Estudiante — BCP AI Lab (Día 04)

> **Programa Train-the-Trainers IA · NTT DATA Perú × BCP**  
> *Orquestación Multi-Agente, Workflows Stateful, Harness Engineering y Guardrails de Producción.*

---

## 📌 Recursos Visuales Interactivos

Para complementar esta guía técnica de terminal, dispones de dos tableros visuales interactivos en la raíz del repositorio. Puedes abrirlos haciendo doble clic sobre ellos en tu explorador de archivos o navegador:

* 📊 [laboratory-guide.html](laboratory-guide.html): **Dashboard Visual y Agenda Horaria** con el desglose de materiales, pasos paso a paso y la rúbrica formal del **Gate G2**.
* 🔀 [laboratory-flows.html](laboratory-flows.html): **Visualizador Interactivo de Flujos Multi-Agente** con diagramas animados del paso de mensajes entre agentes para S1, S2, S3 y S4.

> 💡 **Nota Importante sobre el Repositorio (Camino C):**  
> Este proyecto ya contiene todos los archivos fuente implementados y listos (`s1_crewai/`, `s2_langgraph/`, etc.). **No necesitas escribir ni copiar a mano archivos de código extensos** (como `mcp_projects.py`). Tu rol como estudiante es entender la arquitectura de agentes, ejecutar los pipelines, interactuar en las pausas humanas (HITL) y auditar los resultados.

---

## 🧭 1. Agenda del Día y Objetivos de Aprendizaje

El laboratorio está diseñado para una jornada intensiva de **8 horas netas**:

| Horario | Sesión | Tipo | Objetivo y Concepto Central |
| :--- | :--- | :--- | :--- |
| **08:00 – 10:00** | **S1 — CrewAI** | Generación | **Agentes por Roles + HITL:** Lee el backlog bancario vía MCP y coordina 4 agentes (Designer, Backend Quarkus, Frontend Angular, Líder Técnico). Genera proyectos ejecutables con soporte de reintento (`[s/n/r]`) y checkpoints reanudables. |
| **10:00 – 12:00** | **S2 — LangGraph** | Generación | **Workflows Stateful + Arquitectura Hexagonal:** Mismo objetivo que S1, pero modelado como un grafo de estado (`StateGraph`) con `interrupt_before` y estructurando el backend en **7 capas hexagonales** validadas de forma matemática determinista (`OUT-HEX`). |
| **12:00 – 13:00** | ☕ *Almuerzo* | Descanso | Pausa de integración. |
| **13:00 – 15:00** | **S3 — Harness** | Refactorización | **Harness Engineering + Constitución:** Clona **tu** `workshop-requirements-api`, acota el trabajo al issue `GITHUB_ISSUE` e inyecta la **Constitución ReqFlow** (R1-R6) junto con tus artefactos de los Días 1-3. Mide el *Compliance Score* y abre un Pull Request. |
| **15:00 – 17:00** | **S4 — Guardrails** | Gobierno & Evals | **Review Loop dev ↔ reviewer + Guardrails:** Ciclo iterativo de revisión de código con PR en GitHub, blindado por guardrails de entrada/salida (PII, tokens) y 8 evaluaciones deterministas (**Gate G2 ≥ 80%**). |

---

## ⚙️ 2. Prerrequisitos de tu Máquina

Verifica en tu terminal PowerShell que dispones de las siguientes herramientas:

```powershell
python --version   # Python 3.11 o 3.12
git --version      # Git instalado
gh --version       # GitHub CLI
```

### Contenedores (Podman o Docker)
El laboratorio está preparado para funcionar con cualquiera de los dos:
* **Podman** (Entorno oficial del laboratorio en BCP/NTT DATA).
* **Docker Desktop** (Completamente soportado si trabajas en tu máquina personal).

### Modelos LLM
* **GitHub Copilot (único LLM del laboratorio):** Copilot CLI instalado y autenticado (`copilot` → `/login`). Las sesiones usan Copilot SDK (`COPILOT_MODEL=gpt-6-luna`, esfuerzo `high`). No hay otra opción que configurar.

---

## 🐍 3. El Entorno Virtual (`.venv`)

Cada carpeta de sesión (`s1_crewai`, `s2_langgraph`, etc.) cuenta con su propio `requirements.txt`.  

```powershell
cd s1_crewai
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
*(Deberás repetir esto dentro de `s2_langgraph`, `s3_harness` y `s4_guardrails`).*

> 🏢 **¿Estás en laptop corporativa con VPN / Zscaler?**  
> Si al instalar paquetes o llamar al LLM ves el error `CERTIFICATE_VERIFY_FAILED`, descomenta la línea `pip-system-certs>=4.0` en el `requirements.txt` y vuelve a instalar con `python -m pip install -r requirements.txt`.

---

## 🚀 4. Plan de Vuelo: Paso a Paso Cronológico

Durante el día trabajarás con **2 terminales de PowerShell abiertas en paralelo**:

```
+------------------------------------+   +------------------------------------+
|       TERMINAL 1 (Servicios)       |   |       TERMINAL 2 (Pipeline)        |
|                                    |   |                                    |
|  Servidor MCP en puerto 8081       |   |  Ejecución de scripts Python       |
|  (No cerrar durante el lab)        |   |  (S1, S2, S3 o S4)                 |
+------------------------------------+   +------------------------------------+
```

---

### PASO 1 — Autenticar GitHub CLI (Una sola vez)
En cualquier terminal, autentícate y asegura los permisos para leer proyectos:

```powershell
gh auth login
gh auth refresh -s project
```

---

### PASO 2 — Terminal 1: Levantar el Servidor MCP Local
El servidor MCP permite que los agentes de S1 y S2 lean el backlog del proyecto en vivo.

```powershell
cd c:\...\bcp-ai-lab-day-04\00_support\mcp-local

# Con Podman (por defecto en el lab):
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api"

# O con Docker (si usas Docker Desktop):
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api" -Engine docker
```

> 💡 **Deja esta Terminal 1 abierta.** Verás que expone el servicio en el puerto `8081`.

> ⚠️ **Si S1/S2 dicen "No se encontraron proyectos"** aunque `gh` sí los vea: el `list` del servidor solo trae proyectos vinculados al repo, pero el pipeline busca solo los de tu owner (uno → directo, varios → menú) sin necesidad de vínculos. Opcional de una sola vez, vincular tus 3 repos (en Terminal 2, con `.venv` activo y `.env` ya copiado en `s1_crewai`):
> ```powershell
> $projId = gh project view <N> --owner "<OWNER>" --format json --jq .id
> foreach ($r in "workshop-auth-backend", "workshop-login-frontend", "workshop-requirements-api") {
>     python -c "from dotenv import load_dotenv; load_dotenv(); import mcp_projects; print(mcp_projects.call_tool('manage_project', {'action':'link_to_repo','projectId':'$projId','owner':'<OWNER>','repo':'$r'}))" | Select-Object -First 3
> }
> ```
> *(Reemplaza `<N>` por el número de tu Project ReqFlow.)*

---

### PASO 3 — Terminal 2: Configurar tu `.env`
Ve a la sesión con la que vas a trabajar (por ejemplo `s1_crewai`):

```powershell
cd c:\...\bcp-ai-lab-day-04\s1_crewai
copy .env.example .env
```

Abre el archivo `.env` en tu editor y verifica las variables de Copilot (vienen en `.env.example`, no hay otro LLM que configurar):

#### GitHub Copilot (único LLM):
```env
COPILOT_MODEL=gpt-6-luna
COPILOT_REASONING_EFFORT=high
COPILOT_USE_LOGGED_IN_USER=true
PROJECTS_MCP_URL=http://localhost:8081
```
Prerrequisito (una vez): Copilot CLI autenticado (`copilot` → `/login`).

---

### PASO 4 — Terminal 2: Ejecutar las Sesiones

#### 📍 Sesión 1: CrewAI + Human-in-the-Loop (08:00 – 10:00)
```powershell
cd c:\...\bcp-ai-lab-day-04\s1_crewai
python main.py
```
**Cómo interactuar con el pipeline:**
1. Elige un feature del backlog (ej: opción `1`).
2. Aparecerá un spinner animado que te indica que el agente está trabajando.
3. Al terminar cada agente, verás una tabla con el resumen del código o especificación.
4. Opciones de control humano (**HITL**):
   * `s` + Enter: **Aprobar** y avanzar al siguiente rol. Guarda el progreso en `output/.checkpoint.json`.
   * `r` + Enter: **Reintentar**. Podrás ingresar instrucciones adicionales opcionales para corregir al agente (ej: *"respeta el contrato de docs/ENDPOINTS.md"*).
   * `n` + Enter: **Rechazar** y abortar el flujo.

---

#### 📍 Sesión 2: LangGraph + Arquitectura Hexagonal (10:00 – 12:00)
```powershell
cd c:\...\bcp-ai-lab-day-04\s2_langgraph
copy .env.example .env     # (Configurar igual que en S1)
python main.py
```
* **Qué notarás diferente:** En vez de roles de CrewAI, el flujo corre sobre un grafo computacional con pausas automáticas (`interrupt_before`) y extrae el backend en **7 capas hexagonales** (`domain`, `application`, `infrastructure`). Al final, ejecuta un validador que comprueba que no haya violaciones de dependencias (`output/hex_report.md`).
* **Test sin tokens:** Puedes probar el validador sin gastar llamadas al LLM corriendo:
  ```powershell
  python test_hex_wiring.py
  ```

---

#### 📍 Sesión 3: Harness Engineering (13:00 – 15:00)
```powershell
cd c:\...\bcp-ai-lab-day-04\s3_harness
copy .env.example .env
python main.py
```
* **Qué aprenderás:** El script clona un repositorio real y ejecuta un pipeline donde se inyecta la **Constitución de Seguridad**. Mide en tiempo real si el código generado cumple las reglas (BCrypt con factor 12, JWT de 8h, rate limiting, etc.) y abre un Pull Request.

---

#### 📍 Sesión 4: Guardrails & Review Loop (15:00 – 17:00)
```powershell
cd c:\...\bcp-ai-lab-day-04\s4_guardrails
copy .env.example .env
python main.py
```
* **Qué aprenderás:** Observarás un diálogo automatizado entre un desarrollador y un revisor (`dev ↔ reviewer`) que se retroalimentan hasta que el código es perfecto antes de hacer push a GitHub.
* **Evaluaciones deterministas (Gate G2):**
  ```powershell
  python evals/eval_basic.py
  ```

---

## 🖥️ 5. ¿Cómo probar los proyectos generados en S1 y S2?

El pipeline no solo crea texto: genera proyectos completos en la carpeta `output/`. Para levantarlos en tu máquina:

### Probar el Backend (Java Quarkus)
```powershell
cd output\backend-quarkus
mvn compile quarkus:dev
```
* Abre tu navegador en: `http://localhost:8080` (con Swagger UI en `/q/swagger-ui`).

### Probar el Frontend (Angular 17)
```powershell
cd output\frontend-angular
npm install
npm start
```
* Abre tu navegador en: `http://localhost:4200`.

---

## 🏆 6. Criterio de Evaluación: Gate G2 (Cierre del Día)

Al finalizar la jornada, se evalúa el cumplimiento del **Gate G2** mediante la ejecución de la suite de evals:

```powershell
cd s4_guardrails
python evals/eval_basic.py
```

La rúbrica ponderada exige un score **≥ 80%**:
1. **Constitución ReqFlow (R1-R6):** contrato, secretos, datos, token, errores, pruebas + trazabilidad (**30%**).
2. **Contrato y trazabilidad:** análisis, plan y cambios sobre archivos reales de tu repo (**25%**).
3. **Calidad del pipeline:** hallazgos con severidad, plan, archivos extraíbles, veredicto y review loop (**20%**).
4. **Guardrails de Entrada/Salida:** el estado final pasa el guardrail de salida (**15%**).
5. **Apertura exitosa de Pull Request:** `main.py` abrió el PR con `Closes #GITHUB_ISSUE` (**10%**).

El cálculo está en `s4_guardrails/evals/gate_g2.py` y queda en `evidence/eval_results.json` (`gate_g2`).

---

## ❓ 7. Preguntas Frecuentes y Solución de Problemas

### 1. ¿Cómo vuelvo a ejecutar un paso desde cero si me equivoqué?
El pipeline guarda tu progreso en `output/.checkpoint.json`. Si quieres empezar de nuevo o probar otro feature:
```powershell
Remove-Item output\.checkpoint.json
python main.py
```

### 2. El comando `start-mcp.ps1` dice "Podman no está disponible"
Si tienes Docker Desktop en lugar de Podman, añade el parámetro `-Engine docker`:
```powershell
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api" -Engine docker
```

### 3. Al probar con `curl http://localhost:8081/mcp` recibo `400 Bad Request - No sessionId`
¡Eso es excelente! Significa que el servidor MCP está levantado y funcionando correctamente a la espera de peticiones de los agentes.

### 4. ¿Por qué la telemetría no me interrumpe?
CrewAI y OpenTelemetry han sido configurados para ejecutarse en segundo plano con timeouts cortos, por lo que recopilan métricas silenciosamente sin emitir advertencias molestas ni pausas en tu consola.

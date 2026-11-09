# Guardrails de Producción y Evaluaciones Deterministas (Evals)

> **Módulo de Referencia Técnica · BCP AI Lab (Día 04)**  
> *Alineado con Sesión 4 (`s4_guardrails`) y la aprobación formal del Gate G2.*

---

## 1. ¿Qué son los Guardrails y por qué son necesarios?

En sistemas financieros, no basta con pedirle al modelo que "actúe de forma segura". Los **Guardrails** son barreras deterministas que protegen la aplicación en dos frentes:

```text
[ Repositorio clonado ]
         │
         ▼
┌─────────────────────────────────┐
│   GUARDRAILS DE ENTRADA (Input) │ ← Valida el snapshot: tamaño, secretos, PII
└─────────────────────────────────┘   (Corta ANTES de gastar un solo token)
         │ (Snapshot limpio)
         ▼
┌─────────────────────────────────┐
│   HARNESS  →  GRAPH (5 nodos)   │ ← analyze → chapter → backend → frontend → reviewer
└─────────────────────────────────┘        ↑____________________________|
         │ (Estado final)                   review loop dev ↔ reviewer
         ▼
┌─────────────────────────────────┐
│   GUARDRAILS DE SALIDA (Output) │ ← Valida el estado antes de publicar
└─────────────────────────────────┘
         │ (Aprobado)
         ▼
[ Git Push / Pull Request ]
```

> **La entrada NO es un brief escrito a mano.** Es el código real del repositorio clonado. Cambiar `GITHUB_REPO` cambia los hallazgos: el análisis depende del snapshot, no de un texto fijo.

---

## 2. Guardrails de Entrada (`guardrails/input_check.py`)

`validate_snapshot()` corre **antes** del primer nodo del graph. Su lógica es *fallar rápido*: si lo que va a entrar al modelo no sirve, se corta ahí y no se paga la llamada para descubrirlo.

| Regla | Qué rechaza | Por qué |
| :--- | :--- | :--- |
| **Snapshot vacío** | No se pudo leer el repositorio | Sin código no hay nada que analizar |
| **Mínimo 200 chars** | Lectura casi vacía | El repo está vacío, o el filtro de extensiones dejó todo afuera |
| **Máximo 200.000 chars** | Repositorio desmesurado | No entra en ninguna ventana de contexto |
| **Secretos** | `sk-`, `ghp_`, `AKIA…`, claves privadas PEM | Si el repo los trae, mandarlos al modelo empeora el problema |
| **PII** | Tarjetas Visa y Mastercard | Datos de tarjeta no deben salir del repositorio |

El módulo conserva además `validate_input()` para texto libre (longitud, keywords de inyección como `DROP TABLE` / `rm -rf` / `exec(`, y los mismos patrones de secretos). El pipeline no la usa —su entrada es el snapshot— pero queda disponible para extensiones que reciban un brief escrito.

---

## 3. El Ciclo de Revisión Iterativo: Review Loop (`dev ↔ reviewer`)

El desarrollo no se da por terminado con el primer borrador. Se establece una conversación formal entre roles, **resuelta dentro del graph** (`graph/graph.py`), no en `main.py`:

1. **Ronda 1:** Los nodos `backend` y `frontend` generan los cambios según el plan.
2. **Auditoría:** El nodo `reviewer` evalúa y emite veredicto. `parse_verdict()` lo interpreta de forma conservadora:
   * `APROBADO` → el ciclo cierra.
   * `APROBADO CON OBSERVACIONES` o `RECHAZADO` → otra ronda.
   * *Texto ilegible* → también otra ronda. Ante la duda, no se aprueba.
3. **Rondas 2 y 3:** `should_retry()` devuelve el control a `backend`, y el estado arrastra `review_feedback` con las observaciones exactas. El developer **corrige**, no regenera a ciegas.
4. **Entrega:** El pipeline usa `gh pr create` para abrir el Pull Request.

> **Dos controles que no son lo mismo.** `interrupt_before` es el **HITL**: el grafo se detiene antes de cada nodo y el humano confirma con `[s/r/n]`. `should_retry` es el **review loop**: lo decide el veredicto. El humano confirma el resultado de cada ronda, pero no decide si hay ronda.

---

## 4. Guardrails de Salida (`guardrails/output_check.py`)

`validate_output()` revisa el estado final del graph antes del push. Cada regla lleva un código para trazabilidad:

| Código | Verifica | Por qué importa |
| :--- | :--- | :--- |
| **OUT-01** | `out_analysis`, `out_plan` y `out_reviewer` con ≥ 50 caracteres | Un campo obligatorio vacío significa que un nodo falló en silencio |
| **OUT-02** | El reviewer emitió un veredicto legible | Sin veredicto no se puede cerrar el ciclo |
| **OUT-03** | Los devs emitieron bloques `### ruta/archivo.ext` | Sin ese formato no se extrae ningún archivo y **el PR saldría vacío** |
| **OUT-04** | Ningún output contiene secretos (`sk-`, `ghp_`, `-----BEGIN`) | Un secreto en el PR es un incidente |

`out_backend` y `out_frontend` no son obligatorios por separado: dependen de `project_type`. Pero al menos uno debe traer contenido, o no hay cambios que publicar.

> **S4 no valida arquitectura hexagonal.** El repositorio que refactoriza es código ajeno: imponerle las 7 capas daría falsos negativos en cada corrida. Esa validación vive en **S2**, que genera el código desde cero y por tanto sí puede fijar la estructura — ver [01. Arquitectura Hexagonal](01_arquitectura_hexagonal.md).

---

## 5. Suite de Evaluaciones Deterministas (`evals/eval_basic.py`)

La suite corre el **pipeline completo sobre el repositorio real** —sin HITL— y evalúa el resultado con 10 tests deterministas. No juzgan la semántica del output: comprueban estructura y referencias verificables contra el repo.

```powershell
cd s4_guardrails
python evals/eval_basic.py
```

Los tres tests más exigentes cruzan las salidas contra archivos que **existen** en el repositorio:

* `analyze_referencia_el_repo_real` — si el análisis no nombra ningún archivo del repo, no está mirando el código real.
* `chapter_nombra_archivos_del_repo` — el plan debe apuntar a rutas que existan.
* `dev_toca_archivos_existentes` — al menos un archivo modificado debe estar en el repositorio original.

El informe consolidado se genera en `evidence/eval_results.json`, con el repo evaluado, las rondas de review consumidas y el veredicto final.

### Verificar sin gastar tokens

Dos checks parchean el LLM y no tocan MCP ni git:

```powershell
cd s4_guardrails
python test_graph_hitl.py     # HITL, review loop, feedback entre rondas, repo real
python test_harness_flow.py   # contexto, siembra, step, retry, resume, guardrails
```

`test_graph_hitl.py` es el que protege el diseño: si alguien quita `interrupt_before`, o reintroduce un brief fijo en lugar del snapshot, los checks fallan.

### Rúbrica Ponderada — Gate G2 (Cierre del Día)

Para aprobar formalmente el laboratorio, el sistema debe alcanzar un **Score Ponderado ≥ 80%**:

| Criterio Evaluado | Peso | Qué se comprueba (`evals/gate_g2.py`) |
| :--- | :---: | :--- |
| **Constitución ReqFlow (R1-R6)** | **30%** | Fracción de reglas atendidas por `check_security_compliance()`: contrato, secretos, datos, token, errores, pruebas + trazabilidad. |
| **Contrato y trazabilidad** | **25%** | El análisis, el plan y los cambios nombran archivos reales del repo del participante. |
| **Calidad del pipeline** | **20%** | Hallazgos con severidad, plan, bloques de archivo extraíbles, veredicto y review loop. |
| **Guardrails de Entrada/Salida**| **15%** | El estado final pasa `validate_output()` (secretos, campos, veredicto). |
| **Integración Git y PR** | **10%** | Existe `evidence/pr_url.txt`: `main.py` abrió el PR (con `Closes #GITHUB_ISSUE`). |

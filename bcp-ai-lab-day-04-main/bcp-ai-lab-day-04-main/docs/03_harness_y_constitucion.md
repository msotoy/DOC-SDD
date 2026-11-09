# Harness Engineering y Constitución de ReqFlow

> **Módulo de Referencia Técnica · BCP AI Lab (Día 04)**  
> *Alineado con Sesión 3 (`s3_harness`).*

---

## 1. ¿Qué es Harness Engineering?

En aplicaciones críticas bancarias, los agentes inteligentes no pueden operar sin supervisión ni restricciones duras. El patrón **Harness Engineering** introduce una capa externa de gobierno ("el arnés") que envuelve al grafo de agentes:

* El modelo no se re-entrena ni se ajusta mediante fine-tuning.
* El arnés inyecta una **Constitución de Seguridad** en el contexto del sistema.
* El arnés mide de forma determinista el grado de cumplimiento (*Compliance Score*) del código generado antes de permitir que llegue a producción.

---

## 2. Arquitectura en Tres Capas Limpias

La Sesión 3 separa estrictamente las responsabilidades del sistema:

| Capa | Componente | Responsabilidad | Lo que NUNCA debe hacer |
| :--- | :--- | :--- | :--- |
| **Núcleo LLM** | `graph/nodes.py` | Ejecuta las 5 tareas de análisis y código (`analyze → chapter → backend → frontend → reviewer`). | No conoce Git, ni llamadas MCP, ni la terminal. |
| **Arnés de Gobierno** | `harness/harness.py` | Carga la constitución, siembra el estado, entrega el control nodo a nodo y evalúa compliance. | No crea prompts ni llama al LLM directamente. |
| **Orquestador** | `main.py` | Clona el repositorio con Git, interactúa con el humano, commitea y abre el Pull Request. | No instancia modelos ni arma prompts de IA. |

---

## 3. La Constitución de Seguridad (`harness/context/constitution.md`)

La constitución define las reglas innegociables de **ReqFlow** (R1-R6). El arnés la carga **una sola vez** en `state["context"]` junto con los artefactos que el participante dejó en su repo los Días 1-3 (`REGLAS.md`, `docs/GOOD_PRACTICES.md`, `docs/ENDPOINTS.md`, `HALLAZGOS.md`, `openspec/specs/`, DoD) y el Issue en alcance (`GITHUB_ISSUE`). Cada nodo la aprovecha según su rol:

* **`analyze`:** Ignora la constitución a propósito para no sesgar el diagnóstico inicial del repositorio.
* **`chapter`:** Utiliza la constitución para acotar el alcance (*scope*) del plan de refactorización.
* **`backend` y `frontend`:** Restringen la generación de código prohibiendo contraseñas en texto plano y obligando el uso de librerías aprobadas.
* **`reviewer`:** Transforma la constitución en una lista de verificación (*checklist*) punto por punto.

---

## 4. Las 6 Reglas de Compliance Determinista (R1-R6)

El arnés ejecuta una evaluación determinista sobre el texto producido. Mide si el output **atiende** cada regla de la constitución; la verificación real son los tests del repo y `contract_evals.py`:

```python
{
    "R1_contrato_preservado":    bool,  # Cita los contratos (/auth/login, /api/tasks...) o docs/ENDPOINTS.md
    "R2_secretos_por_entorno":   bool,  # Secretos vía entorno (getenv, settings, AUTH_TOKEN_SECRET)
    "R3_datos_protegidos":       bool,  # SQL parametrizado y contraseñas hasheadas
    "R4_token_firmado_y_exp":    bool,  # Token firmado (HMAC/JWT) con expiración
    "R5_errores_genericos":      bool,  # Manejador global, sin stack traces ni innerHTML
    "R6_pruebas_y_trazabilidad": bool,  # Pruebas + referencia a H-xx o #issue
}
```

El resultado se registra en `evidence/compliance_report.json`.

---

## 5. Medición Cuantitativa: `compare()` (SIN vs CON Constitución)

Para demostrar científicamente el valor del arnés de ingeniería, el método `compare()` ejecuta el **mismo pipeline de refactorización dos veces** sobre el mismo repositorio:
1. **Corrida de Control (SIN Constitución):** Los agentes operan libremente solo con el prompt del feature.
2. **Corrida Gobernada (CON Constitución):** Se inyecta la constitución en el estado.

Al finalizar, compara ambos reportes de compliance, demostrando cómo la constitución eleva el cumplimiento de seguridad de un ~20% a un 100% sin intervención humana.

---

## 6. Dos Tipos de Control: HITL vs Retry Automático

* **`interrupt_before` (Human-in-the-Loop):** El grafo se detiene antes de cada nodo para que el humano valide el resultado (`[s/r/n]`).
* **`should_retry` (Bucle Condicional Automático):** Si el agente `reviewer` rechaza el código por incumplir la constitución y aún quedan intentos disponibles (`MAX_RETRIES=3`), LangGraph devuelve el flujo al nodo `backend` automáticamente con el feedback del revisor inyectado en el estado.

---

## 7. La Misma Arquitectura en S4

**S4 comparte esta arquitectura exacta.** No es otro diseño: son las mismas tres capas, el mismo grafo de 5 nodos sobre el repositorio clonado, y el mismo harness como única puerta de entrada. Lo que S4 agrega va *encima*, no *en lugar de*:

| | S3 Harness | S4 Guardrails |
| :--- | :--- | :--- |
| **Capas** | `main.py` → `harness/` → `graph/` | Idénticas |
| **Nodos** | `analyze → chapter → backend → frontend → reviewer` | Idénticos |
| **Entrada** | Snapshot del repositorio clonado | Idéntica |
| **Criterio de vuelta atrás** | `approved` booleano | **Veredicto** de `parse_verdict()` |
| **Feedback al developer** | Reintenta con el estado | **`review_feedback` con las observaciones exactas** |
| **Validación previa** | — | **Guardrail de entrada sobre el snapshot** |
| **Validación posterior** | Compliance Score | Compliance Score **+ guardrail de salida** |
| **Evaluación** | — | **Suite de 10 evals deterministas** |

La diferencia de fondo está en el criterio de retry. S3 vuelve atrás si `approved` es `False`. S4 lo decide por veredicto: **`APROBADO CON OBSERVACIONES` también dispara otra ronda**, y el developer recibe las observaciones textuales para corregir en vez de regenerar a ciegas.

Esa progresión es la que enseña la tarde del laboratorio: S3 introduce el gobierno por constitución; S4 le suma el diálogo iterativo y las barreras deterministas de entrada y salida.

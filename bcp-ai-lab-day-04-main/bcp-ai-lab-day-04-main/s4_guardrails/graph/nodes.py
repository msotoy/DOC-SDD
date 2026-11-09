"""
Nodos del graph LangGraph — pipeline de refactorización S4.

Un nodo es una función `(state) -> dict`: lee lo que necesita del WorkflowState
y devuelve SÓLO los campos que modifica. Aquí vive la única conexión al LLM de
la sesión — `main.py` no instancia modelos.

    analyze → chapter → backend → frontend → reviewer
                 ↑__________________________________|
                 review loop: el dev corrige con las observaciones

Lo que distingue a S4 de S3: los nodos `backend` y `frontend` inyectan
`review_feedback` en su prompt cuando `review_round > 1`. El developer no
regenera a ciegas — corrige lo que el reviewer señaló.

El análisis parte del `snapshot` del repositorio clonado, así que los hallazgos
cambian con cada repo. No hay brief fijo.
"""
import time

from dotenv import load_dotenv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lab_copilot.chat import CopilotChat

from graph.state import WorkflowState

load_dotenv()

_MAX_RETRIES = 3
_CTX_LIMIT   = 4000

_llm = CopilotChat()

def _invoke(prompt: str) -> str:
    """Invoca el LLM con reintentos exponenciales ante errores de red."""
    for attempt in range(_MAX_RETRIES):
        try:
            return _llm.invoke(prompt).content
        except Exception as e:
            if attempt == _MAX_RETRIES - 1:
                raise
            wait = 10 * (attempt + 1)
            print(f"  ⚠️  Error (intento {attempt + 1}/{_MAX_RETRIES}): {e} — reintentando en {wait}s")
            time.sleep(wait)


def _ctx(text: str, max_chars: int = _CTX_LIMIT) -> str:
    """Trunca el texto conservando inicio y fin, para no desbordar el prompt."""
    if not text or len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + f"\n\n[... +{len(text) - max_chars} chars omitidos ...]\n\n" + text[-half:]


def _runs(state: WorkflowState, area: str) -> bool:
    """True si el project_type elegido incluye esta área de implementación."""
    return state.get("project_type", "ambos") in (area, "ambos")


def _const_block(state: WorkflowState, nota: str) -> str:
    """Bloque de constitución para el prompt, vacío si se corre sin harness."""
    ctx = state.get("context", "")
    return f"\n{ctx}\n\n⚠️  {nota}\n\n" if ctx else ""


def _ronda(state: WorkflowState) -> int:
    """
    Ronda del dev que está por correr. `review_round` cuenta las revisiones
    ya emitidas (lo incrementa el reviewer), así que el dev va una adelante.
    """
    return state.get("review_round", 0) + 1


def _feedback_block(state: WorkflowState) -> str:
    """Observaciones de la ronda anterior — el corazón del review loop de S4."""
    if state.get("review_round", 0) < 1:
        return ""                      # primera ronda: todavía no hubo review
    feedback = state.get("review_feedback", "")
    if not feedback:
        return ""
    return (
        "\n⚠️  OBSERVACIONES DE LA RONDA ANTERIOR — incorpóralas TODAS:\n"
        f"{_ctx(feedback, 1500)}\n\n"
    )


# ── Nodo 1: Analyze ───────────────────────────────────────────────
def analyze_node(state: WorkflowState) -> dict:
    """
    Detecta problemas de calidad en el código clonado.
    No usa `context`: el diagnóstico del repo no debe sesgarse por la
    constitución. Los hallazgos salen del snapshot real, no de un brief.
    Escribe en: out_analysis
    """
    print("[analyze_node] Analizando calidad del código...")
    prompt = (
        "Eres un arquitecto de software senior. Analiza el siguiente código fuente\n"
        f"del repositorio {state['repo_name']} y detecta problemas de calidad.\n\n"
        "Evalúa:\n"
        "- Estructura y organización del código\n"
        "- Patrones de diseño aplicados o faltantes\n"
        "- Deuda técnica y code smells\n"
        "- Seguridad y manejo de errores\n"
        "- Testabilidad y mantenibilidad\n"
        "- Dependencias y versiones\n\n"
        f"Código del proyecto:\n{_ctx(state['snapshot'], 6000)}\n\n"
        "Responde con un análisis estructurado con hallazgos numerados y "
        "severidad (Alta/Media/Baja)."
    )
    return {"out_analysis": _invoke(prompt)}


# ── Nodo 2: Chapter Lead ──────────────────────────────────────────
def chapter_node(state: WorkflowState) -> dict:
    """
    Define el plan de refactorización a partir de los hallazgos reales.
    Usa `context` para acotar el scope del plan.
    Escribe en: out_plan
    """
    print("[chapter_node] Definiendo plan de refactorización...")
    prompt = (
        "Eres el Chapter Lead de un equipo de desarrollo. Tu rol es definir\n"
        f"el plan de refactorización del repositorio {state['repo_name']}.\n"
        + _const_block(state, "El plan DEBE respetar el scope de la constitución.")
        + f"\nTipo de proyecto: {state.get('project_type', 'ambos').upper()}\n\n"
        f"Análisis previo:\n{_ctx(state['out_analysis'], 3000)}\n\n"
        "Define un plan de refactorización claro con:\n"
        "1. Objetivos principales (máx 5)\n"
        "2. Cambios concretos por área (backend / frontend según aplique)\n"
        "3. Prioridad de cada cambio (Alta / Media / Baja)\n"
        "4. Estimación de impacto\n"
        "5. Archivos y módulos que deben modificarse\n\n"
        "Sé específico con rutas de archivos y cambios de código."
    )
    return {"out_plan": _invoke(prompt)}


# ── Nodo 3: Backend Developer ─────────────────────────────────────
def backend_node(state: WorkflowState) -> dict:
    """
    Implementa los cambios de backend del plan.
    En rondas > 1 incorpora las observaciones del reviewer.
    Se salta si project_type no incluye backend.
    Escribe en: out_backend
    """
    if not _runs(state, "backend"):
        print("[backend_node] project_type no incluye backend — saltando.")
        return {}

    print(f"[backend_node] Refactorizando backend (ronda {_ronda(state)})...")

    prompt = (
        "Eres un desarrollador backend senior. Implementa los cambios de backend\n"
        f"definidos en el plan para el repositorio {state['repo_name']}.\n"
        + _const_block(state, "El código DEBE cumplir las restricciones de la constitución.")
        + f"\nPlan de refactorización:\n{_ctx(state['out_plan'], 2000)}\n\n"
        f"Código actual del proyecto:\n{_ctx(state['snapshot'], 4000)}\n"
        + _feedback_block(state)
        + "Para cada archivo modificado, responde con el bloque completo en el formato:\n"
        "### path/relativo/al/repo/archivo.ext\n"
        "```\n<contenido completo del archivo>\n```\n\n"
        "Implementa solo cambios de backend (lógica de negocio, modelos, servicios, APIs).\n"
        "Mantén la coherencia con el resto del código existente."
    )
    return {"out_backend": _invoke(prompt)}


# ── Nodo 4: Frontend / API Developer ──────────────────────────────
def frontend_node(state: WorkflowState) -> dict:
    """
    Implementa los cambios de frontend/API del plan.
    Mismo tratamiento del feedback que el backend.
    Se salta si project_type no incluye frontend.
    Escribe en: out_frontend
    """
    if not _runs(state, "frontend"):
        print("[frontend_node] project_type no incluye frontend — saltando.")
        return {}

    print(f"[frontend_node] Refactorizando frontend/API (ronda {_ronda(state)})...")

    prompt = (
        "Eres un desarrollador frontend/API senior. Implementa los cambios de\n"
        f"frontend definidos en el plan para el repositorio {state['repo_name']}.\n"
        + _const_block(state, "El código DEBE cumplir las restricciones de la constitución.")
        + f"\nPlan de refactorización:\n{_ctx(state['out_plan'], 2000)}\n\n"
        f"Código actual del proyecto:\n{_ctx(state['snapshot'], 4000)}\n"
        + _feedback_block(state)
        + "Para cada archivo modificado, responde con el bloque completo en el formato:\n"
        "### path/relativo/al/repo/archivo.ext\n"
        "```\n<contenido completo del archivo>\n```\n\n"
        "Implementa solo cambios de frontend o API (componentes, rutas, clientes HTTP).\n"
        "Mantén la coherencia con el resto del código existente."
    )
    return {"out_frontend": _invoke(prompt)}


# ── Nodo 5: Tech Lead Reviewer ────────────────────────────────────
def reviewer_node(state: WorkflowState) -> dict:
    """
    Revisa los cambios y emite veredicto. Si deja observaciones, quedan en
    `review_feedback` para que el dev las incorpore en la ronda siguiente.

    Usa `context` como checklist de compliance.
    Escribe en: out_reviewer, review_feedback, last_verdict, approved, review_round
    """
    ronda = _ronda(state)          # esta revision incrementa el contador
    print(f"[reviewer_node] Revisando cambios (ronda {ronda})...")

    prev = (
        "\nEn rondas anteriores diste observaciones. "
        "Verifica si se han incorporado correctamente.\n"
        if ronda > 1 else ""
    )
    dev_outputs = "\n\n".join(filter(None, [
        state.get("out_backend", ""),
        state.get("out_frontend", ""),
    ])) or "(sin cambios de código)"

    prompt = (
        "Eres el Tech Lead del equipo. Revisa los cambios propuestos para\n"
        f"{state['repo_name']} y emite un veredicto técnico.\n{prev}"
        + _const_block(state, "Evalúa además el cumplimiento de la constitución (PII, "
                              "credenciales, compliance regulatorio).")
        + f"\nPlan original:\n{_ctx(state['out_plan'], 1500)}\n\n"
        f"Cambios implementados:\n{_ctx(dev_outputs, 3000)}\n\n"
        "Evalúa:\n"
        "1. ¿Los cambios cumplen con el plan?\n"
        "2. ¿Hay problemas de arquitectura o seguridad introducidos?\n"
        "3. ¿El código es mantenible y testeable?\n"
        "4. Calificación general (1-10)\n"
        "5. Veredicto final: APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO\n\n"
        "Si das observaciones, especifica EXACTAMENTE: archivo, línea aproximada y "
        "qué cambiar.\n"
        "Para terminar el ciclo escribe el veredicto en su propia línea en mayúsculas."
    )
    salida = _invoke(prompt)
    veredicto = parse_verdict(salida)

    etiqueta = {"aprobado": "APROBADO ✓",
                "observaciones": "APROBADO CON OBSERVACIONES",
                "rechazado": "RECHAZADO ✗"}[veredicto]
    print(f"[reviewer_node] Ronda {ronda}: {etiqueta}")

    return {
        "out_reviewer":    salida,
        "review_feedback": salida,          # lo lee el dev en la ronda siguiente
        "last_verdict":    veredicto,
        "approved":        veredicto == "aprobado",
        "review_round":    ronda,
    }


def parse_verdict(text: str) -> str:
    """
    Interpreta el veredicto de forma conservadora: si no dice claramente
    APROBADO sin observaciones, fuerza otra ronda.

    Retorna: "aprobado" | "observaciones" | "rechazado"
    """
    t = (text or "").lower()
    if "rechazado" in t or "rejected" in t:
        return "rechazado"
    if "aprobado con observaciones" in t or "approved with comments" in t:
        return "observaciones"
    if "aprobado" in t or "approved" in t:
        return "aprobado"
    return "observaciones"   # sin veredicto legible → conservador

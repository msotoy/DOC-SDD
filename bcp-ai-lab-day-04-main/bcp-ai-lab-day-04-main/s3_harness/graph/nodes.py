"""
Nodos del graph LangGraph — pipeline de refactorización S3.

Un nodo es una función `(state) -> dict`: lee los campos que necesita del
WorkflowState y devuelve SÓLO los campos que modifica. LangGraph mergea ese
dict en el estado y se lo pasa al nodo siguiente. Aquí vive la única conexión
al LLM de toda la sesión — `main.py` no instancia modelos.

Los cinco nodos replican el equipo del pipeline:
    analyze → chapter → backend → frontend → reviewer

`state["context"]` trae instructions + constitution + policies, cargados una
sola vez por el harness. Cada nodo decide cómo aplicarlo: el chapter lo usa
para acotar el scope del plan, los devs para restringir el código que generan,
y el reviewer lo convierte en checklist de compliance. Si viene vacío, el nodo
corre en modo libre — así `compare()` puede contrastar SIN y CON constitución.
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


# ── Nodo 1: Analyze ───────────────────────────────────────────────
def analyze_node(state: WorkflowState) -> dict:
    """
    Detecta problemas reales de calidad en el código clonado.
    No usa `context`: el análisis debe ser una lectura honesta del repo,
    sin que la constitución sesgue qué se considera un hallazgo.
    Escribe en: out_analysis
    """
    print("[analyze_node] Analizando calidad del código...")
    prompt = (
        f"Eres un Tech Lead senior. Analiza el código del repo '{state['repo_name']}':\n\n"
        f"{_ctx(state['snapshot'], 8000)}\n\n"
        "Identifica problemas reales de calidad de código:\n"
        "- Código duplicado o redundante\n"
        "- Responsabilidades mezcladas (violación SRP / SoC)\n"
        "- Falta de manejo de errores o excepciones\n"
        "- Configuraciones hardcodeadas que deberían ser variables de entorno\n"
        "- Falta de validaciones de input\n"
        "- Deuda técnica evidente (TODOs, hacks, workarounds)\n"
        "- Patrones de diseño mal aplicados o ausentes\n"
        "- Problemas de seguridad básica (secrets en código, SQL dinámico, etc.)\n\n"
        "Formato: lista Markdown. Para cada hallazgo: categoría, archivo afectado, "
        "descripción del problema, impacto. Máx 15 hallazgos concretos y accionables."
    )
    return {"out_analysis": _invoke(prompt)}


# ── Nodo 2: Chapter Lead ──────────────────────────────────────────
def chapter_node(state: WorkflowState) -> dict:
    """
    Define el plan de refactorización.
    Usa `context` para acotar el SCOPE: el plan no puede proponer cambios
    fuera de lo que la constitución permite.
    Escribe en: out_plan
    """
    print("[chapter_node] Definiendo plan de refactorización...")
    ctx = state.get("context", "")
    const_block = (
        f"\n{ctx}\n\n"
        "⚠️  El plan DEBE respetar las restricciones y el scope definidos en la constitución.\n\n"
    ) if ctx else ""

    prompt = (
        f"Eres el Chapter Lead (arquitecto) del equipo.\n"
        f"{const_block}"
        f"Análisis de código recibido:\n\n{_ctx(state['out_analysis'], 3000)}\n\n"
        f"Snapshot del código:\n\n{_ctx(state['snapshot'], 3000)}\n\n"
        "Define un plan de refactorización claro:\n"
        "1. **Archivos a modificar** — nombre exacto y qué cambiar en cada uno\n"
        "2. **Patrón a aplicar** — ej: Extract Service, Repository Pattern, Config class\n"
        "3. **Scope del PR** — qué queda fuera de esta iteración\n"
        "4. **Criterios de éxito** — qué debe cumplir el código refactorizado\n\n"
        "Organiza por área (backend, frontend/API). Sé específico con nombres de "
        "archivos y métodos. Formato Markdown."
    )
    return {"out_plan": _invoke(prompt)}


# ── Nodo 3: Backend Developer ─────────────────────────────────────
def backend_node(state: WorkflowState) -> dict:
    """
    Implementa los cambios de backend del plan.
    Usa `context` para restringir el CÓDIGO que genera (PII, credenciales,
    compliance regulatorio). Se salta si project_type no incluye backend.

    Incrementa `retry_count`: es el nodo al que vuelve `should_retry()`
    cuando el reviewer rechaza, así que cuenta los intentos del ciclo.
    Escribe en: out_backend, retry_count
    """
    if not _runs(state, "backend"):
        print("[backend_node] project_type no incluye backend — saltando.")
        return {}

    retry = state.get("retry_count", 0)
    retry_note = (
        f"\n⚠️  ATENCIÓN: este es el intento #{retry + 1}. El Reviewer rechazó el "
        "output anterior. Corrige los problemas que señaló:\n"
        f"{_ctx(state.get('out_reviewer', ''), 1500)}\n"
    ) if retry > 0 else ""
    print(f"[backend_node] Refactorizando backend (intento {retry + 1})...")

    ctx = state.get("context", "")
    const_block = (
        f"\n{ctx}\n\n"
        "⚠️  Todo el código que generes DEBE cumplir con las restricciones y regulaciones "
        "definidas en la constitución (PII, credenciales, compliance regulatorio).\n\n"
    ) if ctx else ""

    prompt = (
        f"Eres un Backend Developer senior.\n"
        f"{const_block}"
        f"Plan del Chapter Lead:\n\n{_ctx(state['out_plan'], 2500)}\n\n"
        f"Código actual:\n\n{_ctx(state['snapshot'], 3000)}\n"
        f"{retry_note}\n"
        "Implementa las refactorizaciones de backend definidas en el plan.\n"
        "Para cada archivo que modifiques, usa este formato EXACTO:\n\n"
        "### ruta/relativa/Archivo.ext\n"
        "```lenguaje\n"
        "<código completo refactorizado>\n"
        "```\n\n"
        "Solo archivos backend. Sin unit tests. Código listo para producción. "
        "Incluye comentarios donde el cambio no sea obvio."
    )
    return {
        "out_backend": _invoke(prompt),
        "retry_count": retry + 1,
    }


# ── Nodo 4: Frontend / API Developer ──────────────────────────────
def frontend_node(state: WorkflowState) -> dict:
    """
    Implementa los cambios de frontend/API del plan.
    Mismo uso de `context` que el backend. Se salta si project_type no
    incluye frontend.
    Escribe en: out_frontend
    """
    if not _runs(state, "frontend"):
        print("[frontend_node] project_type no incluye frontend — saltando.")
        return {}

    print("[frontend_node] Refactorizando frontend/API...")
    ctx = state.get("context", "")
    const_block = (
        f"\n{ctx}\n\n"
        "⚠️  Todo el código que generes DEBE cumplir con las restricciones y regulaciones "
        "definidas en la constitución (PII, credenciales, compliance regulatorio).\n\n"
    ) if ctx else ""

    prompt = (
        f"Eres un Frontend/API Developer senior.\n"
        f"{const_block}"
        f"Plan del Chapter Lead:\n\n{_ctx(state['out_plan'], 2500)}\n\n"
        f"Código actual:\n\n{_ctx(state['snapshot'], 3000)}\n\n"
        "Implementa las refactorizaciones de frontend o API definidas en el plan.\n"
        "Para cada archivo que modifiques, usa este formato EXACTO:\n\n"
        "### ruta/relativa/Archivo.ext\n"
        "```lenguaje\n"
        "<código completo refactorizado>\n"
        "```\n\n"
        "Solo archivos frontend/API. Sin tests. Código listo para producción. "
        "Incluye comentarios donde el cambio no sea obvio."
    )
    return {"out_frontend": _invoke(prompt)}


# ── Nodo 5: Tech Lead Reviewer ────────────────────────────────────
def reviewer_node(state: WorkflowState) -> dict:
    """
    Valida el trabajo del equipo y emite veredicto.
    Usa `context` como CHECKLIST de compliance — el único nodo que lo
    convierte en criterios verificables uno por uno.

    `approved` es True sólo con APROBADO limpio: "aprobado con observaciones"
    y "rechazado" devuelven False para que `should_retry()` mande otra ronda.
    Escribe en: out_reviewer, approved
    """
    print("[reviewer_node] Revisando el trabajo del equipo...")
    ctx = state.get("context", "")
    const_eval = (
        f"\nAdemás, evalúa que el código cumpla con la constitución del sistema:\n"
        f"{_ctx(ctx, 600)}\n\n"
        "- **Compliance constitución** (Y/N por regla):\n"
        "  [ ] ¿Se respeta el scope definido en la constitución?\n"
        "  [ ] ¿No hay datos PII ni credenciales reales en el código?\n"
        "  [ ] ¿Se cumple el cumplimiento regulatorio (SBS, PCI-DSS, ISO 27001)?\n"
        "  [ ] ¿Las decisiones que requieren aprobación humana están marcadas?\n\n"
    ) if ctx else ""

    prompt = (
        f"Eres el Tech Lead Reviewer. Revisa el trabajo del equipo.\n\n"
        f"Plan del Chapter:\n{_ctx(state['out_plan'], 1000)}\n\n"
        f"Backend refactorizado:\n{_ctx(state.get('out_backend', '') or '(no aplica)', 1500)}\n\n"
        f"Frontend/API refactorizado:\n{_ctx(state.get('out_frontend', '') or '(no aplica)', 1500)}\n\n"
        f"{const_eval}"
        "Emitir veredicto:\n"
        "- **Resultado**: ✅ APROBADO / ⚠️ APROBADO CON OBSERVACIONES / ❌ RECHAZADO\n"
        "- **Checklist** (Y/N por ítem):\n"
        "  [ ] ¿Se cumplió el plan del chapter?\n"
        "  [ ] ¿El código compila / es sintácticamente correcto?\n"
        "  [ ] ¿Se eliminaron los problemas detectados?\n"
        "  [ ] ¿No se introdujeron nuevos problemas?\n"
        "  [ ] ¿Está listo para el PR?\n"
        "- **Observaciones** para el PR description\n"
        "Máx 300 palabras."
    )
    review_text = _invoke(prompt)
    approved = parse_verdict(review_text) == "aprobado"

    print(f"[reviewer_node] Veredicto: {'APROBADO ✓' if approved else 'requiere otra ronda ✗'}")
    return {
        "out_reviewer": review_text,
        "approved":     approved,
    }


def parse_verdict(text: str) -> str:
    """
    Interpreta el veredicto de forma conservadora: si no dice claramente
    APROBADO sin observaciones, devuelve algo que fuerza otra ronda.

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

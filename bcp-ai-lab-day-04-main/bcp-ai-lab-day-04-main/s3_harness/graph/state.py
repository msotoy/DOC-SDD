"""
Estado compartido del workflow LangGraph — pipeline de refactorización S3.

Cada nodo lee y escribe sobre este TypedDict. El estado lo siembra el harness
(`harness.run_with_harness`) y lo hace avanzar `main.py`, un nodo por vez.
"""
from typing import TypedDict


class WorkflowState(TypedDict):
    """
    Estado del pipeline de refactorización de un repositorio real.

    Entrada (la siembra el harness antes del primer nodo):
        repo_name    : "owner/repo" del repositorio clonado.
        snapshot     : Código leído del repo, truncado para caber en el prompt.
        project_type : "backend" | "frontend" | "ambos". Determina qué nodos
                       de implementación corren y cuáles se saltan.
        context      : instructions.md + constitution.md + allowed_tools.json,
                       cargados UNA sola vez por el harness. Cada nodo decide
                       cómo usarlo: el chapter lo aplica al scope del plan, los
                       devs al código generado, el reviewer lo convierte en
                       checklist de compliance. Cadena vacía = modo sin harness.

    Outputs acumulados, uno por nodo:
        out_analysis : Hallazgos de calidad detectados en el código.
        out_plan     : Plan de refactorización del Chapter Lead.
        out_backend  : Archivos backend refactorizados (formato ### ruta/archivo).
        out_frontend : Archivos frontend/API refactorizados (mismo formato).
        out_reviewer : Veredicto técnico del Tech Lead Reviewer.

    Control del retry automático:
        approved     : True sólo si el reviewer aprueba SIN observaciones.
                       `should_retry()` lo usa para decidir si vuelve a backend.
        retry_count  : Intentos consumidos del ciclo backend→reviewer (máx 3).
    """
    # ── Entrada ──────────────────────────────────────────────────
    repo_name:    str
    snapshot:     str
    project_type: str
    context:      str

    # ── Outputs por nodo ─────────────────────────────────────────
    out_analysis: str
    out_plan:     str
    out_backend:  str
    out_frontend: str
    out_reviewer: str

    # ── Control ──────────────────────────────────────────────────
    approved:     bool
    retry_count:  int

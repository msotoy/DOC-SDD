"""
Definición y compilación del graph LangGraph — pipeline de refactorización S4.

Flujo:
    analyze → chapter → backend → frontend → reviewer
                           ↑__________________________|
                           review loop dev↔reviewer, máx MAX_REVIEW_ROUNDS

Misma forma que S3, con una diferencia en el criterio de vuelta atrás:

  · S3 vuelve si `approved` es False.
  · S4 vuelve según el **veredicto** (`last_verdict`), y arrastra las
    observaciones en `review_feedback` para que el dev corrija en vez de
    regenerar. "APROBADO CON OBSERVACIONES" también dispara otra ronda.

Dos controles que no son lo mismo:

  · `interrupt_before` — HITL. El grafo se detiene ANTES de cada nodo y
    devuelve el control a main.py, que muestra la salida y pide [s/r/n].
    Cada `graph.invoke(None, config)` ejecuta exactamente un nodo.

  · `should_retry` — review loop. Lo decide el veredicto, no el humano.
"""
import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import WorkflowState
from graph.nodes import (
    analyze_node,
    chapter_node,
    backend_node,
    frontend_node,
    reviewer_node,
)

# Rondas máximas del ciclo dev↔reviewer. Configurable por entorno.
MAX_REVIEW_ROUNDS = int(os.getenv("MAX_REVIEW_ROUNDS", "3"))

# Nodos en orden de ejecución. main.py recorre esta lista para el HITL.
NODES = ["analyze", "chapter", "backend", "frontend", "reviewer"]


def should_retry(state: WorkflowState) -> str:
    """
    Routing posterior al reviewer — el review loop de S4.

    Vuelve a `backend` mientras el veredicto no sea APROBADO limpio y queden
    rondas. El dev recibe `review_feedback` con las observaciones exactas.
    Agotadas las rondas, termina igual: el PR se abre con las observaciones
    registradas, que es lo que el lab quiere mostrar.
    """
    veredicto = state.get("last_verdict", "observaciones")
    ronda     = state.get("review_round", 0)

    if veredicto != "aprobado" and ronda < MAX_REVIEW_ROUNDS:
        print(f"[routing] Ronda {ronda}/{MAX_REVIEW_ROUNDS} — "
              f"veredicto '{veredicto}' → el dev incorpora observaciones")
        return "backend"

    if veredicto != "aprobado":
        print(f"[routing] Límite de {MAX_REVIEW_ROUNDS} rondas alcanzado "
              f"con veredicto '{veredicto}' — se cierra el ciclo")
    return END


def build_graph():
    """Construye y compila el graph con checkpointer y HITL por nodo."""
    builder = StateGraph(WorkflowState)

    builder.add_node("analyze",  analyze_node)
    builder.add_node("chapter",  chapter_node)
    builder.add_node("backend",  backend_node)
    builder.add_node("frontend", frontend_node)
    builder.add_node("reviewer", reviewer_node)

    # Flujo principal
    builder.set_entry_point("analyze")
    builder.add_edge("analyze",  "chapter")
    builder.add_edge("chapter",  "backend")
    builder.add_edge("backend",  "frontend")
    builder.add_edge("frontend", "reviewer")

    # Review loop
    builder.add_conditional_edges(
        "reviewer",
        should_retry,
        {"backend": "backend", END: END},
    )

    # HITL: pausa ANTES de ejecutar cada nodo. Sin esto, un solo invoke()
    # correría el pipeline entero y se perdería la aprobación humana.
    return builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=NODES,
    )


# Instancia global — la importa harness/harness.py
graph = build_graph()

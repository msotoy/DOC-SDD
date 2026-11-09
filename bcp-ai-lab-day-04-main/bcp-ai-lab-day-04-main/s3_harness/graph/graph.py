"""
Definición y compilación del graph LangGraph — pipeline de refactorización S3.

Flujo:
    analyze → chapter → backend → frontend → reviewer
                           ↑__________________________|
                           (retry automático si el reviewer no aprueba, máx 3)

Dos mecanismos de control que NO son lo mismo:

  · `interrupt_before` — HITL. El grafo se detiene ANTES de ejecutar cada nodo
    y devuelve el control a main.py, que muestra el output y pide [s/r/n].
    Cada `graph.invoke(None, config)` ejecuta exactamente un nodo.

  · `should_retry` — retry automático. Si el reviewer no aprueba y quedan
    intentos, la arista condicional vuelve a `backend` sin preguntar. El
    humano confirma el resultado de esa ronda, pero no decide si hay ronda:
    eso lo decide el veredicto.

El graph usa MemorySaver: el estado persiste entre invocaciones con el mismo
thread_id, que es lo que permite avanzar nodo a nodo sin perder el contexto.
"""
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

MAX_RETRIES = 3

# Nodos en orden de ejecución. main.py recorre esta lista para el HITL.
NODES = ["analyze", "chapter", "backend", "frontend", "reviewer"]


def should_retry(state: WorkflowState) -> str:
    """
    Routing posterior al reviewer.

    Si el veredicto no fue APROBADO limpio y quedan intentos, vuelve a
    `backend` con el feedback del reviewer en el estado. Agotados los
    intentos —o con aprobación— termina.
    """
    if not state.get("approved", False) and state.get("retry_count", 0) < MAX_RETRIES:
        print(f"[routing] Retry {state.get('retry_count', 0)}/{MAX_RETRIES} → volviendo a backend")
        return "backend"
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

    # Retry automático post-reviewer
    builder.add_conditional_edges(
        "reviewer",
        should_retry,
        {"backend": "backend", END: END},
    )

    # HITL: pausa ANTES de ejecutar cada nodo. Sin esto, un solo invoke()
    # correría los cinco nodos de corrido y se perdería la aprobación humana.
    return builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=NODES,
    )


# Instancia global — la importa harness/harness.py
graph = build_graph()

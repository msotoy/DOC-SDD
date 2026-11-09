"""
Grafo LangGraph S2 — flujo Designer → Backend → API → Frontend → Reviewer
(sólo corren los nodos del alcance; main.py omite el resto).

Checkpointing: intenta SqliteSaver (persistencia en disco).
Si el paquete no está instalado, cae a MemorySaver y main.py
maneja la persistencia con un archivo .checkpoint.json propio.

Para habilitar SqliteSaver:
    pip install langgraph-checkpoint-sqlite
"""
import sqlite3
from pathlib import Path
from langgraph.graph import StateGraph, END

from graph.state import WorkflowState
from graph.nodes import (
    designer_node,
    backend_dev_node,
    api_dev_node,
    frontend_dev_node,
    reviewer_node,
)

# ── Checkpointer: SqliteSaver si está disponible, sino MemorySaver ─
_CHECKPOINT_DB = Path(__file__).parent.parent / ".langgraph_checkpoint.db"

try:
    # Paquete separado en LangGraph >= 0.2
    from langgraph_checkpoint_sqlite import SqliteSaver as _SqliteSaver
    _conn = sqlite3.connect(str(_CHECKPOINT_DB), check_same_thread=False)
    checkpointer = _SqliteSaver(_conn)
    USING_SQLITE = True
except ModuleNotFoundError:
    try:
        # Versiones anteriores donde venía incluido
        from langgraph.checkpoint.sqlite import SqliteSaver as _SqliteSaver
        _conn = sqlite3.connect(str(_CHECKPOINT_DB), check_same_thread=False)
        checkpointer = _SqliteSaver(_conn)
        USING_SQLITE = True
    except ModuleNotFoundError:
        from langgraph.checkpoint.memory import MemorySaver
        checkpointer = MemorySaver()
        USING_SQLITE = False
        print(
            "ℹ️  SqliteSaver no encontrado — usando MemorySaver.\n"
            "   El checkpoint se guardará en .checkpoint.json (manejado por main.py).\n"
            "   Para persistencia nativa: pip install langgraph-checkpoint-sqlite\n"
        )

# ── Construcción del grafo ────────────────────────────────────────
builder = StateGraph(WorkflowState)

builder.add_node("designer",     designer_node)
builder.add_node("backend_dev",  backend_dev_node)
builder.add_node("api_dev",      api_dev_node)
builder.add_node("frontend_dev", frontend_dev_node)
builder.add_node("reviewer",     reviewer_node)

builder.set_entry_point("designer")
builder.add_edge("designer",     "backend_dev")
builder.add_edge("backend_dev",  "api_dev")
builder.add_edge("api_dev",      "frontend_dev")
builder.add_edge("frontend_dev", "reviewer")
builder.add_edge("reviewer",     END)

# HITL: pausa ANTES de ejecutar cada nodo
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["designer", "backend_dev", "api_dev", "frontend_dev", "reviewer"],
)

"""
Estado del grafo LangGraph S2 — mismo flujo que S1 CrewAI.
4 nodos: designer → backend_dev → frontend_dev → reviewer
con HITL antes de cada nodo.
"""
from typing import TypedDict


class WorkflowState(TypedDict):
    # Datos del feature seleccionado del backlog
    feature_title: str
    feature_brief: str
    acceptance: list

    # Contexto de los repos reales (árboles) + diff para el Reviewer
    repo_context: str
    review_diff: str

    # Loop de corrección: notas del Reviewer + ronda (máx 2)
    correction_notes: str
    correction_round: int

    # Outputs acumulados de cada agente
    designer_output: str
    backend_output: str
    api_output: str
    frontend_output: str
    reviewer_output: str

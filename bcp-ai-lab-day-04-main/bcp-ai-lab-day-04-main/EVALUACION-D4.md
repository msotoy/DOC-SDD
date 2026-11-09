# Evaluación D4 — Orquestación + Guardrails

Puerta de entrada: `check_handoff.py --day 3` en verde (apto / no apto, no puntúa). Umbral de salida: **promedio ponderado ≥ 8.0** + **Gate G2 ≥ 80 %**.

| # | Criterio | Peso | Aprueba (≥ 8) si… | Evidencia |
|---|---|---|---|---|
| 1 | Output | 30% | PR abierto desde el harness con `Closes #N` sobre el issue en `Todo`; `evidence/pr_url.txt`; backlog consumido, no inventado | PR, `GITHUB_ISSUE` acotando el alcance |
| 2 | Contenido | 30% | **Gate G2 ≥ 80 %** (30/25/20/15/10); `contract_evals` en verde; R1–R6 medidos (heurística declarada + tests reales) | `evals/gate_g2.py`, suite de 10 evals |
| 3 | Trazabilidad | 20% | Contexto del producto inyectado (`REGLAS.md`, `GOOD_PRACTICES.md`, `ENDPOINTS.md`, `HALLAZGOS.md`, specs, DoD); ciclo completo hallazgo → HU → issue → spec → PR demostrable | `load_product_context`, `load_issue_context` |
| 4 | Criterio humano | 20% | Review loop con decisión (approved / changes_requested / blocked); guardrails de entrada/salida activos; pausas HITL de S1/S2 atendidas; alcance confirmado por HITL y respetado (solo generan los stacks involucrados, sobre sus repos en rama local sin push) | Diálogo Dev ↔ Reviewer, checkpoints (incluyen `scope`), diff por repo |

Escala por criterio: 0 ausente · 1–3 parcial · 4–5 básico · 6–7 sólido · 8–10 ejemplar y verificable.

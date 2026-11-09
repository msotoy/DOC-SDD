# Evaluación D2 — Skills + MCP

Puerta de entrada: `check_handoff.py --day 1` en verde (apto / no apto, no puntúa). Umbral de salida: **promedio ponderado ≥ 8.0** + tag `day2-done`. El gate formal del día es **W1** con su propia rúbrica (`w1_evaluation/EVALUACION-W1.md`); esta rúbrica cubre S1–S3.

| # | Criterio | Peso | Aprueba (≥ 8) si… | Evidencia |
|---|---|---|---|---|
| 1 | Output | 30% | Skill S1 versionado (`v0.1.0` + tag), 6 Skills instalados por repo, `HU-01.md`/`HU-05.md` en su repo, un issue por HU en el Project ReqFlow, `.vscode/mcp.json`; commit + tags `lab02-s1/s2/s3`, `day2-done` | Tags, `check_handoff.py --day 2` en verde |
| 2 | Contenido | 30% | El Skill produce el documento del contrato sin inventar requisitos; HU-01/HU-05 con criterios verificables; matriz reutiliza `TESTING.md`; sin secretos | Documentos generados, `SDLC-EVIDENCE.md` |
| 3 | Trazabilidad | 20% | Cada HU tiene sección Origen con `H-xx`; cada issue completa `Hallazgo origen`; la matriz cita `H-xx` por prueba | `HU-*.md`, issues, matriz |
| 4 | Criterio humano | 20% | Revisión `pull-request-review` con decisión explícita; escritura MCP autorizada tras revisar la llamada; `read-only` entendido como reducción de superficie, no como frontera | Review con decisión, comparativa MCP local vs oficial |

Escala por criterio: 0 ausente · 1–3 parcial · 4–5 básico · 6–7 sólido · 8–10 ejemplar y verificable.

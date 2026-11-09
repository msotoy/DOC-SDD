# Evaluación D1 — Prompting + Secure AI

Puerta de entrada: ninguna (primer día). Umbral de salida: **promedio ponderado ≥ 8.0** + tag `day1-done`.

| # | Criterio | Peso | Aprueba (≥ 8) si… | Evidencia |
|---|---|---|---|---|
| 1 | Output | 30% | Existen `HALLAZGOS.md`, `PLAN.md`, `prompts/`, `docs/ENDPOINTS.md`, `docs/TESTING.md` en cada repo trabajado; commit + tag `day1-done` | `git tag day1-done`, `check_handoff.py --day 1` en verde |
| 2 | Contenido | 30% | Al menos una fila "Pendiente" con Id `H-xx`; contrato y pruebas coherentes con el código; sin secretos ni datos reales | `HALLAZGOS.md`, diff revisado |
| 3 | Trazabilidad | 20% | Cada hallazgo cita evidencia `archivo:línea`; `PLAN.md` referencia los `H-xx` que corrige | Referencias cruzadas en archivos |
| 4 | Criterio humano | 20% | El review del paso 3 confirma o reabre con motivo; nada mergeado sin comprenderlo | Veredicto en `HALLAZGOS.md` |

Escala por criterio: 0 ausente · 1–3 parcial · 4–5 básico · 6–7 sólido · 8–10 ejemplar y verificable.

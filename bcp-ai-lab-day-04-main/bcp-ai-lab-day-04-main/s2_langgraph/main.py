"""Punto de entrada — S2 LangGraph | mismo flujo que S1 CrewAI, sobre repos reales.

Checkpoint persistente en output/.checkpoint.json — si el proceso crashea,
al reiniciar se detecta el checkpoint y se ofrece continuar desde donde quedó.
Si SqliteSaver está disponible (pip install langgraph-checkpoint-sqlite),
el grafo también guarda su propio estado en .langgraph_checkpoint.db.

Se trabaja sobre reqflow-workspace en rama local agent/<slug> (sin push).
Los nodos de código escriben bloques `### <ruta relativa>` en el repo de su
stack; el cierre genera output/repo_report.md (manifiestos + cambiados).

Uso:
    cp .env.example .env
    python main.py
"""
import os
import re
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(override=True)
from graph.graph import graph, USING_SQLITE
from graph.state import WorkflowState

from mcp_projects import (
    list_tools as proj_tools,
    list_projects,
    list_project_items,
    get_feature_from_item,
    infer_scope,
    format_scope,
    resolve_project,
    list_owner_projects,
    STACK_REPO,
    slugify,
    resolve_workspace,
    repo_tree,
    ensure_branch,
    write_repo_files,
    repo_diffstat,
)
import mcp_projects
mcp_projects.set_verbose(os.getenv("MCP_VERBOSE", "false").lower() == "true")

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

CHECKPOINT_FILE = OUTPUT_DIR / ".checkpoint.json"

CONFIG = {"configurable": {"thread_id": "s2-langgraph-crew-01"}}

STEPS = ["designer", "backend_dev", "api_dev", "frontend_dev", "reviewer"]

STEP_LABELS = {
    "designer":     "Designer (Especificación técnica)",
    "backend_dev":  "Backend Developer (Repo Quarkus real)",
    "api_dev":      "API Developer (Scaffolding FastAPI)",
    "frontend_dev": "Frontend Developer (Repo Angular real)",
    "reviewer":     "Tech Lead Reviewer (Veredicto)",
}

OUTPUT_FIELDS = {
    "designer":     "designer_output",
    "backend_dev":  "backend_output",
    "api_dev":      "api_output",
    "frontend_dev": "frontend_output",
    "reviewer":     "reviewer_output",
}

OUTPUT_FILES = {
    "designer":     "designer_spec.md",
    "backend_dev":  "backend_code.md",
    "api_dev":      "api_code.md",
    "frontend_dev": "frontend_code.md",
    "reviewer":     "reviewer_report.md",
}

# Alcance por stack (lo resuelve el issue; Designer/Reviewer siempre corren).
# Los nodos de código se omiten si su stack no está involucrado.
_SCOPE: list = []
_STEP_STACK = {"backend_dev": "backend", "api_dev": "api", "frontend_dev": "frontend"}
SKIP_NOTE = "(omitido — fuera de alcance)"

# Repos reales por stack (se llenan tras el prompt del workspace).
STEP_REPOS: dict = {}
_BRANCH = ""
STACK_MANIFESTS = {
    "backend": ("pom.xml",),
    "frontend": ("package.json",),
    "api": ("requirements.txt", "app/main.py", "main.py"),
}

# Loop de corrección: un RECHAZADO del Reviewer vuelve a los nodos de código
# con las observaciones, hasta este máximo. Para eso está el loop.
MAX_CORRECTION_ROUNDS = 2
_CORR_ROUND = 0


def parse_verdict(output: str) -> str:
    m = re.search(r"VEREDICTO:\s*(APROBADO|RECHAZADO)", output or "", re.IGNORECASE)
    return m.group(1).upper() if m else "DESCONOCIDO"


# ── Persistencia de checkpoint en JSON ───────────────────────────
def save_checkpoint(state: dict, next_step: str) -> None:
    data = {
        "feature_title":   state.get("feature_title", ""),
        "feature_brief":   state.get("feature_brief", ""),
        "acceptance":      state.get("acceptance", []),
        "designer_output": state.get("designer_output", ""),
        "backend_output":  state.get("backend_output", ""),
        "api_output":      state.get("api_output", ""),
        "frontend_output": state.get("frontend_output", ""),
        "reviewer_output": state.get("reviewer_output", ""),
        "repo_context":    state.get("repo_context", ""),
        "review_diff":     state.get("review_diff", ""),
        "correction_notes": state.get("correction_notes", ""),
        "correction_round": state.get("correction_round", _CORR_ROUND),
        "next_step":       next_step,
        "scope":           list(_SCOPE),
    }
    CHECKPOINT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_checkpoint() -> dict | None:
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def clear_checkpoint() -> None:
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


# ── Utilidades de output ──────────────────────────────────────────
def save_step(step_key: str, content: str, current_state: dict) -> None:
    fname = OUTPUT_FILES[step_key]
    (OUTPUT_DIR / fname).write_text(content, encoding="utf-8")
    print(f"  ✅ output/{fname}")
    if step_key in STEP_REPO:
        total = write_repo_files(STEP_REPO[step_key], content)
        for rel in total:
            print(f"  💾 {STEP_REPO[step_key].name}/{rel}")
        if not total:
            print("  ⚠ Sin bloques `### ruta` válidos: nada escrito en el repo.")
    # Guardar checkpoint con el próximo paso
    idx = STEPS.index(step_key)
    next_step = STEPS[idx + 1] if idx + 1 < len(STEPS) else "done"
    save_checkpoint(current_state, next_step)


def save_skip(step_key: str) -> None:
    """Avanza el checkpoint sin ejecutar el nodo ni escribir archivos."""
    snapshot = graph.get_state(CONFIG)
    state_vals = dict(snapshot.values or {})
    idx = STEPS.index(step_key)
    next_step = STEPS[idx + 1] if idx + 1 < len(STEPS) else "done"
    save_checkpoint(state_vals, next_step)


# ── Detección de checkpoint ───────────────────────────────────────
def check_existing_checkpoint() -> tuple[bool, int, dict | None]:
    """
    Devuelve (reanudar, start_from_idx, checkpoint_data).
    Primero intenta SqliteSaver (si está activo), luego el JSON propio.
    """
    # ── Intentar via SqliteSaver ──────────────────────────────────
    if USING_SQLITE:
        try:
            snapshot = graph.get_state(CONFIG)
            if snapshot and snapshot.next:
                next_node = snapshot.next[0]
                if next_node in STEPS:
                    state_vals = snapshot.values or {}
                    return _ask_resume(state_vals, next_node), STEPS.index(next_node), None
        except Exception:
            pass

    # ── Intentar via JSON ─────────────────────────────────────────
    ckpt = load_checkpoint()
    if ckpt:
        next_step = ckpt.get("next_step", "")
        if next_step in STEPS:
            resume = _ask_resume(ckpt, next_step)
            return resume, STEPS.index(next_step), ckpt if resume else None

    return False, 0, None


def _ask_resume(state_vals: dict, next_node: str) -> bool:
    print("\n" + "─" * 60)
    print(f"[CHECKPOINT] Sesión anterior encontrada.")
    print(f"  Feature:      {state_vals.get('feature_title', 'desconocido')}")
    print(f"  Próximo paso: {STEP_LABELS.get(next_node, next_node)}")
    for s in STEPS:
        field = OUTPUT_FIELDS[s]
        done = bool(state_vals.get(field, ""))
        icon = "✅" if done else ("⏳" if s == next_node else "⬜")
        print(f"    {icon} {STEP_LABELS[s]}")
    print("─" * 60)
    return input("¿Reanudar desde ese punto? [s/N]: ").strip().lower() == "s"


# ── MCP Proyectos ─────────────────────────────────────────────────
print("[MCP Proyectos] Autenticando...")
_proj_tools = proj_tools()
print("[MCP Proyectos] Herramientas cargadas correctamente.")

_projects = list_projects()
if not _projects:
    # Project genérico sin vínculos: enumerar por owner vía gh (uno → directo,
    # varios → menú, como el flujo normal). Sin modificar el servidor.
    print("[MCP Proyectos] Sin vinculados al repo: buscando projects del owner...")
    _projects = list_owner_projects()
if not _projects:
    print("[MCP Proyectos] ✗ No se encontraron proyectos.")
    print("  gh project view <N> --owner <OWNER> --format json --jq .id")
    _pid = input("Pega el node id del Project (vacío=abortar): ").strip()
    if not _pid:
        raise SystemExit(1)
    try:
        _projects = [resolve_project(_pid)]
    except RuntimeError as exc:
        print(f"  {exc}")
        raise SystemExit(1)

if len(_projects) == 1:
    _selected_proj = _projects[0]
    print(f"\n[MCP Proyectos] Proyecto asignado: {_selected_proj.get('title', _selected_proj.get('name', ''))}")
else:
    print("\n[MCP Proyectos] Proyectos disponibles:")
    for _i, _proj in enumerate(_projects, 1):
        _icon = "⚫" if _proj.get("closed") else "🟢"
        print(f"  {_i}. {_icon} {_proj.get('title', _proj.get('name', '(sin título)'))}")
    while True:
        _sel = input(f"\nSelecciona el número de proyecto [1-{len(_projects)}]: ").strip()
        if _sel.isdigit() and 1 <= int(_sel) <= len(_projects):
            _selected_proj = _projects[int(_sel) - 1]
            break
        print(f"  ✗ Ingresa entre 1 y {len(_projects)}.")

_proj_id = _selected_proj.get("id") or _selected_proj.get("number") or _selected_proj.get("project_number")
_backlog = list_project_items(_proj_id)
if not _backlog:
    print("[MCP Proyectos] ✗ El proyecto no tiene items en el backlog.")
    raise SystemExit(1)

print(f"\n[MCP Proyectos] Backlog de '{_selected_proj.get('title', '')}':")
for _i, _item in enumerate(_backlog, 1):
    _icon = "⚫" if _item.get("state", "").lower() == "closed" else "🟢"
    _num  = f"#{_item['number']} — " if _item.get("number") else ""
    print(f"  {_i}. {_icon} {_num}{_item.get('title', '(sin título)')}")

while True:
    _sel = input(f"\nSelecciona el número de feature [1-{len(_backlog)}]: ").strip()
    if _sel.isdigit() and 1 <= int(_sel) <= len(_backlog):
        _selected_item = _backlog[int(_sel) - 1]
        break
    print(f"  ✗ Ingresa entre 1 y {len(_backlog)}.")

_feature = get_feature_from_item(_selected_item)
print(f"\n[MCP Proyectos] Feature seleccionado: {_feature.get('title', '')}")
if _feature.get("description"):
    print(f"  Descripción: {_feature['description'][:200]}...")
if _feature.get("acceptance_criteria"):
    print(f"  Criterios de aceptación: {len(_feature['acceptance_criteria'])} items")

# ── Alcance por stack (el issue manda) ───────────────────────────
_scope = infer_scope(_selected_item, _feature)
print(f"\n[MCP Proyectos] {format_scope(_scope)}")
while True:
    _ans = input("¿Alcance correcto? [Enter=aceptar / b,f,a=ajustar / n=abortar]: ").strip().lower()
    if _ans in ("", "s"):
        break
    if _ans == "n":
        print("Abortado.")
        raise SystemExit(0)
    _picked = [s for s, code in (("backend", "b"), ("frontend", "f"), ("api", "a")) if code in _ans]
    if _picked:
        _scope = {"stacks": _picked, "reasons": [f"ajuste manual: {_ans}"], "repo": _scope.get("repo")}
        break
    print("  ✗ Usa Enter, b/f/a o n.")
_SCOPE = list(_scope["stacks"])
_feature["description"] = (_feature.get("description") or "") + (
    "\n\n**Alcance del cambio (stacks involucrados):** "
    + ", ".join(_SCOPE)
    + ". Genera SOLO artefactos y código de esos stacks; "
    + "no emitas archivos de otros stacks."
)

# ── Workspace + repos reales (rama local, sin push) ─────────────
_ws_default = resolve_workspace(session_file=__file__)
_ws_ans = input(f"\nReqflow workspace [{_ws_default}]: ").strip()
WORKSPACE = resolve_workspace(_ws_ans, session_file=__file__)
STEP_REPOS: dict = {}
for _stack in _SCOPE:
    _repo_name = STACK_REPO.get(_stack)
    if not _repo_name:
        continue
    _repo_path = WORKSPACE / _repo_name
    if not _repo_path.is_dir():
        print(f"  ✗ Repo no encontrado: {_repo_path}")
        print("    Revisa REQFLOW_WORKSPACE o clona tus repos del Día 1. Abortando.")
        raise SystemExit(1)
    STEP_REPOS[_stack] = _repo_path
_BRANCH = "agent/" + slugify(_feature.get("title", "feature"))
for _stack, _repo_path in STEP_REPOS.items():
    _ok, _msg = ensure_branch(_repo_path, _BRANCH)
    print(f"  [{_repo_path.name}] rama {_BRANCH}: {_msg}" + ("" if _ok else " — ABORTANDO"))
    if not _ok:
        raise SystemExit(1)
print("  (rama local, sin push: el cambio queda sólo en tu disco)")
_REPO_CONTEXT = "\n\n".join(
    f"### {p.name}\n{repo_tree(p)}" for p in STEP_REPOS.values()
)
STEP_REPO = {_step: STEP_REPOS[_stack]
             for _step, _stack in _STEP_STACK.items() if _stack in STEP_REPOS}

initial_state: WorkflowState = {
    "feature_title":   _feature.get("title", ""),
    "feature_brief":   _feature.get("description", ""),
    "acceptance":      _feature.get("acceptance_criteria", []),
    "repo_context":    _REPO_CONTEXT,
    "review_diff":     "",
    "correction_notes": "",
    "correction_round": 0,
    "designer_output": "",
    "backend_output":  "",
    "api_output":      "",
    "frontend_output": "",
    "reviewer_output": "",
}

# ── Loop principal con HITL por paso ─────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("S2 LangGraph — mismo flujo CrewAI con LangGraph")
    print(f"Feature: {_feature.get('title', '')}")
    _STEP_SHORT = {"designer": "Designer", "backend_dev": "Backend", "api_dev": "API",
                   "frontend_dev": "Frontend", "reviewer": "Líder Técnico"}
    print("Pasos: " + " → ".join(_STEP_SHORT[s] for s in STEPS
                                 if s not in _STEP_STACK or _STEP_STACK[s] in _SCOPE))
    print("=" * 60)

    # ── Detectar checkpoint ───────────────────────────────────────
    resuming, start_from_idx, ckpt_data = check_existing_checkpoint()

    # Si el checkpoint es de otro alcance, empezar de cero
    if resuming and ckpt_data and ckpt_data.get("scope") and ckpt_data["scope"] != _SCOPE:
        print(f"\n⚠  El checkpoint existente es de otro alcance ({', '.join(ckpt_data['scope'])}).")
        print("   Se ignora y se empieza desde cero.")
        clear_checkpoint()
        resuming, start_from_idx, ckpt_data = False, 0, None

    if not resuming:
        _confirm = input("\n¿Iniciar ejecución del grafo? [s/N]: ").strip().lower()
        if _confirm != "s":
            print("Cancelado.")
            raise SystemExit(0)
        # Arrancar el grafo — se detiene antes del primer nodo
        graph.invoke(initial_state, CONFIG)
        # Guardar checkpoint inicial
        save_checkpoint(initial_state, STEPS[0])
    else:
        print(f"\n[RESUME] Reanudando desde: {STEP_LABELS[STEPS[start_from_idx]]}\n")
        # Si usamos MemorySaver, necesitamos inyectar el estado del JSON en el grafo
        if not USING_SQLITE and ckpt_data:
            resumed_state = {
                "feature_title":   ckpt_data.get("feature_title", ""),
                "feature_brief":   ckpt_data.get("feature_brief", ""),
                "acceptance":      ckpt_data.get("acceptance", []),
                "repo_context":    ckpt_data.get("repo_context", _REPO_CONTEXT),
                "review_diff":     ckpt_data.get("review_diff", ""),
                "correction_notes": "",
                "correction_round": ckpt_data.get("correction_round", 0),
                "designer_output": ckpt_data.get("designer_output", ""),
                "backend_output":  ckpt_data.get("backend_output", ""),
                "api_output":      ckpt_data.get("api_output", ""),
                "frontend_output": ckpt_data.get("frontend_output", ""),
                "reviewer_output": ckpt_data.get("reviewer_output", ""),
            }
            # Arrancar el grafo con el estado recuperado y adelantar hasta el paso correcto
            graph.invoke(resumed_state, CONFIG)
            # Adelantar el grafo hasta el paso correcto saltando los nodos ya hechos
            for _s in STEPS[:start_from_idx]:
                graph.update_state(
                    CONFIG,
                    {OUTPUT_FIELDS[_s]: resumed_state.get(OUTPUT_FIELDS[_s], "")},
                    as_node=_s,
                )
            # Re-posicionar el interrupt en el paso correcto
            graph.invoke(None, CONFIG)  # noqa: avanza hasta el primer interrupt real

    # ── Loop por paso ─────────────────────────────────────────────
    _CORR_ROUND = int((ckpt_data or {}).get("correction_round", 0))

    def _correct_from_rejection(output):
        """Ronda de corrección: observaciones → nodos de código → re-revisión."""
        global _CORR_ROUND
        from graph.nodes import (
            backend_dev_node as _be,
            api_dev_node as _ap,
            frontend_dev_node as _fe,
        )
        _CORR_ROUND += 1
        _notes = output[-3000:] if len(output) > 3000 else output
        print(f"\n🔄 Ronda de corrección {_CORR_ROUND}/{MAX_CORRECTION_ROUNDS}: observaciones → nodos.")
        graph.update_state(CONFIG, {"correction_notes": _notes,
                                    "correction_round": _CORR_ROUND})
        for _s, _fn in (("backend_dev", _be), ("api_dev", _ap),
                        ("frontend_dev", _fe)):
            if _STEP_STACK.get(_s) not in _SCOPE:
                continue
            print(f"  ▶ Corrigiendo {_s}...")
            _snap = graph.get_state(CONFIG)
            _new = _fn(dict(_snap.values or {}))
            graph.update_state(CONFIG, _new, as_node=_s)
            save_step(_s, _new[OUTPUT_FIELDS[_s]], dict(graph.get_state(CONFIG).values or {}))
        graph.update_state(CONFIG, {"correction_notes": ""})
        graph.invoke(None, CONFIG)

    for i, step_key in enumerate(STEPS):
        if i < start_from_idx:
            continue

        label        = STEP_LABELS[step_key]
        output_field = OUTPUT_FIELDS[step_key]

        # ── Paso fuera de alcance → omitir sin ejecutar el nodo ──
        if step_key in _STEP_STACK and _STEP_STACK[step_key] not in _SCOPE:
            print(f"\n⏭️  {label} — omitido (fuera de alcance: {', '.join(_SCOPE)}).")
            graph.update_state(CONFIG, {output_field: SKIP_NOTE}, as_node=step_key)
            graph.invoke(None, CONFIG)
            save_skip(step_key)
            continue

        print(f"\n{'─' * 60}")
        print(f"[HITL] Próximo paso: {label}")
        decision = input(f"¿Ejecutar {label}? [s/n]: ").strip().lower()
        if decision != "s":
            print(f"\n[HITL] Ejecución cancelada en paso '{label}'.")
            raise SystemExit(0)

        # El Reviewer necesita el diff real de los repos en el estado
        if step_key == "reviewer":
            _diffs = []
            for _stack, _repo_path in STEP_REPOS.items():
                _diffs.append(f"## Diff de {_repo_path.name} (rama {_BRANCH})\n{repo_diffstat(_repo_path, 8000)}")
            graph.update_state(CONFIG, {"review_diff": "\n\n".join(_diffs)})

        while True:
            graph.invoke(None, CONFIG)
            snapshot   = graph.get_state(CONFIG)
            state_vals = snapshot.values
            output     = state_vals.get(output_field, "")

            print(f"\n{'─' * 60}")
            print(f"[OUTPUT] {label}:")
            print(output[:1000] + ("..." if len(output) > 1000 else ""))
            print(f"\n[Output completo: {len(output)} caracteres]")

            # ── Loop de corrección: RECHAZADO vuelve a los nodos ──
            if step_key == "reviewer" and parse_verdict(output) == "RECHAZADO":
                if _CORR_ROUND >= MAX_CORRECTION_ROUNDS:
                    print(f"\n⚠ Sin rondas de corrección restantes (máx {MAX_CORRECTION_ROUNDS}). "
                          f"Decide con [s/n] abajo.")
                else:
                    _c = input("\n¿Enviar a corrección? [c=corregir / s=seguir a guardar / n=abortar]: ").strip().lower()
                    if _c == "n":
                        print(f"\n[HITL] Cancelado en paso '{label}'.")
                        raise SystemExit(0)
                    if _c == "c":
                        _correct_from_rejection(output)
                        continue

            retry = input(
                "\n¿Qué haces con este output? [s=guardar / r=reintentar / n=cancelar]: "
            ).strip().lower()

            if retry == "s":
                save_step(step_key, output, state_vals)
                break
            elif retry == "r":
                if step_key == "reviewer" and parse_verdict(output) == "RECHAZADO":
                    # Reintentar un RECHAZADO no es re-ejecutar al reviewer en
                    # vacío: es una ronda de corrección hacia los nodos.
                    if _CORR_ROUND >= MAX_CORRECTION_ROUNDS:
                        print(f"\n⚠ Sin rondas de corrección restantes (máx {MAX_CORRECTION_ROUNDS}); "
                              f"re-ejecutando al revisor igual...")
                    else:
                        _correct_from_rejection(output)
                        continue
                print(f"\n[RETRY] Reejecutando {label}...")
                from graph.nodes import (
                    designer_node,
                    backend_dev_node,
                    api_dev_node,
                    frontend_dev_node,
                    reviewer_node,
                )
                _node_fn = {
                    "designer":     designer_node,
                    "backend_dev":  backend_dev_node,
                    "api_dev":      api_dev_node,
                    "frontend_dev": frontend_dev_node,
                    "reviewer":     reviewer_node,
                }[step_key]
                new_output = _node_fn(state_vals)
                graph.update_state(CONFIG, new_output, as_node=step_key)
                continue
            elif retry == "n":
                print(f"\n[HITL] Cancelado en paso '{label}'.")
                raise SystemExit(0)
            else:
                print("  ✗ Opción inválida. Ingresa s, r o n.")

    clear_checkpoint()

    # ── Cierre: reporte estructural sobre los repos reales ──────────
    # Sin proyectos sintéticos: se verifica que cada repo involucrado
    # conserve sus manifiestos y se lista lo cambiado en la rama local.
    print("\n" + "─" * 60)
    print("▶ Verificación estructural de repos")
    print("─" * 60)
    _report = ["# Reporte estructural — S2 LangGraph", "",
               f"Rama local (sin push): `{_BRANCH}`", ""]
    for _stack, _repo_path in STEP_REPOS.items():
        _report.append(f"## {_repo_path.name} ({_stack})")
        for _mf in STACK_MANIFESTS.get(_stack, ()):
            _ok = (_repo_path / _mf).is_file()
            _report.append(f"- `{_mf}`: {'✅' if _ok else '❌ falta'}")
        try:
            import subprocess as _sp
            _r = _sp.run(["git", "-C", str(_repo_path), "status", "--porcelain"],
                         capture_output=True, text=True, timeout=15)
            _changed = [l for l in _r.stdout.splitlines() if l.strip()] if _r.returncode == 0 else []
        except Exception:
            _changed = []
        _report.append(f"- archivos cambiados: {len(_changed)}")
        for _l in _changed[:20]:
            _report.append(f"  - `{_l.strip()}`")
        _report.append("")
    (OUTPUT_DIR / "repo_report.md").write_text("\n".join(_report) + "\n", encoding="utf-8")
    print("  ✅ output/repo_report.md")

    print("\n" + "=" * 60)
    print("✅ Flujo S2 LangGraph completado.")
    print(f"Archivos guardados en: output/")
    print("=" * 60)

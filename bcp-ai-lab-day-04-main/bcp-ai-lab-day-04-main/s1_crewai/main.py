"""S1 CrewAI — Generador BCP con HITL y checkpoint por paso.

Flujo:
  1. Conecta al MCP Projects → lista proyectos → elige proyecto → lista backlog → elige feature
  2. El issue resuelve el alcance (stacks) y se confirma con el humano.
  3. Se trabaja sobre los repos de reqflow-workspace en rama local `agent/<slug>` (sin push).
  4. Por cada agente en alcance corre un mini-Crew de un solo paso.
  5. Tras cada paso muestra un preview y pide aprobación humana [s / n / r].
  6. Al aprobar: guarda la spec y escribe los archivos `### ruta` en el repo.
  7. Al volver a ejecutar: carga el checkpoint y omite los pasos ya aprobados.

Estructura:
  output/.checkpoint.json + output/specs/ (specs por paso).
  Código: archivos escritos en los repos involucrados de reqflow-workspace
  (rama agent/<slug>, local sin push).
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
import logging

# ---------------------------------------------------------------------------
# Telemetría y Tracing en segundo plano (Activos pero 100% No Intrusivos)
# ---------------------------------------------------------------------------
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "false"      # Telemetría habilitada
os.environ["CREWAI_TRACING_ENABLED"] = "true"         # Tracing habilitado
os.environ["OTEL_SDK_DISABLED"] = "false"             # OpenTelemetry activo
os.environ["OTEL_LOG_LEVEL"] = "error"                # No ensucia la terminal con logs informativos
os.environ["OTEL_BSP_EXPORT_TIMEOUT"] = "2000"        # Reduce timeout de exportación a 2s (evita cuelgues al salir)

# Silenciar loggers que puedan imprimir advertencias de red/telemetría en stderr
for _log in ("opentelemetry", "crewai.telemetry", "urllib3", "requests"):
    logging.getLogger(_log).setLevel(logging.ERROR)

try:
    from crewai.events.listeners.tracing.utils import (
        mark_first_execution_done,
        set_suppress_tracing_messages,
    )
    # 1. Registra consentimiento previo para eliminar el prompt interactivo de espera de 20s
    mark_first_execution_done(user_consented=True)
    # 2. Silencia banners y URLs en consola para no interferir con la interfaz HITL
    set_suppress_tracing_messages(True)
except Exception:
    pass

import re
import json
import time
import threading
import textwrap
from pathlib import Path
from crewai import Crew, Process

from crew.agents import chapter_agent, backend_agent, frontend_agent, api_agent, lt_agent
from crew.tasks  import build_tasks

# ── MCP clients ────────────────────────────────────────────────────
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
from hex_archetype import HEX_PROMPT_PREFIX

# ── Flag de verbosidad MCP ─────────────────────────────────────────
# True  → muestra el detalle de cada herramienta al arrancar
# False → solo confirma "Herramientas cargadas correctamente."
VERBOSE_MCP_TOOLS = False

# ── Rutas base ─────────────────────────────────────────────────────
OUTPUT_DIR      = Path(__file__).parent / "output"
CHECKPOINT_FILE = OUTPUT_DIR / ".checkpoint.json"
OUTPUT_DIR.mkdir(exist_ok=True)   # lo necesita save_checkpoint()

# ── Checkpoint ─────────────────────────────────────────────────────

def load_checkpoint() -> dict:
    """Carga el checkpoint si existe, o retorna estado vacío."""
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"steps": {}}


def save_checkpoint(data: dict) -> None:
    """Persiste el checkpoint en disco de forma segura."""
    try:
        clean_data = {}
        for k, v in data.items():
            if k == "steps" and isinstance(v, dict):
                clean_steps = {}
                for sk, sv in v.items():
                    if isinstance(sv, dict):
                        clean_steps[sk] = {
                            "status": sv.get("status"),
                            "output": str(getattr(sv.get("output"), "raw", sv.get("output")) or "")
                        }
                    else:
                        clean_steps[sk] = str(sv)
                clean_data[k] = clean_steps
            else:
                clean_data[k] = v
        CHECKPOINT_FILE.write_text(json.dumps(clean_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"  ⚠ Advertencia al guardar checkpoint: {e}")


def save_spec(filename: str, content) -> None:
    specs_dir = OUTPUT_DIR / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    text = str(getattr(content, "raw", content) or "")
    (specs_dir / filename).write_text(text, encoding="utf-8")
    print(f"  ✅ specs/{filename}")


# ── Mini-Crew: corre un único agente/tarea ─────────────────────────

class StepLoadingSpinner:
    """Indicador de carga interactivo con spinner y tiempo transcurrido en tiempo real."""
    def __init__(self, message: str = "Agente procesando con el LLM..."):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None

    def _spin(self):
        chars = ["|", "/", "-", "\\"]
        idx = 0
        t0 = time.time()
        # Pequeña pausa inicial para que CrewAI imprima sus recuadros iniciales
        time.sleep(1.0)
        while not self.stop_event.is_set():
            elapsed = int(time.time() - t0)
            mins, secs = divmod(elapsed, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            char = chars[idx % len(chars)]
            msg = f"\r  ⏳ [{char}] {self.message} ({time_str} transcurrido)   "
            try:
                sys.stdout.write(msg)
                sys.stdout.flush()
            except Exception:
                pass
            idx += 1
            time.sleep(0.2)
        try:
            sys.stdout.write("\r" + " " * 75 + "\r")
            sys.stdout.flush()
        except Exception:
            pass

    def __enter__(self):
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)


def run_step(agent, task) -> str:
    """Ejecuta un mini-Crew de un solo agente y retorna el output en texto."""
    mini_crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
        tracing=False,
    )
    with StepLoadingSpinner(f"Generando con {agent.llm.model}..."):
        result = mini_crew.kickoff()
    
    # Pausa para permitir que los callbacks y paneles asíncronos de CrewAI terminen de pintar en consola
    time.sleep(1.2)

    if hasattr(result, "raw") and result.raw:
        return str(result.raw)
    if hasattr(task, "output") and task.output:
        return str(getattr(task.output, "raw", task.output))
    return str(result)


# ── HITL: aprobación humana ────────────────────────────────────────

def _flush_input_buffer():
    """Limpia caracteres tecleados accidentalmente mientras el LLM generaba."""
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except Exception:
        pass


def print_formatted_preview(step_name: str, output: str, max_lines: int = 45) -> None:
    """Muestra el preview con formato enriquecido (tablas redondeadas alineadas, colores, preservando saltos de línea)."""
    output_str = str(getattr(output, "raw", output) or "").strip()
    if not output_str:
        print("  (Sin contenido generado)")
        return

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.box import ROUNDED

        console = Console()
        console.print(f"\n[bold cyan]{'─'*65}[/bold cyan]")
        console.print(f"[bold cyan]▶ OUTPUT GENERADO — {step_name}[/bold cyan]")
        console.print(f"[bold cyan]{'─'*65}[/bold cyan]\n")

        all_lines = output_str.splitlines()
        lines = all_lines[:max_lines]
        hidden_count = max(0, len(all_lines) - max_lines)

        table_lines = []
        in_table = False
        non_table_buffer = []

        def flush_buf():
            if non_table_buffer:
                console.print("\n".join(non_table_buffer))
                non_table_buffer.clear()

        def render_table(tbl_lines):
            if len(tbl_lines) < 2:
                for tl in tbl_lines:
                    console.print(tl)
                return
            headers = [c.strip() for c in tbl_lines[0].split("|")[1:-1]]
            if not headers:
                for tl in tbl_lines:
                    console.print(tl)
                return
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED, expand=True)
            for i, h in enumerate(headers):
                if i == 0:
                    table.add_column(h, style="cyan", ratio=3)
                elif i == 1 and any(k in h.lower() for k in ("estado", "status", "resultado")):
                    table.add_column(h, justify="center", ratio=1)
                else:
                    table.add_column(h, style="white", ratio=4)

            # Las filas de datos comienzan tras el separador | --- |
            for r in tbl_lines[2:]:
                cols = [c.strip() for c in r.split("|")[1:-1]]
                if len(cols) == len(headers):
                    table.add_row(*cols)
                elif cols:
                    while len(cols) < len(headers):
                        cols.append("")
                    table.add_row(*cols[:len(headers)])
            console.print(table)

        for line in lines:
            st = line.strip()
            if st.startswith("|") and st.endswith("|") and st.count("|") >= 2:
                if not in_table:
                    flush_buf()
                    in_table = True
                table_lines.append(st)
            else:
                if in_table:
                    render_table(table_lines)
                    table_lines.clear()
                    in_table = False
                non_table_buffer.append(line)

        if in_table:
            render_table(table_lines)
        flush_buf()

        if hidden_count > 0:
            console.print(f"\n[dim italic]... [{hidden_count} líneas adicionales guardadas en specs/ y código][/dim italic]")

        console.print(f"\n[bold cyan]{'─'*65}[/bold cyan]")

    except Exception:
        # Fallback sin formato especial si falla Rich
        sep = "─" * 65
        print(f"\n{sep}\n▶ OUTPUT GENERADO — {step_name}\n{sep}")
        print("\n".join(output_str.splitlines()[:max_lines]))
        print(sep)


def hitl_approve(step_name: str, output: str) -> tuple[str, str]:
    """
    Muestra un preview del output y pide aprobación de forma clara e interactiva.

    Retorna:
        ("s", "")         → aprobado
        ("n", "")         → rechazado (abortar)
        ("r", feedback)   → reintentar el paso (con feedback opcional del usuario)
    """
    import time
    time.sleep(0.3)
    
    print_formatted_preview(step_name, output)

    box_line = "=" * 65
    banner = f"""
{box_line}
 🔔 ACCIÓN REQUERIDA — Aprobación humana para: {step_name}
{box_line}
 [s] = Aprobar y continuar al siguiente paso
 [r] = Reintentar este mismo paso (permite ingresar feedback opcional)
 [n] = Rechazar y detener ejecución
{box_line}"""
    print(banner)

    while True:
        _flush_input_buffer()
        try:
            raw = input("\n👉 Ingresa tu opción [s/r/n] y presiona Enter: ").strip().lower()
        except EOFError:
            return "s", ""
        except KeyboardInterrupt:
            print("\n❌ Interrupción por teclado.")
            return "n", ""

        tokens = raw.split()
        choice = tokens[-1] if tokens else ""

        if not choice:
            continue

        if choice in ("s", "si", "sí", "y", "yes", "1") or choice.endswith("s"):
            return "s", ""
        if choice in ("n", "no", "0") or choice.endswith("n"):
            return "n", ""
        if choice in ("r", "retry", "reintentar") or choice.endswith("r"):
            print("\n💬 [Feedback Opcional] Escribe instrucciones adicionales para el agente")
            feedback = input("   (o presiona Enter para reintentar sin cambios): ").strip()
            return "r", feedback

        print("\n  ✗ Opción inválida. Por favor ingresa 's' para sí, 'r' para reintentar o 'n' para rechazar.")



# ── Contexto acumulado ─────────────────────────────────────────────

def _ctx_snippet(text: str, max_chars: int = 8000) -> str:
    """Recorta el output a max_chars para inyectarlo como contexto."""
    text_clean = str(text or "").strip()
    if len(text_clean) <= max_chars:
        return text_clean
    return text_clean[:max_chars] + "\n...(truncado para contexto)"


def build_context_note(approved_outputs: dict) -> str:
    """Construye una nota de contexto con los outputs aprobados anteriores."""
    parts = []
    labels = {
        "designer":    "Especificación técnica (Designer)",
        "backend_dev": "Implementación backend (Backend Dev)",
        "api_dev":     "Scaffolding API (API Dev)",
        "frontend_dev": "Implementación frontend (Frontend Dev)",
    }
    for key, label in labels.items():
        if key in approved_outputs:
            val = str(getattr(approved_outputs[key], "raw", approved_outputs[key]) or "")
            parts.append(f"### {label}\n{_ctx_snippet(val)}")
    if not parts:
        return ""
    return "\n\n---\n## Contexto de pasos anteriores\n\n" + "\n\n".join(parts)


MAX_CORRECTION_ROUNDS = 2


def parse_verdict(output) -> str:
    """APROBADO / RECHAZADO / DESCONOCIDO según el veredicto del Reviewer."""
    text = str(getattr(output, "raw", output) or "")
    m = re.search(r"VEREDICTO:\s*(APROBADO|RECHAZADO)", text, re.IGNORECASE)
    return m.group(1).upper() if m else "DESCONOCIDO"


def correction_notes(output, max_chars: int = 3000) -> str:
    """Observaciones del Reviewer (cola del reporte) para los agentes."""
    text = str(getattr(output, "raw", output) or "")
    return text if len(text) <= max_chars else text[-max_chars:]


def execute_step(step_key: str, step_label: str, agent, spec_file: str,
                 do_code: bool, extra_feedback: str = "") -> None:
    """Ejecuta un paso con su bucle de reintentos HITL hasta aprobar o abortar.

    extra_feedback: directiva inicial prioritaria (ronda de corrección).
    Al aprobar guarda spec, escribe archivos en el repo del paso y checkpoint.
    Con 'n' aborta el proceso completo (SystemExit).
    """
    user_feedback = extra_feedback
    while True:
        # Rebuild tasks fresh en cada intento
        t_story, t_backend, t_api, t_frontend, t_review = build_tasks(feature, repo_ctx)
        task_map = {
            "designer":    t_story,
            "backend_dev": t_backend,
            "api_dev":     t_api,
            "frontend_dev":t_frontend,
            "reviewer":    t_review,
        }
        task = task_map[step_key]

        # Inyectar contexto de pasos anteriores en la descripción
        ctx_note = build_context_note(approved_outputs)
        if ctx_note:
            task.description = task.description + ctx_note

        # El Reviewer revisa el diff real de los repos (rama local, amplio para evidencia)
        if step_key == "reviewer":
            _diffs = []
            for _stack, _repo_path in STEP_REPOS.items():
                _d = repo_diffstat(_repo_path, 8000)
                _diffs.append(f"## Diff de {_repo_path.name} (rama {BRANCH})\n{_d}")
            task.description += "\n\n---\n## Cambios reales en los repos\n" + "\n\n".join(_diffs)

        # Feedback (humano o de corrección) como directiva prioritaria
        if user_feedback:
            task.description += (
                f"\n\n---\n## ⚠️ INSTRUCCIONES ESPECÍFICAS DE CORRECCIÓN:\n"
                f"{user_feedback}\n"
                f"Por favor atiende y corrige con máxima prioridad las observaciones indicadas arriba.\n"
            )

        # Ejecutar mini-Crew
        output = run_step(agent, task)

        # HITL
        decision, user_feedback = hitl_approve(step_label, output)

        if decision == "s":
            # APROBADO
            print(f"\n✅ {step_label} aprobado. Guardando artefactos...")
            save_spec(spec_file, output)
            if do_code and step_key in STEP_REPO:
                _saved = write_repo_files(STEP_REPO[step_key], str(getattr(output, "raw", output) or ""))
                for _rel in _saved:
                    print(f"  💾 {STEP_REPO[step_key].name}/{_rel}")
                if not _saved:
                    print("  ⚠ Sin bloques `### ruta` válidos: nada escrito en el repo.")
            approved_outputs[step_key] = output
            steps_state[step_key] = {"status": "approved", "output": output}
            checkpoint["steps"] = steps_state
            save_checkpoint(checkpoint)
            return

        elif decision == "n":
            # RECHAZADO (el paso)
            print(f"\n❌ {step_label} rechazado. Abortando ejecución.")
            steps_state[step_key] = {"status": "rejected", "output": output}
            checkpoint["steps"] = steps_state
            save_checkpoint(checkpoint)
            raise SystemExit(0)

        else:
            # REINTENTAR
            if step_key == "reviewer" and parse_verdict(output) == "RECHAZADO":
                # Reintentar un RECHAZADO no es re-ejecutar al LT en vacío:
                # es una ronda de corrección hacia los agentes de código.
                _round = int(checkpoint.get("correction_round", 0))
                if _round >= MAX_CORRECTION_ROUNDS:
                    print(f"\n⚠ Sin rondas de corrección restantes (máx {MAX_CORRECTION_ROUNDS}); "
                          f"re-ejecutando al revisor igual...")
                else:
                    _round += 1
                    checkpoint["correction_round"] = _round
                    save_checkpoint(checkpoint)
                    _notes = correction_notes(output)
                    if user_feedback:
                        _notes += f"\n\nFeedback humano adicional:\n{user_feedback}"
                    print(f"\n🔄 Ronda de corrección {_round}/{MAX_CORRECTION_ROUNDS}: observaciones → agentes.")
                    for _ck, _cl, _ag, _sf, _dc in STEPS:
                        if not _dc:
                            continue  # sólo pasos de código
                        print(f"\n{'─'*60}\n▶ CORRECCIÓN ({_round}): {_cl}\n{'─'*60}")
                        execute_step(_ck, _cl, _ag, _sf, _dc, extra_feedback=_notes)
                    print(f"\n{'─'*60}\n▶ RE-REVISIÓN ({_round}): {step_label}\n{'─'*60}")
                    user_feedback = ""
                    continue
            if user_feedback:
                print(f"\n🔄 Reintentando {step_label} incorporando tu feedback: \"{user_feedback}\"...")
            else:
                print(f"\n🔄 Reintentando {step_label}...")
            # el while True vuelve a ejecutar el paso



# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

# ── MCP Proyectos: descubrir tools ────────────────────────────────
print("\n[MCP Proyectos] Autenticando...")
_proj_tools = proj_tools()
if VERBOSE_MCP_TOOLS:
    print("[MCP Proyectos] Herramientas disponibles:")
    for t in _proj_tools:
        print(f"  · {t['name']}: {t['description']}")
else:
    print("[MCP Proyectos] Herramientas cargadas correctamente.")

# ── Selección de proyecto ─────────────────────────────────────────
projects = list_projects()
if not projects:
    # Project genérico sin vínculos: enumerar por owner vía gh (uno → directo,
    # varios → menú, como el flujo normal). Sin modificar el servidor.
    print("[MCP Proyectos] Sin vinculados al repo: buscando projects del owner...")
    projects = list_owner_projects()
if not projects:
    print("[MCP Proyectos] ✗ No se encontraron proyectos.")
    print("  gh project view <N> --owner <OWNER> --format json --jq .id")
    _pid = input("Pega el node id del Project (vacío=abortar): ").strip()
    if not _pid:
        raise SystemExit(1)
    try:
        projects = [resolve_project(_pid)]
    except RuntimeError as exc:
        print(f"  {exc}")
        raise SystemExit(1)

if len(projects) == 1:
    selected_project = projects[0]
    print(f"\n[MCP Proyectos] Proyecto asignado: {selected_project['title']}")
else:
    print("\n[MCP Proyectos] Proyectos disponibles:")
    for i, proj in enumerate(projects, 1):
        icon = "⚫" if proj.get("closed") else "🟢"
        print(f"  {i}. {icon} {proj.get('title', '(sin título)')}")
    while True:
        sel = input(f"\nSelecciona el número de proyecto [1-{len(projects)}]: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(projects):
            selected_project = projects[int(sel) - 1]
            break
        print(f"  ✗ Entrada inválida.")

# ── Selección de feature del backlog ─────────────────────────────
backlog = list_project_items(selected_project["id"])
if not backlog:
    print("[MCP Proyectos] ✗ El proyecto no tiene items en el backlog.")
    raise SystemExit(1)

print(f"\n[MCP Proyectos] Backlog de '{selected_project['title']}':")
for i, item in enumerate(backlog, 1):
    icon = "⚫" if item.get("state", "").lower() == "closed" else "🟢"
    num  = f"#{item['number']} — " if item.get("number") else ""
    print(f"  {i}. {icon} {num}{item.get('title', '(sin título)')}")

while True:
    sel = input(f"\nSelecciona el número de feature [1-{len(backlog)}]: ").strip()
    if sel.isdigit() and 1 <= int(sel) <= len(backlog):
        selected_item = backlog[int(sel) - 1]
        break
    print(f"  ✗ Entrada inválida.")

feature = get_feature_from_item(selected_item)
print(f"\n[MCP Proyectos] Feature cargado: {feature['title']}")
print(f"[MCP Proyectos] Criterios de aceptación: {feature['acceptance_criteria']}")

# ── Alcance por stack (el issue manda) ───────────────────────────
# El backlog vive en el Project: el repo del issue + palabras clave del
# título/body resuelven qué stacks toca el cambio. Designer y Reviewer
# siempre corren; Backend/Frontend sólo si están involucrados.
scope = infer_scope(selected_item, feature)
print(f"\n[MCP Proyectos] {format_scope(scope)}")
while True:
    ans = input("¿Alcance correcto? [Enter=aceptar / b,f,a=ajustar / n=abortar]: ").strip().lower()
    if ans in ("", "s"):
        break
    if ans == "n":
        print("Abortando.")
        raise SystemExit(0)
    picked = [s for s, code in (("backend", "b"), ("frontend", "f"), ("api", "a")) if code in ans]
    if picked:
        scope = {"stacks": picked, "reasons": [f"ajuste manual: {ans}"], "repo": scope.get("repo")}
        break
    print("  ✗ Usa Enter, b/f/a o n.")
feature["description"] = (feature.get("description") or "") + (
    "\n\n**Alcance del cambio (stacks involucrados):** "
    + ", ".join(scope["stacks"])
    + ". Genera SOLO artefactos y código de esos stacks; "
    + "no emitas archivos de otros stacks."
)

# ── Workspace + repos reales (rama local, sin push) ─────────────
# Se trabaja sobre reqflow-workspace (el mismo de los Días 1-3), no sobre
# proyectos sintéticos. Nada commitea ni pushea: sólo archivos en disco.
_ws_default = resolve_workspace(session_file=__file__)
_ws_ans = input(f"\nReqflow workspace [{_ws_default}]: ").strip()
WORKSPACE = resolve_workspace(_ws_ans, session_file=__file__)
STEP_REPOS: dict[str, Path] = {}
for _stack in scope["stacks"]:
    _repo_name = STACK_REPO.get(_stack)
    if not _repo_name:
        continue
    _repo_path = WORKSPACE / _repo_name
    if not _repo_path.is_dir():
        print(f"  ✗ Repo no encontrado: {_repo_path}")
        print("    Revisa REQFLOW_WORKSPACE o clona tus repos del Día 1. Abortando.")
        raise SystemExit(1)
    STEP_REPOS[_stack] = _repo_path
BRANCH = "agent/" + slugify(feature["title"])
for _stack, _repo_path in STEP_REPOS.items():
    _ok, _msg = ensure_branch(_repo_path, BRANCH)
    print(f"  [{_repo_path.name}] rama {BRANCH}: {_msg}" + ("" if _ok else " — ABORTANDO"))
    if not _ok:
        raise SystemExit(1)
print("  (rama local, sin push: el cambio queda sólo en tu disco)")
repo_ctx = {
    _stack: {"repo": _repo_path.name, "tree": repo_tree(_repo_path)}
    for _stack, _repo_path in STEP_REPOS.items()
}
feature["description"] += "\n\n## Repos involucrados (estructura real)\n" + "\n\n".join(
    f"### {_repo_path.name}\n{repo_ctx[_stack]['tree']}" for _stack, _repo_path in STEP_REPOS.items()
)

# ── Cargar checkpoint ─────────────────────────────────────────────
checkpoint  = load_checkpoint()
steps_state = checkpoint.get("steps", {})

# Verificar si el checkpoint corresponde a este feature (por título)
ckpt_feature = checkpoint.get("feature_title")
if ckpt_feature and ckpt_feature != feature["title"]:
    print(f"\n⚠  El checkpoint existente es para '{ckpt_feature}'.")
    ans = input("¿Ignorar checkpoint y empezar desde cero? [s/n]: ").strip().lower()
    if ans == "s":
        steps_state = {}
        checkpoint  = {"steps": {}}
    else:
        print("Abortando. Cambia de feature o elimina output/.checkpoint.json para reiniciar.")
        raise SystemExit(0)

checkpoint["feature_title"] = feature["title"]

# Si el checkpoint es de otro alcance y ya tiene pasos aprobados, avisar
if checkpoint.get("scope") and checkpoint["scope"] != scope["stacks"] and steps_state:
    print(f"\n⚠  El checkpoint existente es de otro alcance ({', '.join(checkpoint['scope'])}).")
    ans = input("¿Ignorar checkpoint y empezar desde cero? [s/n]: ").strip().lower()
    if ans == "s":
        steps_state = {}
        checkpoint  = {"steps": {}}
    else:
        print("Abortando. Cambia de feature o elimina output/.checkpoint.json para reiniciar.")
        raise SystemExit(0)

checkpoint["scope"] = scope["stacks"]

# ── Recuperar outputs aprobados del checkpoint ────────────────────
approved_outputs: dict = {}
for step_key, step_data in steps_state.items():
    if step_data.get("status") == "approved":
        approved_outputs[step_key] = step_data.get("output", "")

# ── Enriquecer backstory del Chapter con brief del feature ────────
chapter_agent.backstory += HEX_PROMPT_PREFIX + (
    f"\n\n## Feature brief\n"
    f"**{feature['title']}**\n\n{feature['description']}\n\n"
    f"**Criterios de aceptación:** {', '.join(feature['acceptance_criteria'])}"
)

# ── Definición de pasos ───────────────────────────────────────────
# (key, label, agent, spec_filename, extraer_código)
# Designer y Reviewer siempre corren; Backend/Frontend sólo en su alcance.
STEPS = [
    ("designer",    "Designer — Especificación técnica",   chapter_agent,  "user_story.md",    False),
]
if "backend" in scope["stacks"]:
    STEPS.append(("backend_dev", "Backend Dev — Implementación Java",   backend_agent,  "backend_spec.md",  True))
if "api" in scope["stacks"]:
    STEPS.append(("api_dev", "API Dev — Scaffolding FastAPI",   api_agent,  "api_spec.md",  True))
if "frontend" in scope["stacks"]:
    STEPS.append(("frontend_dev","Frontend Dev — Componentes Angular",  frontend_agent, "frontend_spec.md", True))
STEPS.append(("reviewer",    "Líder Técnico — Revisión y veredicto",lt_agent,       "lt_review.md",     False))

_STEP_SHORT = {"designer": "Designer", "backend_dev": "Backend", "api_dev": "API",
               "frontend_dev": "Frontend", "reviewer": "Líder Técnico"}

# Repo destino por paso de código (la extracción escribe ahí, no en output/)
_STEP_STACK = {"backend_dev": "backend", "api_dev": "api", "frontend_dev": "frontend"}
STEP_REPO = {_step: STEP_REPOS[_stack] for _step, _stack in _STEP_STACK.items() if _stack in STEP_REPOS}

# Se trabaja sobre los repos reales (STEP_REPOS, rama local): no hay
# andamiaje sintético que generar en output/.

print("\n" + "=" * 60)
print(f"S1 CrewAI — HITL — Feature: {feature['title']}")
print("Pasos: " + " → ".join(_STEP_SHORT[k] for k, *_ in STEPS))
print("=" * 60)

# ── Loop HITL ─────────────────────────────────────────────────────
for step_key, step_label, agent, spec_file, do_code in STEPS:

    # ── Ya aprobado en ejecución anterior → omitir ───────────────
    if steps_state.get(step_key, {}).get("status") == "approved":
        print(f"\n✅ [{step_label}] — ya aprobado (checkpoint). Omitiendo.")
        if do_code and step_key in STEP_REPO:
            saved_out = steps_state[step_key].get("output", "")
            if saved_out:
                _saved = write_repo_files(STEP_REPO[step_key], str(getattr(saved_out, "raw", saved_out) or ""))
                if _saved:
                    print(f"  💾 Re-escritos en {STEP_REPO[step_key].name}: {len(_saved)} archivo(s)")
        continue

    print(f"\n{'─'*60}")
    print(f"▶ PASO: {step_label}")
    print(f"{'─'*60}")

    # ── Bucle de reintentos + loop de corrección ────────────────
    execute_step(step_key, step_label, agent, spec_file, do_code)

    # ── Loop de corrección: un RECHAZADO del Reviewer vuelve a los agentes
    # con las observaciones, hasta MAX_CORRECTION_ROUNDS. Para eso está el loop.
    if step_key == "reviewer":
        _round = int(checkpoint.get("correction_round", 0))
        while parse_verdict(approved_outputs.get("reviewer", "")) == "RECHAZADO":
            if _round >= MAX_CORRECTION_ROUNDS:
                print(f"\n⚠ Sin rondas de corrección restantes (máx {MAX_CORRECTION_ROUNDS}).")
                _w = input("¿Aceptar igual con observaciones? [s=aceptar / n=abortar]: ").strip().lower()
                if _w == "s":
                    break
                print("Abortando.")
                raise SystemExit(0)
            _c = input("\n¿Enviar a corrección? [c=corregir / s=aceptar igual / n=abortar]: ").strip().lower()
            if _c == "n":
                print("Abortando.")
                raise SystemExit(0)
            if _c == "s":
                break
            if _c != "c":
                print("  ✗ Usa c, s o n.")
                continue
            _round += 1
            checkpoint["correction_round"] = _round
            save_checkpoint(checkpoint)
            _notes = correction_notes(approved_outputs["reviewer"])
            print(f"\n🔄 Ronda de corrección {_round}/{MAX_CORRECTION_ROUNDS}: observaciones → agentes.")
            for _ck, _cl, _ag, _sf, _dc in STEPS:
                if not _dc:
                    continue  # sólo pasos de código
                print(f"\n{'─'*60}\n▶ CORRECCIÓN ({_round}): {_cl}\n{'─'*60}")
                execute_step(_ck, _cl, _ag, _sf, _dc, extra_feedback=_notes)
            print(f"\n{'─'*60}\n▶ RE-REVISIÓN ({_round}): {step_label}\n{'─'*60}")
            execute_step(step_key, step_label, agent, spec_file, do_code)

# ── Todos los pasos aprobados ─────────────────────────────────────
lt_text = str(getattr(approved_outputs.get("reviewer", ""), "raw", approved_outputs.get("reviewer", "")) or "")

print("\n" + "=" * 60)
print("✅ TODOS LOS PASOS APROBADOS")
print("=" * 60)
print("  output/specs/  → specs por paso (user_story.md · *_spec.md · lt_review.md)")
for _stack, _repo_path in STEP_REPOS.items():
    print(f"  {_repo_path.name}/ (rama {BRANCH}, local sin push):")
    try:
        import subprocess as _sp
        _r = _sp.run(["git", "-C", str(_repo_path), "status", "--porcelain"],
                     capture_output=True, text=True, timeout=15)
        _lines = [l for l in _r.stdout.splitlines() if l.strip()][:15] if _r.returncode == 0 else []
    except Exception:
        _lines = []
    if _lines:
        for _l in _lines:
            print(f"    {_l}")
    else:
        print("    (sin cambios en disco)")
print("=" * 60)
print("\nVEREDICTO del LT (extracto):")
print(lt_text[-500:] if len(lt_text) > 500 else lt_text)

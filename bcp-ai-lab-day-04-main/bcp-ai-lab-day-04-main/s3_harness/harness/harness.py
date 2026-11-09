"""
Harness Engineering — S3.

El harness es la ÚNICA puerta de entrada al graph. `main.py` no instancia
modelos ni arma prompts: siembra el estado aquí y hace avanzar el pipeline
nodo a nodo.

Qué aporta el harness sobre invocar el graph pelado:

  · **Contexto.** Carga instructions.md + constitution.md + allowed_tools.json
    UNA sola vez y los deja en `state["context"]`. Cada nodo decide cómo
    aplicarlo (ver graph/nodes.py). Sin harness, `context` viaja vacío y los
    nodos corren en modo libre — esa es exactamente la diferencia que mide
    `compare()`.

  · **Control paso a paso.** `step()` ejecuta un solo nodo y devuelve el
    control, para que main.py pueda mostrar el output y pedir aprobación.

  · **Evidencia.** Registra métricas de cada corrida en `evidence/`.

Uso típico desde main.py:

    from harness.harness import run_with_harness, next_node, step, retry_node

    run_with_harness(repo_name, snapshot, project_type, thread_id="s3-01")
    while next_node(thread_id):
        node, estado = step(thread_id)
        # ... mostrar output, pedir [s/r/n], eventualmente retry_node(...)
"""
import json
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

from graph.graph import graph, NODES
from graph.nodes import (
    analyze_node,
    chapter_node,
    backend_node,
    frontend_node,
    reviewer_node,
)
from graph.state import WorkflowState

# ── Rutas del harness ─────────────────────────────────────────────
_BASE          = Path(__file__).parent
_INSTRUCTIONS  = _BASE / "context"  / "instructions.md"
_CONSTITUTION  = _BASE / "context"  / "constitution.md"
_ALLOWED_TOOLS = _BASE / "policies" / "allowed_tools.json"
_EVIDENCE_DIR  = _BASE.parent / "evidence"
_EVIDENCE_DIR.mkdir(exist_ok=True)

# Nodo → función, para poder reejecutar uno solo en el retry manual.
_NODE_FNS = {
    "analyze":  analyze_node,
    "chapter":  chapter_node,
    "backend":  backend_node,
    "frontend": frontend_node,
    "reviewer": reviewer_node,
}

# Nodo → campo del estado donde deja su salida.
STATE_FIELD = {
    "analyze":  "out_analysis",
    "chapter":  "out_plan",
    "backend":  "out_backend",
    "frontend": "out_frontend",
    "reviewer": "out_reviewer",
}


# Artefactos que el participante dejó en su repo los Días 1-3. Son la
# fuente de verdad del producto: complementan la constitución genérica.
_PRODUCT_DOCS = (
    "REGLAS.md",                    # Día 1: reglas del laboratorio
    "docs/GOOD_PRACTICES.md",       # Día 1: convenciones del código
    "docs/ENDPOINTS.md",            # Día 1: contrato que no se rompe
    "HALLAZGOS.md",                 # Día 1: hallazgos con Id H-xx
    ".github/skills/reqflow-definition-of-done/SKILL.md",  # Día 3: DoD
)
_PRODUCT_GLOBS = ("openspec/specs/**/*.md",)  # Día 3: specs aprobadas
_MAX_DOC_CHARS = 4000


def load_product_context(repo_dir: Path | None) -> str:
    """Lee los artefactos de los Días 1-3 presentes en el repo clonado."""
    if repo_dir is None:
        return ""
    files = [repo_dir / rel for rel in _PRODUCT_DOCS]
    for pattern in _PRODUCT_GLOBS:
        files += sorted(repo_dir.glob(pattern))
    parts = [
        f"--- {f.relative_to(repo_dir).as_posix()} ---\n"
        + f.read_text(encoding="utf-8", errors="ignore")[:_MAX_DOC_CHARS]
        for f in files if f.is_file()
    ]
    if not parts:
        print("  ⚠️  El repo no trae artefactos de los Días 1-3 (REGLAS, ENDPOINTS, specs...).")
        return ""
    print(f"  [HARNESS] Contexto del producto: {len(parts)} artefactos del repo.")
    return "=== CONTEXTO DEL PRODUCTO (Días 1-3, prevalece sobre supuestos) ===\n" + "\n\n".join(parts)


def load_issue_context(repo_full: str) -> str:
    """Trae el Issue del Project ReqFlow indicado en GITHUB_ISSUE (vía `gh`)."""
    number = os.getenv("GITHUB_ISSUE", "").strip()
    if not number or not repo_full:
        return ""
    r = subprocess.run(
        ["gh", "issue", "view", number, "--repo", repo_full, "--json", "number,title,body"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        print(f"  ⚠️  No se pudo leer el issue #{number}: {r.stderr.strip()[:200]}")
        return ""
    issue = json.loads(r.stdout)
    print(f"  [HARNESS] Alcance: issue #{issue['number']} — {issue['title']}")
    return (
        "=== ALCANCE: ISSUE DEL PROJECT REQFLOW (no resuelvas nada fuera de él) ===\n"
        f"#{issue['number']} {issue['title']}\n\n{issue['body']}"
    )


# ── Carga de contexto ─────────────────────────────────────────────
def load_context(repo_dir: Path | None = None, repo_full: str = "") -> str:
    """
    Arma el system context: instrucciones + constitución + política de
    herramientas + artefactos del producto + issue en alcance. Cadena vacía
    si falta la constitución — en ese caso el pipeline corre en modo libre.
    """
    try:
        instructions = _INSTRUCTIONS.read_text(encoding="utf-8")
        constitution = _CONSTITUTION.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"  ⚠️  harness/context/ no encontrado ({e.filename}) — sin constitución.")
        return ""

    bloques = [
        "=== INSTRUCCIONES DEL SISTEMA ===\n" + instructions,
        "=== CONSTITUCIÓN (restricciones obligatorias) ===\n" + constitution,
    ]

    # Las policies son opcionales: si faltan, el resto del contexto sigue valiendo.
    try:
        pol = json.loads(_ALLOWED_TOOLS.read_text(encoding="utf-8"))
        bloques.append(
            "=== POLÍTICAS DE HERRAMIENTAS ===\n"
            f"Permitidas: {', '.join(pol.get('allowed', []))}\n"
            f"Bloqueadas: {', '.join(pol.get('blocked', []))}"
        )
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  ⚠️  allowed_tools.json no utilizable ({e}) — contexto sin políticas.")

    bloques += filter(None, [load_product_context(repo_dir), load_issue_context(repo_full)])

    ctx = "\n\n".join(bloques)
    print(f"  [HARNESS] Contexto cargado ({len(ctx)} chars).")
    return ctx


# ── Manejo de sesión del graph ────────────────────────────────────
def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def state(thread_id: str) -> dict:
    """Estado actual del pipeline para ese thread."""
    return graph.get_state(_config(thread_id)).values


def next_node(thread_id: str) -> str | None:
    """Nodo que se ejecutaría a continuación, o None si el pipeline terminó."""
    nxt = graph.get_state(_config(thread_id)).next
    return nxt[0] if nxt else None


def _start(repo_name: str, snapshot: str, project_type: str,
           thread_id: str, context: str) -> dict:
    """Siembra el estado inicial. El graph queda pausado ANTES del primer nodo."""
    inicial: WorkflowState = {
        "repo_name":    repo_name,
        "snapshot":     snapshot,
        "project_type": project_type,
        "context":      context,
        "out_analysis": "",
        "out_plan":     "",
        "out_backend":  "",
        "out_frontend": "",
        "out_reviewer": "",
        "approved":     False,
        "retry_count":  0,
    }
    graph.invoke(inicial, _config(thread_id))
    return state(thread_id)


def run_with_harness(repo_name: str, snapshot: str, project_type: str,
                     thread_id: str, repo_dir: Path | None = None) -> dict:
    """
    Arranca el pipeline CON el contexto del harness inyectado.
    No ejecuta ningún nodo: deja el graph listo y pausado.
    """
    print(f"\n[harness] Arrancando CON harness (thread: {thread_id})")
    return _start(repo_name, snapshot, project_type, thread_id,
                  load_context(repo_dir, repo_name))


def run_without_harness(repo_name: str, snapshot: str, project_type: str,
                        thread_id: str, repo_dir: Path | None = None) -> dict:
    """
    Arranca el pipeline SIN contexto: los nodos corren en modo libre.
    Es la rama de control de `compare()`.
    """
    print(f"\n[harness] Arrancando SIN harness (thread: {thread_id})")
    return _start(repo_name, snapshot, project_type, thread_id, "")


def resume_with_harness(repo_name: str, snapshot: str, project_type: str,
                        thread_id: str, outputs: dict,
                        repo_dir: Path | None = None) -> dict:
    """
    Retoma una sesión anterior a partir de los outputs ya aprobados.

    El MemorySaver vive en proceso: al reiniciar `main.py` el estado del
    graph se perdió, aunque el checkpoint en disco conserve los artefactos.
    Aquí volvemos a sembrar y adelantamos el graph nodo a nodo con
    `update_state(as_node=...)`, sin reejecutar ninguno: LangGraph recalcula
    el nodo siguiente como si esos ya hubieran corrido.

    Args:
        outputs: campos del estado ya resueltos, p.ej.
                 {"out_analysis": "...", "out_plan": "..."}.

    Returns:
        Estado resultante. `next_node()` apunta al primer nodo sin salida.
    """
    _start(repo_name, snapshot, project_type, thread_id,
           load_context(repo_dir, repo_name))
    cfg = _config(thread_id)

    adelantados = []
    for nodo in NODES:
        valor = outputs.get(STATE_FIELD[nodo], "")
        if not valor:
            break                       # primer nodo pendiente: aquí seguimos
        graph.update_state(cfg, {STATE_FIELD[nodo]: valor}, as_node=nodo)
        adelantados.append(nodo)

    if adelantados:
        print(f"[harness] Adelantado sin reejecutar: {' → '.join(adelantados)}")
    return state(thread_id)


def step(thread_id: str) -> tuple[str | None, dict]:
    """
    Ejecuta EXACTAMENTE un nodo y devuelve (nombre_del_nodo, estado).
    Si el pipeline ya terminó, devuelve (None, estado).

    Depende de `interrupt_before` en graph.py: sin eso, un solo invoke
    correría el pipeline entero y se perdería el HITL.
    """
    nodo = next_node(thread_id)
    if nodo is None:
        return None, state(thread_id)
    graph.invoke(None, _config(thread_id))
    return nodo, state(thread_id)


def retry_node(thread_id: str, nodo: str) -> dict:
    """
    Reejecuta un nodo ya corrido y reinyecta su salida en el estado.
    Lo usa el `[r]` del HITL cuando el humano no acepta el output.
    """
    if nodo not in _NODE_FNS:
        raise ValueError(f"nodo desconocido: {nodo} (esperaba uno de {NODES})")
    cfg = _config(thread_id)
    salida = _NODE_FNS[nodo](graph.get_state(cfg).values)
    graph.update_state(cfg, salida, as_node=nodo)
    return state(thread_id)


def run_to_end(thread_id: str, max_steps: int = 40) -> dict:
    """Corre el pipeline hasta el final sin HITL. Lo usa `compare()`."""
    for _ in range(max_steps):
        if next_node(thread_id) is None:
            break
        graph.invoke(None, _config(thread_id))
    return state(thread_id)


# ── Evidencia ─────────────────────────────────────────────────────
def save_evidence(filename: str, content: str) -> Path:
    """Guarda un artefacto de evidencia en evidence/."""
    path = _EVIDENCE_DIR / filename
    path.write_text(content, encoding="utf-8")
    print(f"[harness] Evidencia guardada: {path.name}")
    return path


def _evidence_for(modo: str, thread_id: str, resultado: dict, elapsed: float) -> dict:
    return {
        "mode":        modo,
        "thread_id":   thread_id,
        "timestamp":   datetime.now().strftime("%Y%m%d_%H%M%S"),
        "elapsed_s":   elapsed,
        "repo":        resultado.get("repo_name", ""),
        "approved":    resultado.get("approved"),
        "retries":     resultado.get("retry_count", 0),
        "context_chars": len(resultado.get("context", "")),
        "output_chars": {
            k: len(resultado.get(k, "") or "")
            for k in ("out_analysis", "out_plan", "out_backend",
                      "out_frontend", "out_reviewer")
        },
    }


# ── Compliance ────────────────────────────────────────────────────
def check_security_compliance(response_text: str) -> dict[str, bool]:
    """
    Verifica las reglas de seguridad buscando patrones deterministas en el
    texto generado. Única implementación: `main.py` la importa de aquí.
    """
    # ponytail: heurística por palabras clave, mide si el output ATIENDE cada
    # regla, no si la cumple; la verificación real son los tests y contract_evals.
    t = (response_text or "").lower()
    has = lambda *words: any(w in t for w in words)  # noqa: E731
    return {
        "R1_contrato_preservado":  has("/auth/login", "/api/tasks", "/api/summary",
                                       "/api/requirements", "endpoints.md", "contrato")
                                   and "breaking change" not in t,
        "R2_secretos_por_entorno": has("getenv", "environ", "settings", "auth_token_secret",
                                       ".env", "variable de entorno"),
        "R3_datos_protegidos":     has("parametriz", "parameteriz", "preparedstatement",
                                       "placeholder", "hash", "bcrypt", "argon2", "pbkdf2"),
        "R4_token_firmado_y_exp":  has("token", "jwt") and has("exp", "expir")
                                   and has("firm", "sign", "hmac", "hs256", "rs256"),
        "R5_errores_genericos":    has("stack trace", "mensaje genérico", "mensajes genéricos",
                                       "generic", "exception_handler", "httpexception",
                                       "exceptionmapper", "innerhtml"),
        "R6_pruebas_y_trazabilidad": has("test", "prueba", "pytest")
                                     and re.search(r"\bh-\d+|#\d+", t) is not None,
    }


def _texto_evaluable(resultado: dict) -> str:
    """Concatena lo que producen los agentes, que es lo que se audita."""
    return " ".join(filter(None, [
        resultado.get("out_backend", ""),
        resultado.get("out_frontend", ""),
        resultado.get("out_reviewer", ""),
    ])) or str(resultado)


# ── Comparativa SIN vs CON ────────────────────────────────────────
def compare(repo_name: str, snapshot: str, project_type: str, run_id: str,
            repo_dir: Path | None = None) -> dict:
    """
    Corre el pipeline completo dos veces sobre el MISMO repo —sin y con
    constitución— y devuelve el compliance de cada rama.

    Corre sin HITL: es una medición, no una sesión interactiva.

    Returns:
        {
          "without_harness": {"response": str, "compliance": {regla: bool}, "score": "n/5"},
          "with_harness":    {...},
        }
    """
    salida = {}
    for modo, arranque in (("without_harness", run_without_harness),
                           ("with_harness",    run_with_harness)):
        thread = f"{run_id}-{'sin' if modo.startswith('without') else 'con'}"
        inicio = time.time()
        arranque(repo_name, snapshot, project_type, thread, repo_dir)
        resultado = run_to_end(thread)
        elapsed = round(time.time() - inicio, 2)

        texto = _texto_evaluable(resultado)
        compliance = check_security_compliance(texto)
        score = f"{sum(compliance.values())}/{len(compliance)}"

        ev = _evidence_for(modo, thread, resultado, elapsed)
        ev["compliance"] = compliance
        ev["score"] = score
        save_evidence(f"run_{modo}.json", json.dumps(ev, indent=2, ensure_ascii=False))
        save_evidence(f"run_{modo}.txt", texto)

        salida[modo] = {"response": texto, "compliance": compliance, "score": score}
        print(f"[harness] {modo}: {score} reglas cumplidas ({elapsed}s)")

    return salida

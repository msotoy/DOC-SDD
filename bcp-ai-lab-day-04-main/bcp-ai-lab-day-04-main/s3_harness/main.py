"""Punto de entrada — S3 Harness | Code Refactoring Pipeline

El flujo clona un repo GitHub real, analiza su código con IA y produce
un PR de refactorización con mejoras concretas y accionables.

Agentes:
  0. analyze     — Lee el código y detecta problemas de calidad
  1. chapter     — Chapter Lead: define el plan de refactorización
  2. backend_dev — Implementa cambios en el backend
  3. frontend_dev— Implementa cambios en el frontend / API
  4. reviewer    — Tech Lead: revisa y emite veredicto

Uso:
    cp .env.example .env   # configurar GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN
    python main.py

Variables de entorno clave:
    GITHUB_OWNER      Org o usuario de GitHub (ej: NTTData-Academy)
    GITHUB_REPO       Repo a analizar y refactorizar
    GITHUB_TOKEN      Token para repos privados (opcional)
    GIT_HEAD_BRANCH   Rama del PR (ej: feature/equipo-01/refactor)
    GIT_BASE_BRANCH   Rama base (default: main)
    GIT_MCP_URL       URL del servidor MCP Git

Salida en output/:
    output/analysis.md        — Hallazgos de calidad de código
    output/chapter_plan.md    — Plan del Chapter Lead
    output/backend_refactor.md
    output/frontend_refactor.md
    output/reviewer_report.md
    output/<archivos refactorizados en su ruta original>
"""
import json
import os
import re
import subprocess
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env ANTES de importar MCPs y LLM
load_dotenv(override=True)

import mcp_git
from mcp_git import list_tools as git_tools, create_pr

# El pipeline de agentes vive en el graph; el harness es su única puerta de
# entrada. main.py no instancia modelos ni arma prompts.
from harness.harness import (
    run_with_harness,
    resume_with_harness,
    next_node,
    step,
    retry_node,
    check_security_compliance,
    state as harness_state,
)

# ── Configuración ────────────────────────────────────────────────────
_MCP_VERBOSE = os.getenv("MCP_VERBOSE", "false").lower() == "true"
mcp_git.set_verbose(_MCP_VERBOSE)

GITHUB_OWNER = os.getenv("GITHUB_OWNER", "NTTData-Academy")
GITHUB_REPO  = os.getenv("GITHUB_REPO",  "workshop-requirements-api-template")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HEAD_BRANCH  = os.getenv("GIT_HEAD_BRANCH", "feature/equipo-01/workshop-refactor")
BASE_BRANCH  = os.getenv("GIT_BASE_BRANCH", "main")
_ISSUE       = os.getenv("GITHUB_ISSUE", "").strip()  # issue del Project ReqFlow en alcance

OUTPUT_DIR      = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
REPOS_DIR       = Path(__file__).parent / "_repos"
REPOS_DIR.mkdir(exist_ok=True)
CHECKPOINT_FILE = OUTPUT_DIR / ".checkpoint.json"

# Identificador de la sesión del graph. El estado vive en el MemorySaver
# del harness indexado por este thread_id.
THREAD_ID = "s3-refactor-01"


# ── Utilidades ────────────────────────────────────────────────────────

def _clone_or_pull(repo_name: str) -> Path:
    """Clona o actualiza el repo en _repos/<repo_name>."""
    token = GITHUB_TOKEN
    url   = (f"https://{token}@github.com/{GITHUB_OWNER}/{repo_name}.git"
             if token else f"https://github.com/{GITHUB_OWNER}/{repo_name}.git")
    clone_dir = REPOS_DIR / repo_name
    if clone_dir.exists():
        print(f"  [GIT] Actualizando {repo_name}...")
        subprocess.run(["git", "-C", str(clone_dir), "pull", "--quiet"],
                       capture_output=True)
    else:
        print(f"  [GIT] Clonando {repo_name}...")
        r = subprocess.run(["git", "clone", "--depth=1", "--quiet", url, str(clone_dir)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ⚠️  Clone error: {r.stderr[:300]}")
    return clone_dir


def _read_snapshot(repo_dir: Path,
                   extensions=(".java", ".ts", ".html", ".py",
                                ".properties", ".sql", ".xml",
                                ".json", ".yml", ".yaml"),
                   max_files: int = 50,
                   max_lines: int = 250) -> str:
    """Lee un snapshot del código del repo (los primeros max_lines por archivo)."""
    parts, count = [], 0
    for ext in extensions:
        for f in sorted(repo_dir.rglob(f"*{ext}")):
            if any(p in str(f) for p in [
                "node_modules", ".git", "target", "__pycache__",
                ".mvn", "dist", "build", ".angular"
            ]):
                continue
            if count >= max_files:
                break
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                snippet = "\n".join(content.splitlines()[:max_lines])
                rel     = f.relative_to(repo_dir).as_posix()
                parts.append(f"\n### {rel}\n```\n{snippet}\n```")
                count += 1
            except Exception:
                pass
    return "\n".join(parts) or "(repositorio vacío o sin archivos con esas extensiones)"


def _detect_project_type(repo_dir: Path) -> str:
    """
    Detecta si el proyecto es 'backend', 'frontend' o 'ambos'
    inspeccionando los archivos presentes en el repo.
    Retorna: 'backend' | 'frontend' | 'ambos'
    """
    backend_markers  = {".java", ".py", ".kt", ".go", ".cs", ".rb"}
    backend_files    = {"pom.xml", "build.gradle", "requirements.txt",
                        "application.properties", "application.yml", "Dockerfile"}
    frontend_markers = {".ts", ".tsx", ".jsx", ".vue", ".svelte"}
    frontend_files   = {"package.json", "angular.json", "vite.config.ts",
                        "vite.config.js", "next.config.js", "nuxt.config.ts"}

    has_backend  = False
    has_frontend = False

    for f in repo_dir.rglob("*"):
        if any(p in str(f) for p in ["node_modules", ".git", "target",
                                      "__pycache__", "dist", "build"]):
            continue
        name = f.name
        ext  = f.suffix.lower()
        if ext in backend_markers or name in backend_files:
            has_backend = True
        if ext in frontend_markers or name in frontend_files:
            has_frontend = True
        if has_backend and has_frontend:
            break

    if has_backend and has_frontend:
        return "ambos"
    if has_frontend:
        return "frontend"
    return "backend"


def _extract_files(text: str) -> int:
    """
    Extrae bloques con cabecera ### path/archivo.ext seguidos de un bloque ```
    y los guarda en output/ respetando la ruta relativa.
    """
    pattern = re.compile(
        r"###\s*(?:Archivo[:\s]+)?`?([^\n`]+\.\w+)`?\s*\n```[\w]*\n([\s\S]*?)```",
        re.MULTILINE,
    )
    saved, seen = 0, set()
    for m in pattern.finditer(text):
        rel  = m.group(1).strip().lstrip("/")
        code = m.group(2).rstrip()
        if rel in seen:
            continue
        seen.add(rel)
        dest = OUTPUT_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(code, encoding="utf-8")
        print(f"  💾 output/{rel}")
        saved += 1
    return saved


def save_checkpoint(state: dict, next_step: str) -> None:
    """Persiste el estado actual del pipeline en .checkpoint.json."""
    data = {
        "project_type":  state.get("project_type", ""),
        "analysis":      state.get("analysis", ""),
        "plan":          state.get("plan", ""),
        "backend_out":   state.get("backend_out", ""),
        "frontend_out":  state.get("frontend_out", ""),
        "head_branch":   state.get("head_branch", ""),
        "base_branch":   state.get("base_branch", ""),
        "commit_type":   state.get("commit_type", ""),
        "commit_msg":    state.get("commit_msg", ""),
        "next_step":     next_step,
    }
    CHECKPOINT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  💾 Checkpoint guardado (next_step={next_step})")


def load_checkpoint() -> dict | None:
    """Carga el checkpoint si existe y es válido."""
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def clear_checkpoint() -> None:
    """Elimina el checkpoint al terminar el pipeline."""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        print("  🗑️  Checkpoint eliminado.")


def _derive_commit_type(plan: str, review_out: str) -> str:
    """
    Infiere el tipo de commit convencional (feat/fix/refactor/chore)
    según el contenido del plan y el veredicto del reviewer.
    Ver: https://www.conventionalcommits.org/en/v1.0.0/
    """
    text = (plan + " " + review_out).lower()
    if any(w in text for w in (
        "nueva funcionalidad", "new feature", "agregar funcionalidad",
        "add feature", "implement new", "nueva capacidad",
    )):
        return "feat"
    if any(w in text for w in (
        "bug", "error crítico", "vulnerabilidad", "security issue",
        "corrección", "broken", "crash", "null pointer", "npe",
        "fix", "hotfix",
    )):
        return "fix"
    if any(w in text for w in (
        "dependencia", "dependency", "upgrade", "update version",
        "package", "build", "ci", "pipeline", "docker", "config",
        "version bump", "chore",
    )):
        return "chore"
    # Default para mejoras de calidad / reestructuración
    return "refactor"


def _branch_name(repo_name: str, commit_type: str, plan: str) -> str:
    """
    Genera un nombre de rama semántico.
    Formato: <type>/<repo-slug>/<short-description>
    Ej: refactor/workshop-requirements-api/code-quality-20240830
    """
    import datetime
    repo_slug = re.sub(r"[^\w-]", "-", repo_name.lower()).strip("-")[:30]
    # Intentar extraer un descriptor corto del plan (primer título ## o primera línea)
    desc_match = re.search(r"##\s+(.+)", plan)
    if desc_match:
        raw_desc = desc_match.group(1).strip()
    else:
        raw_desc = "code-quality"
    desc = re.sub(r"[^\w\s-]", "", raw_desc.lower())
    desc = re.sub(r"\s+", "-", desc.strip())[:30].strip("-")
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    return f"{commit_type}/{repo_slug}/{desc}-{date_str}"


def _commit_message(commit_type: str, repo_name: str, analysis: str) -> str:
    """
    Genera el mensaje de commit siguiendo Conventional Commits.
    Formato: <type>(<scope>): <description>
    """
    scope = re.sub(r"[^\w-]", "-", repo_name.lower()).strip("-")[:25]
    # Extraer un resumen de los hallazgos principales del análisis
    first_line = next(
        (ln.strip().lstrip("- ").lstrip("* ") for ln in analysis.splitlines()
         if ln.strip() and not ln.strip().startswith("#")),
        "code quality improvements"
    )
    # Limpiar y truncar
    desc = re.sub(r"\*\*[^*]+\*\*:?\s*", "", first_line)  # quitar bold
    desc = re.sub(r"\s+", " ", desc).strip()[:72]
    desc = desc[0].lower() + desc[1:] if desc else "code quality improvements"
    return f"{commit_type}({scope}): {desc}"


def _copy_files_to_repo(output_dir: Path, repo_dir: Path) -> int:
    """
    Copia los archivos refactorizados de output/ al repo clonado,
    respetando la ruta relativa. Omite los artefactos de reporte del pipeline.
    """
    _PIPELINE_FILES = {
        "analysis.md", "chapter_plan.md", "backend_refactor.md",
        "frontend_refactor.md", "reviewer_report.md", ".checkpoint.json",
    }
    copied = 0
    for f in sorted(output_dir.rglob("*")):
        if not f.is_file() or f.name in _PIPELINE_FILES:
            continue
        rel  = f.relative_to(output_dir)
        dest = repo_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(f.read_bytes())
        print(f"  📁 {rel}")
        copied += 1
    return copied


def _git_branch_push(repo_dir: Path, branch: str, commit_msg: str) -> str:
    """
    En el repo local clonado:
      1. Configura user/email de git
      2. Crea y cambia a la nueva rama
      3. Agrega todos los cambios al staging
      4. Hace el commit con mensaje convencional
      5. Hace push al remote (origin)
    Retorna el nombre de rama pusheado.
    """
    token = GITHUB_TOKEN
    if token:
        remote_url = (f"https://{token}@github.com/{GITHUB_OWNER}/{GITHUB_REPO}.git")
        subprocess.run(
            ["git", "-C", str(repo_dir), "remote", "set-url", "origin", remote_url],
            capture_output=True,
        )

    setup_cmds = [
        ["git", "-C", str(repo_dir), "config", "user.email", "refactor-pipeline@nttdata.com"],
        ["git", "-C", str(repo_dir), "config", "user.name",  "Refactoring Pipeline (AI)"],
    ]
    for cmd in setup_cmds:
        subprocess.run(cmd, capture_output=True)

    # Crear rama
    r = subprocess.run(
        ["git", "-C", str(repo_dir), "checkout", "-b", branch],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        # Si ya existe, reutilizarla
        subprocess.run(
            ["git", "-C", str(repo_dir), "checkout", branch],
            capture_output=True,
        )
        print(f"  ℹ️  Rama '{branch}' ya existía — reutilizando.")
    else:
        print(f"  ✅ Rama creada: {branch}")

    # Stage + commit
    subprocess.run(["git", "-C", str(repo_dir), "add", "-A"], capture_output=True)
    r = subprocess.run(
        ["git", "-C", str(repo_dir), "commit", "-m", commit_msg],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        stderr = r.stderr.strip()
        if "nothing to commit" in stderr:
            print("  ℹ️  Sin cambios para commitear.")
        else:
            print(f"  ⚠️  git commit: {stderr[:300]}")
    else:
        print(f"  ✅ Commit: {commit_msg}")

    # Push
    r = subprocess.run(
        ["git", "-C", str(repo_dir), "push", "--set-upstream", "origin", branch],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  ⚠️  git push: {r.stderr.strip()[:400]}")
    else:
        print(f"  ✅ Push → origin/{branch}")

    return branch


OUTPUT_FILES = {
    "analyze":  ("analysis.md",           "Análisis de Código"),
    "chapter":  ("chapter_plan.md",       "Plan de Refactorización"),
    "backend":  ("backend_refactor.md",   "Refactorización Backend"),
    "frontend": ("frontend_refactor.md",  "Refactorización Frontend / API"),
    "reviewer": ("reviewer_report.md",    "Reporte del Reviewer"),
}

NODE_LABELS = {
    "analyze":  "Análisis de código",
    "chapter":  "Chapter Lead (Plan)",
    "backend":  "Backend Developer",
    "frontend": "Frontend / API Developer",
    "reviewer": "Tech Lead Reviewer",
}

STATE_FIELDS = {
    "analyze":  "out_analysis",
    "chapter":  "out_plan",
    "backend":  "out_backend",
    "frontend": "out_frontend",
    "reviewer": "out_reviewer",
}


def _hitl_node(nodo: str, estado: dict) -> str:
    """
    Human-in-the-Loop sobre un nodo ya ejecutado por el graph.

    El nodo corrió una vez (vía harness.step). Aquí mostramos su salida y
    pedimos [s/r/n]; con [r] el harness lo reejecuta y reinyecta el
    resultado en el estado con update_state(as_node=...).

    Ojo: esto NO decide si hay otra ronda de review. Eso lo resuelve la
    arista condicional should_retry() según el veredicto.
    """
    label  = NODE_LABELS.get(nodo, nodo)
    campo  = STATE_FIELDS[nodo]
    while True:
        salida = estado.get(campo, "") or ""
        if not salida:
            print(f"  ⏩ {label}: sin salida (nodo omitido por project_type).")
            return ""

        print(f"\n{'─'*60}")
        print(f"[OUTPUT] {label}:")
        print(salida[:1200] + ("..." if len(salida) > 1200 else ""))
        print(f"\n[Output completo: {len(salida)} caracteres]")

        choice = input(
            "\n¿Qué haces? [s=guardar / r=reintentar / n=cancelar]: "
        ).strip().lower()
        if choice == "s":
            return salida
        elif choice == "r":
            print(f"\n[RETRY] Reejecutando {label}...")
            estado = retry_node(THREAD_ID, nodo)
        elif choice == "n":
            print(f"\n[CANCELADO] en paso '{label}'.")
            raise SystemExit(0)
        else:
            print("  ✗ Opción inválida. Ingresa s, r o n.")


# ── Flujo principal ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("S3 Harness — Code Refactoring Pipeline")
    print(f"Repo: {GITHUB_OWNER}/{GITHUB_REPO}")
    print(f"Branch: {HEAD_BRANCH} → {BASE_BRANCH}")
    print("=" * 60 + "\n")

    # ── Inicializar MCP Git ───────────────────────────────────────────
    print("[MCP Git] Conectando...")
    git_tools()
    print("[MCP Git] Herramientas disponibles.\n")

    # La constitución la carga el harness al sembrar el estado (más abajo,
    # en run_with_harness). Aquí ya no se lee nada: main.py no arma contexto.

    # ── Paso 0: Clonar / actualizar el repo ──────────────────────────
    print(f"[REPO] Descargando {GITHUB_OWNER}/{GITHUB_REPO}...")
    repo_dir = _clone_or_pull(GITHUB_REPO)
    snapshot = _read_snapshot(repo_dir)
    file_count = snapshot.count("###")
    print(f"[REPO] Snapshot generado: {file_count} archivos leídos.\n")

    if not snapshot or snapshot == "(repositorio vacío o sin archivos con esas extensiones)":
        print("✗ No se pudo leer el código del repo. Verifica GITHUB_REPO y GITHUB_TOKEN.")
        raise SystemExit(1)

    # ── Detectar tipo de proyecto y confirmar con el usuario ──────────
    detected = _detect_project_type(repo_dir)
    print(f"[DETECCIÓN] Tipo de proyecto detectado: {detected.upper()}")
    print("  (basado en extensiones y archivos de configuración encontrados)\n")

    _tipo_input = input(
        f"¿Tipo de proyecto? [backend / frontend / ambos] (Enter = {detected}): "
    ).strip().lower()
    project_type = _tipo_input if _tipo_input in ("backend", "frontend", "ambos") else detected
    print(f"  → Usando: {project_type.upper()}\n")

    run_backend  = project_type in ("backend",  "ambos")
    run_frontend = project_type in ("frontend", "ambos")

    # Calcular total de pasos según tipo
    _steps = 2 + int(run_backend) + int(run_frontend) + 1  # analyze + chapter + devs + reviewer
    _step  = [0]

    def _step_label() -> str:
        _step[0] += 1
        return f"[PASO {_step[0]}/{_steps}]"

    # ── Checkpoint: intentar retomar sesión anterior ──────────────────
    _ckpt = load_checkpoint()
    _resume = False
    if _ckpt:
        _ckpt_step = _ckpt.get("next_step", "")
        _ckpt_type = _ckpt.get("project_type", "")
        print(f"[CHECKPOINT] Sesión anterior encontrada.")
        print(f"  Tipo: {_ckpt_type.upper()} | Siguiente paso: {_ckpt_step}")
        _resume_input = input("¿Retomar desde el checkpoint? [s/N]: ").strip().lower()
        if _resume_input == "s":
            _resume      = True
            project_type = _ckpt_type or project_type
            run_backend  = project_type in ("backend",  "ambos")
            run_frontend = project_type in ("frontend", "ambos")
            print(f"  → Retomando en: {_ckpt_step}\n")
        else:
            clear_checkpoint()
            _ckpt = None

    if not _resume:
        _confirm = input("¿Iniciar pipeline de refactorización? [s/N]: ").strip().lower()
        if _confirm != "s":
            print("Cancelado.")
            raise SystemExit(0)

    # Estado compartido del pipeline
    _state: dict = {
        "project_type": project_type,
        "analysis":     _ckpt.get("analysis",    "") if _ckpt else "",
        "plan":         _ckpt.get("plan",         "") if _ckpt else "",
        "backend_out":  _ckpt.get("backend_out",  "") if _ckpt else "",
        "frontend_out": _ckpt.get("frontend_out", "") if _ckpt else "",
        "head_branch":  _ckpt.get("head_branch",  "") if _ckpt else "",
        "base_branch":  _ckpt.get("base_branch",  "") if _ckpt else "",
        "commit_type":  _ckpt.get("commit_type",  "") if _ckpt else "",
        "commit_msg":   _ckpt.get("commit_msg",   "") if _ckpt else "",
    }
    _next_step = (_ckpt.get("next_step", "analysis") if _ckpt else "analysis")

    # ── Arrancar el pipeline en el graph, vía harness ─────────────────
    # El harness carga instructions + constitution + policies UNA vez y los
    # deja en state["context"]. No ejecuta ningún nodo todavía.
    _repo_full = f"{GITHUB_OWNER}/{GITHUB_REPO}"

    if _resume:
        # El MemorySaver del graph es en-proceso: se perdió al reiniciar.
        # Resembramos y adelantamos con los artefactos del checkpoint, sin
        # reejecutar ningún nodo ya aprobado.
        resume_with_harness(
            repo_name=_repo_full,
            snapshot=snapshot,
            project_type=project_type,
            thread_id=THREAD_ID,
            outputs={
                "out_analysis": _state["analysis"],
                "out_plan":     _state["plan"],
                "out_backend":  _state["backend_out"],
                "out_frontend": _state["frontend_out"],
                "out_reviewer": _state.get("reviewer_out", ""),
            },
            repo_dir=repo_dir,
        )
        _pendiente = next_node(THREAD_ID)
        print(f"  → Retomando en: {NODE_LABELS.get(_pendiente, _pendiente or 'fin')}\n")
    else:
        run_with_harness(
            repo_name=_repo_full,
            snapshot=snapshot,
            project_type=project_type,
            thread_id=THREAD_ID,
            repo_dir=repo_dir,
        )

    # ── Bucle HITL: un nodo por vuelta ────────────────────────────────
    # step() ejecuta exactamente un nodo gracias a interrupt_before.
    # El retry automático del reviewer lo resuelve should_retry() dentro
    # del graph: aquí el humano sólo confirma el resultado de cada ronda.
    _rondas = {}
    while next_node(THREAD_ID) is not None:
        _nodo = next_node(THREAD_ID)
        _rondas[_nodo] = _rondas.get(_nodo, 0) + 1
        _sufijo = f" (ronda {_rondas[_nodo]})" if _rondas[_nodo] > 1 else ""

        print(f"\n{_step_label()} {NODE_LABELS.get(_nodo, _nodo)}{_sufijo}...")
        _nodo_corrido, _estado = step(THREAD_ID)

        _salida = _hitl_node(_nodo_corrido, _estado)
        if not _salida:
            continue                      # nodo omitido por project_type

        # Persistir el artefacto del nodo
        _fname, _titulo = OUTPUT_FILES[_nodo_corrido]
        _stem = Path(_fname).stem
        if _rondas[_nodo_corrido] > 1:    # rondas extra no pisan la primera
            _fname = f"{_stem}_r{_rondas[_nodo_corrido]}.md"
        (OUTPUT_DIR / _fname).write_text(
            f"# {_titulo} — {GITHUB_REPO}\n\n{_salida}", encoding="utf-8"
        )

        if _nodo_corrido in ("backend", "frontend"):
            _n = _extract_files(_salida)
            print(f"  ✅ output/{_fname} ({_n} archivos extraídos)")
        else:
            print(f"  ✅ output/{_fname}")

        _state[{"analyze": "analysis", "chapter": "plan",
                "backend": "backend_out", "frontend": "frontend_out",
                "reviewer": "reviewer_out"}[_nodo_corrido]] = _salida
        save_checkpoint(_state, _nodo_corrido)

    # ── Recuperar los outputs finales del estado del graph ────────────
    _final       = harness_state(THREAD_ID)
    analysis     = _final.get("out_analysis", "")
    plan         = _final.get("out_plan", "")
    backend_out  = _final.get("out_backend", "")
    frontend_out = _final.get("out_frontend", "")
    review_out   = _final.get("out_reviewer", "")

    print(f"\n[GRAPH] Pipeline completado. "
          f"Veredicto: {'APROBADO' if _final.get('approved') else 'con observaciones'} "
          f"tras {_final.get('retry_count', 0)} ronda(s) de backend.")

    # ── Compliance con la constitución ────────────────────────────────
    if _final.get("context"):
        print("\n[HARNESS] Verificando compliance con la constitución...")
        _combined   = " ".join([backend_out, frontend_out, review_out])
        _compliance = check_security_compliance(_combined)
        _passed = sum(1 for v in _compliance.values() if v)
        _total  = len(_compliance)
        print(f"[HARNESS] Score: {_passed}/{_total}")
        for rule, ok in _compliance.items():
            print(f"  {'✅' if ok else '❌'} {rule}")

        _evidence_dir = Path(__file__).parent / "evidence"
        _evidence_dir.mkdir(exist_ok=True)
        (_evidence_dir / "compliance_report.json").write_text(
            json.dumps(
                {"repo": GITHUB_REPO, "score": f"{_passed}/{_total}",
                 "compliance": _compliance},
                indent=2, ensure_ascii=False
            ),
            encoding="utf-8"
        )
        print("  ✅ evidence/compliance_report.json")
        _state["compliance_score"]  = f"{_passed}/{_total}"
        _state["compliance_detail"] = _compliance

    save_checkpoint(_state, "push")
    _next_step = "push"

    # ── Git local: branch + commit semántico + push ───────────────────
    if _next_step == "push":
        _push = input("\n¿Subir código y crear PR? [s/N]: ").strip().lower()
        if _push != "s":
            clear_checkpoint()
            print("Pipeline completado localmente. Sin push.")
            raise SystemExit(0)

        # 1. Determinar tipo de commit (feat/fix/refactor/chore)
        _commit_type = _derive_commit_type(plan, review_out)
        _base        = BASE_BRANCH

        # 2. Nombre de rama semántico
        _head = _branch_name(GITHUB_REPO, _commit_type, plan)

        # 3. Mensaje de commit convencional
        _msg = _commit_message(_commit_type, GITHUB_REPO, analysis)

        print(f"\n[GIT] Tipo de commit detectado : {_commit_type}")
        print(f"[GIT] Rama                      : {_head}")
        print(f"[GIT] Mensaje                   : {_msg}")

        # 4. Copiar archivos refactorizados al repo local
        print("\n[GIT] Copiando archivos refactorizados al repo local...")
        n_copied = _copy_files_to_repo(OUTPUT_DIR, repo_dir)
        print(f"  {n_copied} archivo(s) copiado(s).")

        # 5. Branch + commit + push desde el repo clonado
        print("\n[GIT] Commiteando y pusheando...")
        _head = _git_branch_push(repo_dir, _head, _msg)

        # Guardar checkpoint DESPUÉS del push (antes del PR)
        _state.update({
            "head_branch": _head,
            "base_branch": _base,
            "commit_type": _commit_type,
            "commit_msg":  _msg,
        })
        save_checkpoint(_state, "pr")
        _next_step = "pr"

    elif _next_step == "pr":
        # Retomar: el push ya fue hecho, solo falta el PR
        _head        = _state.get("head_branch", "")
        _base        = _state.get("base_branch", BASE_BRANCH)
        _commit_type = _state.get("commit_type", "refactor")
        _msg         = _state.get("commit_msg",  "")
        print(f"\n  ⏩ Push ya realizado — retomando PR desde checkpoint.")
        print(f"     Rama: {_head}")

    # 6. MCP Git: crear PR usando la rama pusheada
    print("\n[MCP Git] Creando Pull Request...")
    # Sección de compliance para el PR (si se usó constitución)
    _compliance_section = ""
    if _state.get("compliance_score"):
        _detail = _state.get("compliance_detail", {})
        _rows   = "\n".join(
            f"| `{rule}` | {'✅ PASS' if ok else '❌ FAIL'} |"
            for rule, ok in _detail.items()
        )
        _compliance_section = (
            f"\n## ⚖️ Compliance con Constitución — Score {_state['compliance_score']}\n\n"
            "| Regla | Estado |\n"
            "|-------|--------|\n"
            f"{_rows}\n\n"
            "> Verificado por `_check_compliance()` integrado en el harness.\n"
        )

    _pr_body = (
        f"## Code Refactoring Pipeline — `{GITHUB_OWNER}/{GITHUB_REPO}`\n\n"
        f"**Tipo:** `{_commit_type}` | **Rama:** `{_head}` → `{_base}`\n\n"
        "## Veredicto del Tech Lead Reviewer\n\n"
        f"```\n{review_out[:800]}\n```\n\n"
        "## Plan del Chapter Lead\n\n"
        f"```\n{plan[:800]}\n```\n\n"
        f"{_compliance_section}"
        + (f"Closes #{_ISSUE}\n\n" if _ISSUE else "")
        + "## Artefactos del pipeline\n\n"
        "| Archivo | Descripción |\n"
        "|---------|-------------|\n"
        "| `output/analysis.md` | Hallazgos de calidad de código |\n"
        "| `output/chapter_plan.md` | Plan de refactorización |\n"
        "| `output/backend_refactor.md` | Cambios de backend |\n"
        "| `output/frontend_refactor.md` | Cambios de frontend/API |\n"
        "| `output/reviewer_report.md` | Veredicto del Tech Lead |\n"
        "| `evidence/compliance_report.json` | Score de compliance constitución |\n"
    )

    pr_url = create_pr(
        title=f"{_commit_type}({GITHUB_REPO}): refactoring pipeline — AI-generated",
        body=_pr_body,
        head=_head,
        base=_base,
    )
    print(f"\n[MCP Git] ✅ PR creado: {pr_url}")
    clear_checkpoint()

    print("\n" + "=" * 60)
    print("✅ S3 Harness completado.")
    print(f"  Rama    : {_head}")
    print(f"  Commit  : {_msg}")
    print(f"  Outputs : output/")
    print(f"  PR      : {pr_url}")
    print("=" * 60)

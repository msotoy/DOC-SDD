"""
Cliente HTTP para el MCP de proyectos — mcp-project :8080
Lee issues y features desde GitHub Projects via MCP Streamable HTTP.

Variables de entorno:
    PROJECTS_MCP_URL / MCP_PROJECT_URL   URL base (default: http://localhost:8080)
    MCP_TIMEOUT                          Timeout en segundos (default: 30)
    GITHUB_OWNER                         Owner de GitHub (org o usuario)
    GITHUB_REPO                          Repo por defecto
"""
import os
import re
import fnmatch
import json
import subprocess
import threading
from pathlib import Path
import requests

_URL     = os.getenv("PROJECTS_MCP_URL",     "http://localhost:8081")
_KEY     = os.getenv("PROJECTS_MCP_API_KEY", "")

_rpc_id       = 0
_id_lock      = threading.Lock()
_session_id   = None
_initialized  = False
_init_lock    = threading.Lock()

_VERBOSE = False


def set_verbose(flag: bool) -> None:
    global _VERBOSE
    _VERBOSE = flag


def _next_id() -> int:
    global _rpc_id
    with _id_lock:
        _rpc_id += 1
        return _rpc_id


def _headers() -> dict:
    hdrs = {
        "Authorization": f"Bearer {_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json, text/event-stream",
    }
    if _session_id:
        hdrs["Mcp-Session-Id"] = _session_id
    return hdrs


def _parse_sse_body(resp, msg_id) -> dict:
    """Lee un stream SSE de la respuesta del POST y retorna el JSON-RPC que
    coincide con msg_id (o el primero, si msg_id es None — notificaciones)."""
    data_buf = []
    for raw in resp.iter_lines(decode_unicode=True):
        if raw is None:
            continue
        if raw.startswith("data:"):
            data_buf.append(raw[5:].strip())
        elif raw == "":
            if not data_buf:
                continue
            payload_str = "\n".join(data_buf)
            data_buf     = []
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict) and (msg_id is None or payload.get("id") == msg_id):
                return payload
    raise RuntimeError("[MCP Proyectos] Stream SSE cerrado sin respuesta")


def _post_mcp(payload: dict, timeout: int) -> tuple[dict, str | None]:
    resp = requests.post(
        f"{_URL}/mcp",
        headers=_headers(),
        json=payload,
        stream=True,
        timeout=timeout,
    )
    resp.raise_for_status()
    sid   = resp.headers.get("Mcp-Session-Id")
    ctype = resp.headers.get("Content-Type", "")

    if "text/event-stream" in ctype:
        result = _parse_sse_body(resp, payload.get("id"))
    elif resp.content:
        result = resp.json()
    else:
        result = {}
    return result, sid


def _ensure_session(timeout: int = 20) -> None:
    """Handshake MCP: initialize → notifications/initialized (una sola vez)."""
    global _session_id, _initialized
    with _init_lock:
        if _initialized:
            return

        init_payload = {
            "jsonrpc": "2.0",
            "id":      _next_id(),
            "method":  "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities":    {},
                "clientInfo":      {"name": "s1-crewai", "version": "1.0.0"},
            },
        }
        result, sid = _post_mcp(init_payload, timeout)
        if "error" in result:
            raise RuntimeError(f"[MCP Proyectos] Error en initialize: {result['error']}")
        if sid:
            _session_id = sid

        try:
            _post_mcp(
                {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                timeout,
            )
        except Exception:
            pass

        _initialized = True


def _sse_call(method: str, params: dict, timeout: int = 20) -> dict:
    """Envía un JSON-RPC 2.0 vía Streamable HTTP y retorna el resultado."""
    _ensure_session(timeout)

    msg_id  = _next_id()
    payload = {
        "jsonrpc": "2.0",
        "id":      msg_id,
        "method":  method,
        "params":  params,
    }

    try:
        result, sid = _post_mcp(payload, timeout)
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"[MCP Proyectos] Error de conexión: {exc}") from exc

    if sid:
        global _session_id
        _session_id = sid

    if "error" in result:
        raise RuntimeError(f"[MCP Proyectos] Error RPC: {result['error']}")
    if _VERBOSE:
        keys = sorted(result.keys()) if isinstance(result, dict) else type(result).__name__
        print(f"[MCP Proyectos] {method} -> {keys}")
    return result.get("result", {})


# ── API pública ────────────────────────────────────────────────────────────────

def list_tools() -> list[dict]:
    """Descubre las herramientas disponibles en el MCP de proyectos.

    Llama a tools/list vía Streamable HTTP y retorna la lista de herramientas:
        [{"name": "get_issue", "description": "...", "inputSchema": {...}}, ...]
    """
    result = _sse_call("tools/list", {})
    return result.get("tools", [])


def call_tool(tool: str, params: dict) -> dict:
    """Llama una herramienta del MCP de proyectos por nombre.

    Usa tools/call vía Streamable HTTP. El agente debe llamar list_tools()
    primero para conocer qué herramientas están disponibles.

    Importante: el protocolo MCP reporta los errores de ejecución de una tool
    como {"content": [...], "isError": true} DENTRO de un resultado JSON-RPC
    exitoso — no como el campo "error" de JSON-RPC. Si no se revisa "isError"
    aquí, un fallo de la tool (p.ej. parámetros inválidos) se interpreta
    silenciosamente como una respuesta vacía/válida.
    """
    result = _sse_call("tools/call", {"name": tool, "arguments": params})
    content = result.get("content", [])
    text = content[0]["text"] if content and content[0].get("type") == "text" else None

    if result.get("isError"):
        raise RuntimeError(f"[MCP Proyectos] Tool '{tool}' falló: {text or result}")

    if text is not None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}
    return result


def discover_tool_schema(group: str, action: str | None = None) -> dict:
    """Introspecciona en runtime el esquema real de una tool vía discover_tools.

    Evita adivinar nombres de parámetros que pueden diferir entre versiones
    del server MCP (p.ej. `filterQuery` vs `filter`).
    """
    params = {"group": group, "includeSchemas": True}
    if action:
        params["action"] = action
    return call_tool("discover_tools", params)


_OWNER = os.getenv("GITHUB_OWNER", "")
_REPO  = os.getenv("GITHUB_REPO",  "")


def _extract_acceptance_criteria(body: str) -> list[str]:
    """Extrae criterios de aceptación del body markdown de un Issue.

    Prioriza checkboxes (- [ ] / - [x]); si no hay, busca viñetas bajo un
    encabezado que mencione "criterios de aceptación" / "acceptance criteria".
    """
    if not body:
        return []

    checkboxes = re.findall(r"^\s*-\s*\[[ xX]\]\s*(.+)$", body, re.MULTILINE)
    if checkboxes:
        return [c.strip() for c in checkboxes]

    lines   = body.splitlines()
    grabbed = []
    in_section = False
    for line in lines:
        if re.search(r"criterios?\s+de\s+aceptaci[oó]n|acceptance\s+criteria", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if line.strip().startswith("#"):
                break
            m = re.match(r"\s*[-*]\s*(.+)", line)
            if m:
                grabbed.append(m.group(1).strip())
            elif line.strip() == "" and grabbed:
                break
    return grabbed


def get_feature(issue_number: int | str) -> dict:
    """Lee el feature brief desde el GitHub Issue vía MCP de proyectos.

    Helper sobre call_tool("manage_issues", {"action": "get", ...}).

    Retorna:
        {
            "title":               str,
            "description":         str,   # body del issue en markdown
            "acceptance_criteria": list[str],
        }
    """
    params = {"action": "get", "owner": _OWNER, "repo": _REPO}
    if isinstance(issue_number, str) and issue_number.startswith("I_"):
        params["issueId"] = issue_number
    else:
        params["issueNumber"] = issue_number
    result = call_tool("manage_issues", params)
    issue = result.get("issue", result) if isinstance(result, dict) else result
    body  = issue.get("body") or issue.get("description") or ""
    return {
        "title":               issue.get("title", ""),
        "description":         body,
        "acceptance_criteria": _extract_acceptance_criteria(body),
    }


def list_issues() -> list[dict]:
    """Lista todos los issues/features del proyecto GitHub vía MCP.

    Llama a manage_issues (action "list") y retorna la lista:
        [{"number": 42, "title": "...", "state": "open"}, ...]

    Si el MCP retorna un dict con clave "items" o "issues", extrae la lista.
    """
    result = call_tool("manage_issues", {
        "action": "list",
        "owner":  _OWNER,
        "repo":   _REPO,
        "state":  "all",
        "limit":  100,
    })
    if isinstance(result, list):
        raw = result
    else:
        raw = result.get("issues", result.get("items", []))

    return [
        {
            "number": it.get("number"),
            "title":  it.get("title", "(sin título)"),
            "state":  it.get("state", ""),
        }
        for it in raw
    ]


# ── GitHub Projects (v2) — proyecto asignado + backlog ──────────────────────

def list_projects() -> list[dict]:
    """Lista los GitHub Projects (v2) visibles para el MCP.

    Llama a manage_project (action "list") y normaliza la respuesta:
        [{"id": "PVT_...", "title": "...", "number": 1, "closed": False}, ...]
    """
    result = call_tool("manage_project", {"action": "list", "status": "all", "limit": 20})
    if isinstance(result, list):
        raw = result
    else:
        raw = result.get("projects", result.get("items", []))

    return [
        {
            "id":     p.get("id"),
            "title":  p.get("title", p.get("name", "(sin título)")),
            "number": p.get("number"),
            "closed": bool(p.get("closed", p.get("status") == "closed")),
        }
        for p in raw
    ]


def _normalize_project_item(it: dict) -> dict:
    """Normaliza un item de backlog de GitHub Projects a un formato uniforme.

    El shape exacto varía según el server MCP (list_items vs filter_items),
    así que se prueban varias claves posibles para cada campo.
    """
    content     = it.get("content") if isinstance(it.get("content"), dict) else {}
    field_values = it.get("fieldValues") if isinstance(it.get("fieldValues"), dict) else {}

    title = (
        it.get("title")
        or content.get("title")
        or field_values.get("Title")
        or "(sin título)"
    )
    number = (
        it.get("number")
        or it.get("issueNumber")
        or it.get("contentNumber")
        or content.get("number")
    )
    state = it.get("state") or content.get("state") or ""
    item_type = it.get("type") or it.get("contentType") or content.get("__typename") or "Issue"

    return {
        "id":         it.get("id"),
        "contentId":  it.get("contentId") or content.get("id"),
        "type":       item_type,
        "title":      title,
        "number":     number,
        "state":      state,
    }


def list_project_items(project_id: str, limit: int = 100) -> list[dict]:
    """Lista el backlog (items) de un GitHub Project (v2) — features/tareas.

    Prueba filter_items (más completo: título, estado, labels) con las dos
    formas de parámetro documentadas para "sin filtro" (`filter: {}` y
    `filterQuery: ""`), y si ambas fallan cae a list_items — que siempre
    acepta solo projectId/limit pero no devuelve título.

    Cada intento fallido levanta RuntimeError gracias a la detección de
    "isError" en call_tool(), así que el fallback SÍ se ejecuta cuando
    corresponde (antes se tragaba el error silenciosamente y devolvía backlog
    vacío aunque el proyecto tuviera items).

    Retorna: [{"id", "contentId", "type", "title", "number", "state"}, ...]
    """
    attempts = [
        {"action": "filter_items", "projectId": project_id, "filter": {}},
        {"action": "filter_items", "projectId": project_id, "filterQuery": ""},
        {"action": "list_items",   "projectId": project_id, "limit": limit},
    ]

    result   = None
    last_exc = None
    for params in attempts:
        try:
            result = call_tool("manage_project", params)
            break
        except RuntimeError as exc:
            last_exc = exc
            continue

    if result is None:
        raise RuntimeError(f"[MCP Proyectos] No se pudo listar items del proyecto: {last_exc}")

    if isinstance(result, list):
        raw = result
    else:
        # filter_items devuelve los items en structuredContent.items
        # list_items los devuelve directamente en items
        raw = (
            result.get("structuredContent", {}).get("items")
            or result.get("items")
            or []
        )

    return [_normalize_project_item(it) for it in raw]


def get_feature_from_item(item: dict) -> dict:
    """Resuelve el feature brief completo (título, body, criterios) a partir
    de un item de backlog de GitHub Projects.

    Usa contentId cuando el Project devuelve el ID de nodo del issue.
    Si no está disponible, conserva la resolución por número o título.
    """
    content_id = item.get("contentId") or item.get("content_id")
    if content_id and str(content_id).startswith("I_"):
        return get_feature(content_id)

    number = item.get("number")
    if number is None:
        for candidate in list_issues():
            if candidate.get("title") == item.get("title"):
                number = candidate.get("number")
                break

    if number is None:
        # El item de Projects v2 no tiene número de issue asociado
        # (puede ser un Draft Issue). Usamos los datos del propio item.
        title = item.get("title", "(sin título)")
        desc  = (
            item.get("description")
            or item.get("body")
            or f"Feature: {title}"
        )
        ac = item.get("acceptance_criteria", [])
        print(f"[MCP Proyectos] ⚠ Item sin número de issue — usando datos del proyecto directamente.")
        return {"title": title, "description": desc, "acceptance_criteria": ac}

    return get_feature(number)


# ── Alcance por stack: qué repos toca el cambio ──────────────────────
# El backlog vive en el Project (no necesariamente vinculado a un repo):
# el issue resuelve el alcance y cada agente corre sólo si su stack está
# involucrado. Designer y Reviewer siempre corren.

REPO_STACKS: dict[str, tuple[str, ...]] = {
    "workshop-auth-backend": ("backend",),
    "workshop-login-frontend": ("frontend",),
    "workshop-requirements-api": ("api",),
}
KNOWN_REPOS = tuple(REPO_STACKS)

STACK_KEYWORDS: dict[str, tuple[str, ...]] = {
    # Palabras que SÓLO existen en un stack (nada ambiguo como "token",
    # "jwt", "auth" o "login": viven en backend y frontend a la vez).
    "backend": ("quarkus", "endpoint", "microservicio", "controller",
                "repository", "jpa", "dto", ".java", " java ", "maven",
                "pom.xml", "datasource"),
    "frontend": ("angular", "frontend", "pantalla", "componente",
                 "interceptor", "guard", "css", "html", "typescript",
                 " ui ", " ux ", "sessionstorage", "localstorage",
                 "standalone"),
    "api": ("fastapi", "requirements-api", "python",
            "uvicorn", "pydantic", "pytest", "testclient"),
}

STACK_ORDER = ("backend", "frontend", "api")

# Negaciones que anulan una keyword ("sin endpoint", "no debe crearse").
_NEGATIONS = ("sin ", "no ", "ningún ", "ningun ", "tampoco ", "evitar ")


def _unnegated(text: str, kw: str) -> str | None:
    """Primera ocurrencia de kw no precedida por negación, o None."""
    start = 0
    while True:
        i = text.find(kw, start)
        if i < 0:
            return None
        window = text[max(0, i - 14):i]
        if not any(n in window for n in _NEGATIONS):
            return kw
        start = i + len(kw)


def _resolve_issue_repo(issue_number, owner: str, candidates) -> str | None:
    """Prueba en qué repo vive el issue (el item del Project no trae repo)."""
    for repo in candidates:
        try:
            call_tool("manage_issues", {"action": "get", "owner": owner, "repo": repo, "issueNumber": issue_number})
            return repo
        except Exception:
            # RuntimeError (tool falló / issue no está en este repo) o
            # error de conexión (servidor caído): probar el siguiente.
            continue
    return None


def infer_scope(item: dict, feature: dict, owner: str = "", repos: tuple = ()) -> dict:
    """Propone el alcance del cambio como stacks involucrados.

    Señal primaria: el repo donde vive el issue. Secundaria: palabras clave
    del título/body (pueden SUMAR stacks al alcance). Sin señales, alcance
    completo para no cambiar el comportamiento actual.

    Retorna {"stacks": [...], "reasons": [...], "repo": ...|None, "repos": [...]}.
    """
    stacks: list[str] = []
    reasons: list[str] = []
    found_repo = None

    number = item.get("number")
    if number is not None:
        eff_owner = owner or os.getenv("GITHUB_OWNER", "") or _OWNER
        cands = [r for r in (os.getenv("GITHUB_REPO", ""), _REPO, *(repos or KNOWN_REPOS)) if r]
        ordered: list[str] = []
        for r in cands:
            if r not in ordered:
                ordered.append(r)
        found_repo = _resolve_issue_repo(number, eff_owner, ordered)
        if found_repo and found_repo in REPO_STACKS:
            for s in REPO_STACKS[found_repo]:
                if s not in stacks:
                    stacks.append(s)
            reasons.append(f"issue #{number} vive en {found_repo}")

    text = f"{feature.get('title', '')} {feature.get('description', '')}".lower()
    for stack, kws in STACK_KEYWORDS.items():
        if stack in stacks:
            continue
        hit = None
        for k in kws:
            if _unnegated(text, k):
                hit = k
                break
        if hit:
            stacks.append(stack)
            reasons.append(f"palabra clave de {stack} ('{hit.strip()}') en título/body")

    if not stacks:
        stacks = ["backend", "frontend", "api"]
        reasons.append("sin señales: alcance completo (confirmar)")

    ordered_stacks = [s for s in STACK_ORDER if s in stacks]
    repos: list[str] = []
    for s in ordered_stacks:
        r = STACK_REPO.get(s)
        if r and r not in repos:
            repos.append(r)

    return {
        "stacks": ordered_stacks,
        "reasons": reasons,
        "repo": found_repo,
        "repos": repos,
    }


def format_scope(scope: dict) -> str:
    """Una línea legible del alcance para consola y logs."""
    stacks = ", ".join(scope.get("stacks", [])) or "ninguno"
    reasons = "; ".join(scope.get("reasons", [])) or "sin señales"
    return f"Alcance: {stacks} ({reasons})"


def resolve_project(project_id: str) -> dict:
    """Resuelve un Project genérico por node id (sin necesidad de vínculos).

    Usa manage_project (action "get") y normaliza al mismo shape de
    list_projects(). Levanta RuntimeError si el id no resuelve.
    """
    try:
        result = call_tool("manage_project", {"action": "get", "projectId": project_id})
    except Exception as exc:
        raise RuntimeError(f"[MCP Proyectos] El id '{project_id}' no resolvió a ningún proyecto: {exc}")
    if not isinstance(result, dict) or not result.get("id"):
        raise RuntimeError(f"[MCP Proyectos] El id '{project_id}' no resolvió a ningún proyecto.")
    return {
        "id": result.get("id"),
        "title": result.get("title", result.get("name", "(sin título)")),
        "number": result.get("number"),
        "closed": bool(result.get("closed", result.get("status") == "closed")),
    }


def list_owner_projects(owner: str = "") -> list[dict]:
    """Enumera los Projects del owner sin necesidad de vínculos.

    El `list` del servidor sólo trae proyectos vinculados al repo; para un
    Project genérico se enumeran por owner vía `gh` CLI (requisito del lab)
    y cada uno se resuelve por MCP (`get`), devolviendo el mismo shape de
    list_projects(). Si `gh` falla, retorna [].
    """
    eff_owner = owner or os.getenv("GITHUB_OWNER", "") or _OWNER
    if not eff_owner:
        return []
    try:
        out = subprocess.run(
            ["gh", "project", "list", "--owner", eff_owner,
             "--format", "json", "--jq", ".[].number"],
            capture_output=True, text=True, timeout=30, check=True,
        )
    except Exception:
        return []
    found: list[dict] = []
    for line in out.stdout.split():
        num = line.strip()
        if not num.isdigit():
            continue
        try:
            view = subprocess.run(
                ["gh", "project", "view", num, "--owner", eff_owner,
                 "--format", "json", "--jq", ".id"],
                capture_output=True, text=True, timeout=30, check=True,
            )
            pid = view.stdout.strip()
            if pid:
                found.append(resolve_project(pid))
        except Exception:
            continue
    return found


# ── Trabajo sobre repos reales (reqflow-workspace, rama local, sin push) ──
# S1/S2 no generan proyectos sintéticos: modifican los repos del workspace
# en una rama local `agent/<slug>`. Nada commitea ni pushea.

STACK_REPO: dict[str, str] = {
    "backend": "workshop-auth-backend",
    "frontend": "workshop-login-frontend",
    "api": "workshop-requirements-api",
}

# Archivos que los agentes nunca deben tocar (trazabilidad de los Días 1-3).
PROTECTED_PATTERNS = ("HALLAZGOS.md", "HU-*.md", ".github/*", ".git/*", "prompts/*", "docs/*")

_SKIP_DIRS = {".git", "node_modules", "target", ".venv", "venv", "__pycache__",
              ".pytest_cache", "dist", "build", ".angular", ".idea", ".vscode"}


def slugify(title: str, max_len: int = 24) -> str:
    """Rama-seguro: minúsculas, alfanumérico+guion, cortado a max_len."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return (slug or "feature")[:max_len]


def default_workspace(session_file: str = "") -> Path:
    """reqflow-workspace al lado de los labs (el mismo de los Días 1-3)."""
    base = Path(session_file).resolve().parent if session_file else Path.cwd()
    return (base.parent.parent / "reqflow-workspace").resolve()


def resolve_workspace(explicit: str = "", session_file: str = "") -> Path:
    """Workspace efectivo: REQFLOW_WORKSPACE, explícito o default."""
    raw = explicit or os.getenv("REQFLOW_WORKSPACE", "") or str(default_workspace(session_file))
    return Path(raw).expanduser().resolve()


def repo_tree(repo_path, max_files: int = 80, max_chars: int = 8000) -> str:
    """Árbol del repo + contenido de manifiestos (para grounding del Designer)."""
    root = Path(repo_path)
    if not root.is_dir():
        return f"(repo no encontrado: {repo_path})"
    paths: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS and not d.startswith("."))
        for fn in sorted(filenames):
            if fn.startswith("."):
                continue
            rel = str((Path(dirpath) / fn).relative_to(root)).replace("\\", "/")
            paths.append(rel)
            if len(paths) >= max_files:
                break
        if len(paths) >= max_files:
            break
    out = [f"Árbol de {root.name} ({len(paths)} archivos):"] + paths
    manifests = [p for p in paths if Path(p).name in (
        "pom.xml", "package.json", "requirements.txt", "angular.json",
        "application.properties", "README.md")]
    for m in manifests[:6]:
        try:
            content = (root / m).read_text(encoding="utf-8", errors="replace")[:1500]
        except OSError:
            continue
        out.append(f"\n--- {m} ---\n{content}")
    text = "\n".join(out)
    return text if len(text) <= max_chars else text[:max_chars] + "\n[... truncado ...]"


def _is_protected(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    return any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(Path(rel).name, pat)
               for pat in PROTECTED_PATTERNS)


def write_repo_files(repo_root, text: str) -> list[str]:
    """Escribe bloques `### <ruta relativa>` + fence dentro del repo.

    Rechaza escapes fuera del repo (`..`) y rutas protegidas. Nunca hace
    commit ni push. Retorna las rutas escritas.
    """
    root = Path(repo_root).resolve()
    pattern = re.compile(
        r"^#{1,3}\s*`?([^`\n]+?)`?\s*\n```[\w]*\n([\s\S]*?)```",
        re.MULTILINE,
    )
    saved: list[str] = []
    seen: set[str] = set()
    for m in pattern.finditer(text):
        rel = m.group(1).strip().strip("/").replace("\\", "/")
        code = m.group(2).rstrip() + "\n"
        if not rel or rel in seen:
            continue
        try:
            dest = (root / rel).resolve()
            dest.relative_to(root)
        except ValueError:
            continue  # escape fuera del repo
        if _is_protected(rel):
            continue
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(code, encoding="utf-8")
        except OSError:
            continue
        seen.add(rel)
        saved.append(rel)
    return saved


def ensure_branch(repo_path, branch: str) -> tuple[bool, str]:
    """Crea (o reutiliza) la rama local de trabajo. Nunca pushea."""
    try:
        cur = subprocess.run(["git", "-C", str(repo_path), "rev-parse", "--is-inside-work-tree"],
                             capture_output=True, text=True, timeout=15)
        if cur.returncode != 0 or cur.stdout.strip() != "true":
            return False, "no es un repo git"
        exists = subprocess.run(["git", "-C", str(repo_path), "rev-parse", "--verify", branch],
                                capture_output=True, text=True, timeout=15).returncode == 0
        args = ["git", "-C", str(repo_path), "checkout", branch] if exists \
            else ["git", "-C", str(repo_path), "checkout", "-b", branch]
        r = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return False, r.stderr.strip()[:200]
        return True, "reutilizada" if exists else "creada"
    except Exception as exc:
        return False, str(exc)[:200]


def repo_diffstat(repo_path, max_chars: int = 4000) -> str:
    """`git status` + `diff --stat` + diff acotado (evidencia para el Reviewer)."""
    parts: list[str] = []
    for args in (["git", "-C", str(repo_path), "status", "--porcelain"],
                 ["git", "-C", str(repo_path), "diff", "--stat"]):
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                parts.append(f"$ git {' '.join(args[2:])}\n{r.stdout.strip()}")
        except Exception:
            continue
    try:
        r = subprocess.run(["git", "-C", str(repo_path), "diff", "--", ".", ":(exclude)HALLAZGOS.md"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            diff = r.stdout.strip()
            parts.append(diff if len(diff) <= max_chars else diff[:max_chars] + "\n[... diff truncado ...]")
    except Exception:
        pass
    return "\n\n".join(parts) if parts else "(sin cambios)"

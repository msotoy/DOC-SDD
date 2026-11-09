"""
Nodos del grafo LangGraph S2.
Cada nodo llama al LLM directamente con retry ante errores de red (504, 502, 503).
Prompts reducidos para minimizar tokens generados y evitar timeouts.
"""
import time
from langchain_core.messages import SystemMessage, HumanMessage
from config.llm import llm
from hex_archetype import HEX_PROMPT_PREFIX

_MAX_RETRIES = 5
_RETRY_DELAY = 12.0   # segundos base (se duplica en cada intento)

# Máximo de caracteres de contexto pasados entre nodos
_CTX_LIMIT = 3000


def _invoke(system: str, user: str) -> str:
    """Llama al LLM con retry exponencial ante errores de servidor."""
    last_exc = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
            return response.content
        except Exception as e:
            last_exc = e
            msg = str(e).lower()
            is_retriable = any(code in msg for code in ["504", "503", "502", "500", "timeout", "connection"])
            if is_retriable and attempt < _MAX_RETRIES - 1:
                wait = _RETRY_DELAY * (2 ** attempt)
                print(f"\n  ⚠️  Error en intento {attempt + 1}/{_MAX_RETRIES}: {e}")
                print(f"  🔄 Reintentando en {wait:.0f}s...")
                time.sleep(wait)
            else:
                raise
    raise last_exc


def _ctx(text: str, max_chars: int = _CTX_LIMIT) -> str:
    """Trunca el contexto para no sobrecargar el prompt."""
    if not text or len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + f"\n\n[... +{len(text) - max_chars} chars omitidos ...]\n\n" + text[-half:]


def _ac_text(acceptance: list) -> str:
    if not acceptance:
        return "  (Ver descripción del feature)"
    # Máximo 5 criterios para no inflar el prompt
    items = acceptance[:5]
    suffix = f"\n  (+ {len(acceptance) - 5} más)" if len(acceptance) > 5 else ""
    return "\n".join(f"  - {c}" for c in items) + suffix


# ── Nodo 1: Designer ─────────────────────────────────────────────
def designer_node(state: dict) -> dict:
    title      = state.get("feature_title", "")
    brief      = state.get("feature_brief", "")
    acceptance = state.get("acceptance", [])
    repo_ctx   = state.get("repo_context", "")

    system = (
        "Eres un arquitecto de software senior en banca digital peruana (PCI-DSS, SBS). "
        "Produces especificaciones técnicas concisas y precisas, grounded en los repos reales."
    )

    repos = f"\nRepos involucrados (estructura real):\n{repo_ctx}\n\n" if repo_ctx else ""

    user = (
        f"Feature: **{title}**\n{brief}\n\n"
        f"{repos}"
        f"Criterios de aceptación:\n{_ac_text(acceptance)}\n\n"
        "Genera una especificación técnica con:\n"
        "1. Resumen del módulo (1-2 párrafos)\n"
        "2. Componentes y responsabilidades (lista breve)\n"
        "3. Contrato de API: endpoint, método, request/response JSON, códigos de error\n"
        "4. Reglas de negocio (lista numerada)\n"
        "5. Criterios de aceptación en formato Dado/Cuando/Entonces\n"
        "6. Archivos del repo a modificar/crear (rutas relativas existentes)\n\n"
        "Sé conciso. Máximo 600 palabras."
    )

    return {"designer_output": _invoke(system, user)}


# ── Nodo 2: Backend Developer (sobre el repo Quarkus real) ─────────
def backend_dev_node(state: dict) -> dict:
    title        = state.get("feature_title", "")
    acceptance   = state.get("acceptance", [])
    designer_ctx = _ctx(state.get("designer_output", ""), max_chars=2000)
    repo_ctx     = _ctx(state.get("repo_context", ""), max_chars=3000)

    system = (
        "Eres un desarrollador backend senior en Java Quarkus 3.x para microservicios bancarios. "
        "Trabajas SOBRE el repo existente (no un proyecto sintético): respetas su estructura, "
        "dependencias y estilo. Generas código limpio, funcional y seguro (BCrypt, JWT)."
        + HEX_PROMPT_PREFIX
    )

    ctx = f"Especificación del Designer:\n{designer_ctx}\n\n---\n\n" if designer_ctx else ""
    if repo_ctx:
        ctx += f"Repo real (estructura y manifiestos):\n{repo_ctx}\n\n---\n\n"
    corr = state.get("correction_notes", "")
    if corr:
        ctx += (f"Correcciones exigidas por el Reviewer "
                f"(ronda {state.get('correction_round', 1)}):\n{corr}\n"
                f"Aplica TODAS antes de entregar.\n\n---\n\n")

    user = (
        f"{ctx}"
        f"Implementa el backend Quarkus 3.x para **{title}** dentro del repo existente.\n\n"
        f"Criterios:\n{_ac_text(acceptance)}\n\n"
        "REGLAS:\n"
        "- Usa las dependencias y packages YA EXISTENTES en el repo; no inventes librerías.\n"
        "- El código nuevo separa capas: nada de `domain`/`application` puede importar de `infrastructure`.\n"
        "- PROHIBIDO tocar: HALLAZGOS.md, HU-*.md, .github/, prompts/, docs/. Sin commit ni push.\n\n"
        "Entrega cada archivo bajo su encabezado `### <ruta relativa al repo>` con fence, "
        "sin tests extensos ni comentarios verbosos. Código funcional y compacto."
    )

    return {"backend_output": _invoke(system, user)}


# ── Nodo 3: API Developer (scaffolding FastAPI en el repo) ───────────
def api_dev_node(state: dict) -> dict:
    title        = state.get("feature_title", "")
    acceptance   = state.get("acceptance", [])
    designer_ctx = _ctx(state.get("designer_output", ""), max_chars=2000)
    repo_ctx     = _ctx(state.get("repo_context", ""), max_chars=3000)

    system = (
        "Eres un desarrollador backend Python senior especializado en FastAPI para "
        "servicios bancarios. Generas el scaffolding completo (routers, modelos "
        "Pydantic, tests pytest) con código tipado y compacto."
    )

    ctx = f"Especificación del Designer:\n{designer_ctx}\n\n---\n\n" if designer_ctx else ""
    if repo_ctx:
        ctx += f"Repo real (estructura y manifiestos):\n{repo_ctx}\n\n---\n\n"
    corr = state.get("correction_notes", "")
    if corr:
        ctx += (f"Correcciones exigidas por el Reviewer "
                f"(ronda {state.get('correction_round', 1)}):\n{corr}\n"
                f"Aplica TODAS antes de entregar.\n\n---\n\n")

    user = (
        f"{ctx}"
        f"Genera el scaffolding FastAPI para **{title}** dentro del repo.\n\n"
        f"Criterios:\n{_ac_text(acceptance)}\n\n"
        "Entrega (rutas relativas al repo, todo el scaffolding lo generas tú):\n\n"
        "### `app/main.py`\n```python\n# app FastAPI + include_router + health\n```\n\n"
        "### `app/models/<recurso>.py`\n```python\n# modelos Pydantic\n```\n\n"
        "### `app/schemas/<recurso>.py`\n```python\n# esquemas request/response\n```\n\n"
        "### `app/routers/<recurso>.py`\n```python\n# endpoints REST\n```\n\n"
        "### `tests/test_<recurso>.py`\n```python\n# tests TestClient\n```\n\n"
        "PROHIBIDO tocar: HALLAZGOS.md, HU-*.md, .github/, prompts/, docs/. Sin commit ni push.\n"
        "Código funcional y compacto. Sin explicaciones adicionales."
    )

    return {"api_output": _invoke(system, user)}


# ── Nodo 4: Frontend Developer (sobre el repo Angular real) ───────
def frontend_dev_node(state: dict) -> dict:
    title        = state.get("feature_title", "")
    acceptance   = state.get("acceptance", [])
    designer_ctx = _ctx(state.get("designer_output", ""), max_chars=1500)
    backend_ctx  = _ctx(state.get("backend_output", ""), max_chars=2000)
    repo_ctx     = _ctx(state.get("repo_context", ""), max_chars=3000)

    system = (
        "Eres un desarrollador frontend Angular 17 para el BCP. Trabajas SOBRE el repo "
        "existente: respetas su arranque, routing y nombres exportados. "
        "Generas TypeScript estricto (no `any`), AuthGuard, interceptors JWT. Sin comentarios verbosos."
    )

    ctx_parts = []
    if designer_ctx:
        ctx_parts.append(f"Especificación:\n{designer_ctx}")
    if backend_ctx:
        ctx_parts.append(f"Backend:\n{backend_ctx}")
    if repo_ctx:
        ctx_parts.append(f"Repo real (estructura y manifiestos):\n{repo_ctx}")
    corr = state.get("correction_notes", "")
    if corr:
        ctx_parts.append(f"Correcciones exigidas por el Reviewer "
                         f"(ronda {state.get('correction_round', 1)}):\n{corr}. "
                         f"Aplica TODAS antes de entregar.")
    ctx = "\n\n---\n\n".join(ctx_parts) + "\n\n---\n\n" if ctx_parts else ""

    user = (
        f"{ctx}"
        f"Implementa los componentes Angular 17 para **{title}** dentro del repo existente.\n\n"
        f"Criterios:\n{_ac_text(acceptance)}\n\n"
        "REGLAS:\n"
        "- Extiende el routing y componentes existentes; no reinventes AppComponent/routes.\n"
        "- Rutas de archivo relativas al repo existente (sigue su layout src/app/...).\n"
        "- PROHIBIDO tocar: HALLAZGOS.md, HU-*.md, .github/, prompts/, docs/. Sin commit ni push.\n\n"
        "Entrega cada archivo bajo su encabezado `### <ruta relativa al repo>` con fence "
        "(código compacto, sin comentarios extensos)."
    )

    return {"frontend_output": _invoke(system, user)}


# ── Nodo 5: Tech Lead Reviewer ────────────────────────────────────
def reviewer_node(state: dict) -> dict:
    title        = state.get("feature_title", "")
    acceptance   = state.get("acceptance", [])
    designer_ctx = _ctx(state.get("designer_output", ""), max_chars=1000)
    backend_ctx  = _ctx(state.get("backend_output", ""), max_chars=1500)
    api_ctx      = _ctx(state.get("api_output", ""), max_chars=1500)
    frontend_ctx = _ctx(state.get("frontend_output", ""), max_chars=1500)
    diff_ctx     = _ctx(state.get("review_diff", ""), max_chars=3000)

    system = (
        "Eres el tech lead del BCP. Revisas código en entornos regulados. "
        "Emites veredictos técnicos concisos y accionables."
    )

    ctx_parts = []
    if designer_ctx:
        ctx_parts.append(f"Designer:\n{designer_ctx}")
    if backend_ctx:
        ctx_parts.append(f"Backend:\n{backend_ctx}")
    if api_ctx:
        ctx_parts.append(f"API:\n{api_ctx}")
    if frontend_ctx:
        ctx_parts.append(f"Frontend:\n{frontend_ctx}")
    if diff_ctx:
        ctx_parts.append(f"Diff real en los repos:\n{diff_ctx}")
    ctx = "\n\n---\n\n".join(ctx_parts) + "\n\n---\n\n" if ctx_parts else ""

    user = (
        f"{ctx}"
        f"Revisa los outputs para **{title}** (sólo los stacks que corrieron).\n\n"
        "Checklist (responde SÍ/NO por ítem):\n"
        "1. Cada agente implementa las reglas del Designer\n"
        "2. Contrato de API consistente entre spec y código\n"
        "3. Criterios de aceptación cubiertos:\n"
        f"{_ac_text(acceptance)}\n"
        "4. Sin riesgos de seguridad evidentes (credentials hardcoded, logging sensible)\n"
        "5. Código compatible con el stack del repo (Quarkus 3.x / Angular 17 / FastAPI)\n"
        "6. El código nuevo respeta la estructura del repo y separa capas "
        "(nada de dominio importando infraestructura)\n\n"
        "Concluye con: **VEREDICTO: APROBADO** o **VEREDICTO: RECHAZADO**\n"
        "Si RECHAZADO, lista máximo 5 observaciones accionables numeradas.\n"
        "Máximo 300 palabras."
    )

    return {"reviewer_output": _invoke(system, user)}

"""
Fábrica de tareas del crew BCP.
Las tareas se construyen dinámicamente a partir del feature seleccionado
del backlog (MCP Projects), de modo que el crew trabaja siempre sobre
el requerimiento real — no sobre un caso de ejemplo hardcodeado.

Uso:
    from crew.tasks import build_tasks
    t_story, t_backend, t_api, t_frontend, t_review = build_tasks(feature, repo_ctx)

donde `feature` es el dict devuelto por mcp_projects.get_feature_from_item():
    {
        "title": str,
        "description": str,
        "acceptance_criteria": list[str],
    }

y `repo_ctx` (opcional) mapea stack -> {"repo": nombre, "tree": árbol+manifiestos}:
    {"backend": {"repo": "workshop-auth-backend", "tree": "..."}, ...}
Los agentes de código trabajan SOBRE esos repos (rama local, sin push) y
entregan cada archivo con encabezado `### <ruta relativa al repo>`.
"""
from crewai import Task
from crew.agents import designer, backend_dev, frontend_dev, api_dev, reviewer


def _rc(repo_ctx: dict | None, stack: str) -> str:
    """Bloque de grounding del repo para el prompt, o '' si no hay."""
    if not repo_ctx or stack not in repo_ctx:
        return ""
    info = repo_ctx[stack]
    return (
        f"\nTrabajas SOBRE EL REPO EXISTENTE **{info.get('repo', stack)}** "
        f"(ya clonado en el workspace, rama local de trabajo). "
        f"Respeta su estructura, dependencias y estilo; modifica o crea "
        f"sólo lo necesario para el feature.\n"
        f"Estructura y manifiestos del repo:\n{info.get('tree', '(sin árbol)')}\n"
    )


_REPO_RULES = (
    "OBLIGATORIO: cada archivo se entrega con encabezado `### <ruta relativa "
    "al repo>` seguido de fence con código (ej:\n"
    "### src/main/java/pe/bcp/auth/AuthService.java\n```java\n...\n```\n).\n"
    "PROHIBIDO tocar: HALLAZGOS.md, HU-*.md, .github/, prompts/, docs/. "
    "PROHIBIDO hacer commit o push: sólo se escriben archivos en disco.\n"
)


def build_tasks(feature: dict, repo_ctx: dict | None = None) -> tuple:
    """
    Construye las 5 tareas del crew a partir del feature cargado del backlog.

    Args:
        feature: dict con keys 'title', 'description', 'acceptance_criteria'
        repo_ctx: opcional, grounding por stack (ver docstring del módulo)

    Returns:
        Tupla (t_story, t_backend, t_api, t_frontend, t_review)
    """
    title = feature.get("title", "(sin título)")
    description = feature.get("description", "")
    ac_list = feature.get("acceptance_criteria", [])

    # Formatear criterios de aceptación para incluirlos en las tareas
    ac_text = (
        "\n".join(f"  - {c}" for c in ac_list)
        if ac_list
        else "  (Ver descripción del feature)"
    )

    feature_brief = (
        f"**Feature:** {title}\n\n"
        f"{description}\n\n"
        f"**Criterios de aceptación:**\n{ac_text}"
    )

    # ── Tarea 1: Especificación técnica (Chapter / Designer) ──────────────
    t_story = Task(
        description=(
            f"Analiza el siguiente brief de feature y produce una especificación "
            f"técnica completa alineada a los estándares BCP:\n\n"
            f"{feature_brief}\n\n"
            "Tu output debe incluir:\n"
            "1. Resumen del módulo (2-3 párrafos)\n"
            "2. Componentes principales con responsabilidades\n"
            "3. Contrato de la API principal (endpoint, método HTTP, "
            "   request body, response body y códigos de error)\n"
            "4. Reglas de negocio formalizadas\n"
            "5. Criterios de aceptación medibles — uno por cada criterio "
            "   listado en el brief, en formato 'Dado / Cuando / Entonces'"
        ),
        expected_output=(
            "Especificación técnica en texto estructurado con secciones "
            "numeradas, contrato de API en formato JSON/pseudocódigo y "
            "lista de criterios de aceptación con formato "
            "'Dado / Cuando / Entonces'. Mínimo un criterio por cada "
            "acceptance criteria del feature."
        ),
        agent=designer,
    )

    # ── Tarea 2: Implementación backend (sobre el repo) ────────────
    t_backend = Task(
        description=(
            f"Basándote en la especificación técnica generada por el Designer "
            f"para el feature **{title}**, implementa el backend en Java Quarkus 3.x.\n"
            f"{_rc(repo_ctx, 'backend')}\n"
            "IMPORTANTE: Todo el código fuente (nombres de clases, atributos, métodos, DTOs y nombres de archivo) "
            "debe generarse estrictamente en INGLÉS siguiendo las mejores prácticas bancarias del BCP.\n\n"
            "Usa las dependencias y packages YA EXISTENTES en el repo (ver árbol y pom.xml arriba) — "
            "no inventes librerías ni packages nuevos salvo que el repo los justifique.\n\n"
            "Requisitos de entrega:\n"
            "- Entidad/modelo principal del feature, con constructores y getters/setters completos.\n"
            "- Repositorio/persistencia para la entidad principal.\n"
            "- DTOs tipados (Request y Response) con validaciones Jakarta (@NotNull, @NotBlank, etc.).\n"
            "- Service con lógica de negocio y tratamiento seguro de datos sensibles (BCrypt si aplica).\n"
            "- Resource/Controller con endpoints REST y códigos HTTP adecuados (200, 201, 400, 404, 409).\n"
            "- Al menos un test unitario con JUnit 5.\n\n"
            f"{_REPO_RULES}"
        ),
        expected_output=(
            "Código Java completo y funcional en inglés para cada archivo solicitado, "
            "cada uno bajo encabezado `### <ruta relativa al repo>` con fence. "
            "Cada archivo debe compilar en el repo y cubrir los criterios de aceptación."
        ),
        agent=backend_dev,
    )

    # ── Tarea 3: Scaffolding API FastAPI (sobre el repo) ────────────
    t_api = Task(
        description=(
            f"Basándote en la especificación técnica generada por el Designer "
            f"para el feature **{title}**, genera el scaffolding del API en Python FastAPI "
            f"desde cero dentro del repo (todo el scaffolding lo generas tú).\n"
            f"{_rc(repo_ctx, 'api')}\n"
            "IMPORTANTE: código en INGLÉS, tipado (Pydantic v2), routers por recurso, "
            "manejo de errores HTTP y tests pytest.\n\n"
            "Requisitos de entrega (rutas relativas al repo):\n"
            "- `app/main.py`: app FastAPI con include_router y health check.\n"
            "- `app/models/<recurso>.py`: modelos de dominio/Pydantic del feature.\n"
            "- `app/schemas/<recurso>.py`: esquemas request/response con validación.\n"
            "- `app/routers/<recurso>.py`: endpoints REST (GET/POST/PUT/DELETE según aplique) con status codes adecuados.\n"
            "- `app/core/config.py`: settings por entorno (si el repo no lo trae).\n"
            "- `tests/test_<recurso>.py`: tests del API con TestClient.\n"
            "- Actualizar `requirements.txt` sólo si falta fastapi/uvicorn/pytest/httpx.\n\n"
            f"{_REPO_RULES}"
        ),
        expected_output=(
            "Scaffolding FastAPI completo y funcional, cada archivo bajo encabezado "
            "`### <ruta relativa al repo>` con fence. Los tests deben pasar con pytest."
        ),
        agent=api_dev,
    )

    # ── Tarea 4: Implementación frontend (sobre el repo) ──────────────
    t_frontend = Task(
        description=(
            f"Basándote en la API definida por el Designer y el Backend "
            f"para el feature **{title}**, implementa los componentes Angular 17.\n"
            f"{_rc(repo_ctx, 'frontend')}\n"
            "IMPORTANTE: Todo el código fuente (interfaces, servicios, componentes, selectores y archivos) "
            "debe generarse estrictamente en INGLÉS bajo estándares Angular 17.\n\n"
            "Respeta el arranque y rutas YA EXISTENTES en el repo (main.ts, app.routes.ts, "
            "nombres exportados exactos como AppComponent/routes): no los reinventes, extiéndelos.\n\n"
            "Requisitos de entrega (rutas relativas al repo, siguiendo su layout):\n"
            "- models: interfaces TypeScript del feature con `export interface ...`\n"
            "- servicio HTTP que consume los endpoints del backend, importando los modelos.\n"
            "- guard de acceso si el feature lo requiere.\n"
            "- componente STANDALONE (`standalone: true`) con template, estilos y validaciones.\n"
            "- interceptor HTTP si se requiere manejo de token.\n"
            "- rutas del feature agregadas al routing existente.\n\n"
            "Estándares BCP: componentes standalone Angular 17, errores HTTP con mensajes "
            "amigables, TypeScript estricto sin `any`.\n\n"
            f"{_REPO_RULES}"
        ),
        expected_output=(
            "Código TypeScript/HTML completo en inglés para cada archivo, cada uno bajo "
            "encabezado `### <ruta relativa al repo>` con fence. "
            "Los componentes deben ser standalone y consumir la API del Backend."
        ),
        agent=frontend_dev,
    )

    # ── Tarea 5: Revisión técnica y veredicto ─────────────────────────
    t_review = Task(
        description=(
            f"Revisa los outputs anteriores (Designer y agentes de código que corrieron) "
            f"para el feature **{title}** y emite un veredicto técnico.\n\n"
            "Checklist de revisión (sólo lo que corrió en este alcance):\n"
            "1. ¿Cada agente de código implementa las reglas de negocio del Designer?\n"
            "2. ¿El contrato de API del Designer coincide con el código generado?\n"
            "3. ¿Cada criterio de aceptación está cubierto por el código?\n"
            "   Criterios a verificar:\n"
            f"{ac_text}\n"
            "4. ¿Hay riesgos de seguridad? (credenciales hardcodeadas, "
            "   logging de datos sensibles, falta de validación de inputs)\n"
            "5. ¿El código respeta el stack y versiones del repo (Quarkus 3.x / Angular 17 / FastAPI)?\n\n"
            "Emitir veredicto final: VEREDICTO: APROBADO o VEREDICTO: RECHAZADO\n"
            "con observaciones numeradas y accionables."
        ),
        expected_output=(
            "Reporte de revisión con:\n"
            "- VEREDICTO: APROBADO / RECHAZADO (en mayúsculas y negrita)\n"
            "- Tabla de cobertura: criterio → estado (✅/❌) → observación\n"
            "- Lista numerada de observaciones accionables\n"
            "- Resumen ejecutivo de una línea"
        ),
        agent=reviewer,
    )

    return t_story, t_backend, t_api, t_frontend, t_review
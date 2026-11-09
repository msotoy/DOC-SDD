# -*- coding: utf-8 -*-
"""Check del graph de S3 — no llama al LLM ni al MCP.

Verifica las dos garantías que el pipeline necesita:

  1. HITL vivo: con `interrupt_before`, cada `graph.invoke(None, config)`
     ejecuta EXACTAMENTE un nodo y vuelve a pausar. Si alguien quita el
     interrupt, el grafo corre los 5 nodos en una sola llamada y este check falla.
  2. Retry automático: si el reviewer no aprueba, la arista condicional
     vuelve a `backend` sin intervención humana, hasta MAX_RETRIES.

Ejecutar:  .venv\\Scripts\\python.exe test_graph_hitl.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import graph.nodes as nodes
from graph.graph import graph, NODES, MAX_RETRIES


# ── Stub del LLM: responde según el rol que lo invoca ──────────────
class Stub:
    """Reemplaza a nodes._invoke. Cuenta llamadas y guion del reviewer."""

    def __init__(self, veredictos):
        self.calls = []
        self.veredictos = list(veredictos)

    # Ancla en la linea de rol que ABRE cada prompt. Ojo: los prompts de
    # backend y frontend citan "Plan del Chapter Lead:", asi que buscar
    # "Chapter Lead" suelto los clasifica mal.
    ROLES = [
        ("Eres un Backend Developer senior",      "backend"),
        ("Eres un Frontend/API Developer senior", "frontend"),
        ("Eres el Chapter Lead (arquitecto)",     "chapter"),
        ("Eres un Tech Lead senior",              "analyze"),
        ("Eres el Tech Lead Reviewer",            "reviewer"),
    ]

    def __call__(self, prompt: str) -> str:
        rol = next((r for marca, r in self.ROLES if marca in prompt), None)
        assert rol, f"prompt sin rol reconocible: {prompt[:80]!r}"
        self.calls.append(rol)
        if rol == "reviewer":
            return self.veredictos.pop(0) if self.veredictos else "APROBADO"
        return f"### app/demo.py\n```python\n# salida simulada de {rol}\n```"


def seed(thread_id, project_type="ambos", context="(constitucion simulada)"):
    """Siembra el estado como lo hará el harness en la Etapa 2."""
    estado = {
        "repo_name": "owner/repo", "snapshot": "### app/demo.py\nprint(1)",
        "project_type": project_type, "context": context,
        "out_analysis": "", "out_plan": "", "out_backend": "",
        "out_frontend": "", "out_reviewer": "",
        "approved": False, "retry_count": 0,
    }
    cfg = {"configurable": {"thread_id": thread_id}}
    graph.invoke(estado, cfg)          # se detiene ANTES del primer nodo
    return cfg


def siguiente(cfg):
    """Nombre del nodo que el grafo ejecutaría a continuación, o None."""
    nxt = graph.get_state(cfg).next
    return nxt[0] if nxt else None


def test_hitl_un_nodo_por_invoke():
    nodes._invoke = Stub(["APROBADO"])
    cfg = seed("t-hitl")

    assert siguiente(cfg) == "analyze", f"tras sembrar deberia esperar en analyze, no {siguiente(cfg)}"
    assert not nodes._invoke.calls, "sembrar el estado NO debe ejecutar ningun nodo"

    recorrido = []
    for esperado in NODES:
        actual = siguiente(cfg)
        assert actual == esperado, f"esperaba pausa antes de '{esperado}', esta en '{actual}'"
        antes = len(nodes._invoke.calls)
        graph.invoke(None, cfg)
        corridos = len(nodes._invoke.calls) - antes
        assert corridos == 1, f"'{esperado}' disparo {corridos} llamadas al LLM, no 1"
        recorrido.append(esperado)

    assert siguiente(cfg) is None, "el grafo deberia haber terminado"
    assert recorrido == NODES, f"orden inesperado: {recorrido}"
    print(f"1. HITL: {len(NODES)} nodos, 1 invoke = 1 nodo  ->  {' -> '.join(recorrido)}  OK")


def test_retry_automatico():
    # El reviewer rechaza, luego aprueba con observaciones, y aprueba limpio.
    nodes._invoke = Stub(["RECHAZADO", "APROBADO CON OBSERVACIONES", "APROBADO"])
    cfg = seed("t-retry")

    for _ in range(40):                      # tope de seguridad
        if siguiente(cfg) is None:
            break
        graph.invoke(None, cfg)

    vals = graph.get_state(cfg).values
    backends  = nodes._invoke.calls.count("backend")
    reviewers = nodes._invoke.calls.count("reviewer")
    assert backends == 3, f"esperaba 3 pasadas por backend, hubo {backends}"
    assert reviewers == 3, f"esperaba 3 revisiones, hubo {reviewers}"
    assert vals["approved"] is True, "deberia terminar aprobado"
    assert vals["retry_count"] == 3, f"retry_count={vals['retry_count']}, esperaba 3"
    print(f"2. Retry automatico: {backends} rondas backend, {reviewers} revisiones, "
          f"aprobado al final (max {MAX_RETRIES})  OK")


def test_salta_por_project_type():
    nodes._invoke = Stub(["APROBADO"])
    cfg = seed("t-backend-solo", project_type="backend")

    for _ in range(20):
        if siguiente(cfg) is None:
            break
        graph.invoke(None, cfg)

    llamadas = nodes._invoke.calls
    assert "backend" in llamadas, "backend deberia haber corrido"
    assert "frontend" not in llamadas, "frontend NO deberia correr con project_type=backend"
    assert graph.get_state(cfg).values["out_frontend"] == "", "out_frontend deberia quedar vacio"
    print(f"3. project_type='backend': frontend saltado  ->  {llamadas}  OK")


def test_context_llega_a_los_nodos():
    prompts = []

    def espia(base):
        def _f(p):
            prompts.append(p)
            return base(p)
        return _f

    # Sin contexto: ningun prompt debe traer la marca.
    base = Stub(["APROBADO"])
    nodes._invoke = espia(base)
    cfg = seed("t-sin-ctx", context="")
    for _ in range(20):
        if siguiente(cfg) is None:
            break
        graph.invoke(None, cfg)
    assert not any("MARCA-CONSTITUCION" in p for p in prompts), \
        "sin context no deberia aparecer el bloque de constitucion"

    # Con contexto: debe llegar a chapter, devs y reviewer, pero no a analyze.
    prompts.clear()
    base = Stub(["APROBADO"])
    nodes._invoke = espia(base)
    cfg = seed("t-con-ctx", context="MARCA-CONSTITUCION")
    for _ in range(20):
        if siguiente(cfg) is None:
            break
        graph.invoke(None, cfg)

    con_marca = [p for p in prompts if "MARCA-CONSTITUCION" in p]
    assert len(con_marca) >= 3, f"solo {len(con_marca)} prompts recibieron el contexto"
    assert not any("Tech Lead senior" in p for p in con_marca), \
        "analyze_node NO debe recibir la constitucion"
    print(f"4. context: {len(con_marca)}/{len(prompts)} nodos lo usan, analyze queda libre  OK")


def main():
    test_hitl_un_nodo_por_invoke()
    test_retry_automatico()
    test_salta_por_project_type()
    test_context_llega_a_los_nodos()
    print("\nTodo OK — graph de S3 verificado (HITL + retry + skip + context).")


if __name__ == "__main__":
    main()

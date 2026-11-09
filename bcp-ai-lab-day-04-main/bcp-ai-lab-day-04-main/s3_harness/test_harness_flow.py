# -*- coding: utf-8 -*-
"""Check del harness de S3 — no llama al LLM, al MCP ni a git.

Comprueba que el harness sea de verdad la puerta de entrada del pipeline:

  1. `load_context()` arma instructions + constitution + policies.
  2. `run_with_harness()` siembra el estado SIN ejecutar ningun nodo, y
     deja `context` poblado; `run_without_harness()` lo deja vacio.
  3. `step()` avanza exactamente un nodo por llamada (el HITL de main.py
     depende de esto).
  4. `retry_node()` reejecuta un nodo y reemplaza su salida en el estado.
  5. `check_security_compliance()` puntua 0/5 y 5/5 segun el texto.

Ejecutar:  .venv\\Scripts\\python.exe test_harness_flow.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import graph.nodes as nodes
from harness import harness as H
from test_graph_hitl import Stub


REPO = "NTTData-Academy/workshop-requirements-api-template"
SNAP = "### app/main.py\n```python\nprint('hola')\n```"


def test_load_context():
    ctx = H.load_context()
    assert ctx, "load_context() devolvio vacio: faltan archivos del harness"
    for marca in ("INSTRUCCIONES DEL SISTEMA", "CONSTITUCIÓN", "POLÍTICAS DE HERRAMIENTAS"):
        assert marca in ctx, f"el contexto no incluye '{marca}'"
    assert "R1 — Contratos preservados" in ctx, "la constitucion cargada no trae las reglas R1-R6"
    print(f"1. load_context(): {len(ctx)} chars, 3 bloques + R1-R6  OK")


def test_siembra_sin_ejecutar():
    nodes._invoke = Stub(["APROBADO"])

    st = H.run_with_harness(REPO, SNAP, "ambos", "t-con")
    assert not nodes._invoke.calls, "sembrar NO debe ejecutar nodos"
    assert st["context"], "run_with_harness deberia poblar context"
    assert st["repo_name"] == REPO
    assert H.next_node("t-con") == "analyze"

    st2 = H.run_without_harness(REPO, SNAP, "ambos", "t-sin")
    assert st2["context"] == "", "run_without_harness deberia dejar context vacio"
    print("2. Siembra: 0 nodos ejecutados; context poblado con harness, vacio sin el  OK")


def test_step_un_nodo():
    nodes._invoke = Stub(["APROBADO"])
    H.run_with_harness(REPO, SNAP, "ambos", "t-step")

    recorrido = []
    while H.next_node("t-step") is not None:
        antes = len(nodes._invoke.calls)
        nodo, estado = H.step("t-step")
        assert len(nodes._invoke.calls) - antes == 1, \
            f"step() sobre '{nodo}' disparo mas de una llamada al LLM"
        recorrido.append(nodo)

    assert recorrido == ["analyze", "chapter", "backend", "frontend", "reviewer"], recorrido
    nodo, _ = H.step("t-step")
    assert nodo is None, "step() sobre un pipeline terminado deberia devolver None"
    print(f"3. step(): 1 nodo por llamada  ->  {' -> '.join(recorrido)}  OK")


def test_retry_node():
    nodes._invoke = Stub(["APROBADO"])
    H.run_with_harness(REPO, SNAP, "ambos", "t-retry-manual")
    H.step("t-retry-manual")                       # corre analyze
    primero = H.state("t-retry-manual")["out_analysis"]

    # El stub devuelve texto distinto en la segunda pasada
    base = Stub(["APROBADO"])
    nodes._invoke = lambda p: base(p) + "\n<<reintento>>"

    estado = H.retry_node("t-retry-manual", "analyze")
    assert "<<reintento>>" in estado["out_analysis"], "retry_node no reemplazo la salida"
    assert estado["out_analysis"] != primero
    assert H.next_node("t-retry-manual") == "chapter", \
        "tras el retry el pipeline deberia seguir esperando en chapter"
    print("4. retry_node(): reejecuta el nodo y reinyecta la salida  OK")

    try:
        H.retry_node("t-retry-manual", "inexistente")
    except ValueError:
        print("   retry_node() rechaza un nodo desconocido  OK")
    else:
        raise AssertionError("retry_node deberia rechazar un nodo invalido")


def test_resume_sin_reejecutar():
    """El resume adelanta el graph con los artefactos ya aprobados."""
    nodes._invoke = Stub(["APROBADO"])
    H.resume_with_harness(
        REPO, SNAP, "ambos", "t-resume",
        outputs={
            "out_analysis": "analisis ya aprobado",
            "out_plan":     "plan ya aprobado",
            "out_backend":  "",          # aca quedo la sesion anterior
            "out_frontend": "",
            "out_reviewer": "",
        },
    )
    assert not nodes._invoke.calls, "el resume NO debe reejecutar nodos"

    st = H.state("t-resume")
    assert st["out_analysis"] == "analisis ya aprobado"
    assert st["out_plan"] == "plan ya aprobado"
    assert H.next_node("t-resume") == "backend", \
        f"deberia continuar en backend, no en {H.next_node('t-resume')}"

    # Y desde ahi el pipeline sigue normal.
    nodo, _ = H.step("t-resume")
    assert nodo == "backend"
    assert nodes._invoke.calls == ["backend"], nodes._invoke.calls
    print("6. resume_with_harness(): adelanta analyze+chapter sin reejecutar, sigue en backend  OK")


def test_compliance():
    vacio = H.check_security_compliance("texto sin nada relevante")
    assert sum(vacio.values()) == 0, f"esperaba 0/6, dio {sum(vacio.values())}"

    completo = H.check_security_compliance(
        "Se preserva el contrato POST /auth/login de docs/ENDPOINTS.md. "
        "AUTH_TOKEN_SECRET se lee con os.getenv. SQL parametrizado y password con hash bcrypt. "
        "Token firmado HMAC con exp validado. exception_handler con mensajes genéricos. "
        "Test de caracterizacion con pytest; resuelve H-03 del issue #12."
    )
    assert all(completo.values()), f"esperaba 6/6, dio {sum(completo.values())}: {completo}"
    print("5. check_security_compliance(): 0/6 y 6/6 (R1-R6 ReqFlow) segun el texto  OK")


def test_contexto_del_producto():
    """El harness suma los artefactos de los Dias 1-3 que trae el repo clonado."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "REGLAS.md").write_text("Cobertura minima 85%", encoding="utf-8")
        spec = repo / "openspec" / "specs" / "tasks"
        spec.mkdir(parents=True)
        (spec / "spec.md").write_text("Scenario: GET /api/tasks devuelve 200", encoding="utf-8")
        ctx = H.load_context(repo)
    assert "=== CONTEXTO DEL PRODUCTO" in ctx
    assert "Cobertura minima 85%" in ctx and "GET /api/tasks devuelve 200" in ctx
    assert "=== CONTEXTO DEL PRODUCTO" not in H.load_context(), "sin repo no hay bloque de producto"
    print("8. load_context(repo_dir): suma REGLAS.md y openspec/specs del repo  OK")


def main():
    test_load_context()
    test_siembra_sin_ejecutar()
    test_step_un_nodo()
    test_retry_node()
    test_resume_sin_reejecutar()
    test_compliance()
    test_contexto_del_producto()
    print("\nTodo OK — harness de S3 verificado (contexto + siembra + step + retry + compliance).")


if __name__ == "__main__":
    main()

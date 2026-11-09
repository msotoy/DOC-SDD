# -*- coding: utf-8 -*-
"""Check del cableado hexagonal de S2 — no llama al LLM ni al MCP.

Verifica que FILE_MAP aterrice en las capas de HEX_LAYERS y que
scaffold() + validate() distingan un backend limpio de uno que viola
la regla de dependencias.

Ejecutar:  python test_hex_wiring.py
"""
import ast
import re
import tempfile
from pathlib import Path

from hex_archetype import HEX_LAYERS, scaffold, validate

HERE = Path(__file__).parent
PKG = "pe.bcp.login"


def file_map():
    """Lee FILE_MAP de main.py sin ejecutarlo (main.py arranca el flujo MCP)."""
    tree = ast.parse((HERE / "main.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FILE_MAP":
            return ast.literal_eval(node.value)
    raise AssertionError("FILE_MAP no encontrado en main.py")


def _blk(name, lang, body):
    return f"### `{name}`\n```{lang}\n{body}\n```\n\n"


def sample(clean: bool) -> str:
    service_imports = f"import {PKG}.domain.port.input.LoginUseCase;"
    if not clean:                      # viola: application -> infrastructure
        service_imports = f"import {PKG}.infrastructure.adapter.output.UserRepositoryJpa;\n" + service_imports
    return (
        _blk("User.java", "java", f"package {PKG}.domain.model;\npublic record User(Long id) {{}}")
        + _blk("LoginUseCase.java", "java", f"package {PKG}.domain.port.input;\npublic interface LoginUseCase {{}}")
        + _blk("UserRepository.java", "java", f"package {PKG}.domain.port.output;\npublic interface UserRepository {{}}")
        + _blk("TokenService.java", "java", f"package {PKG}.domain.port.output;\npublic interface TokenService {{}}")
        + _blk("LoginService.java", "java", f"package {PKG}.application.service;\n{service_imports}\npublic class LoginService {{}}")
        + _blk("AuthResource.java", "java", f"package {PKG}.infrastructure.adapter.input;\npublic class AuthResource {{}}")
        + _blk("LoginRequest.java", "java", f"package {PKG}.infrastructure.adapter.input;\npublic record LoginRequest(String u) {{}}")
        + _blk("AuthResponse.java", "java", f"package {PKG}.infrastructure.adapter.input;\npublic record AuthResponse(String t) {{}}")
        + _blk("UserRepositoryJpa.java", "java", f"package {PKG}.infrastructure.adapter.output;\npublic class UserRepositoryJpa {{}}")
        + _blk("JwtTokenAdapter.java", "java", f"package {PKG}.infrastructure.adapter.output;\npublic class JwtTokenAdapter {{}}")
        + _blk("application.properties", "properties", "quarkus.http.port=8080")
        + _blk("schema.sql", "sql", "CREATE TABLE users(id INTEGER PRIMARY KEY);")
    )


def pattern():
    """Toma el regex real de extract_and_save_code() en vez de duplicarlo,
    para que este check falle si alguien cambia el parser de main.py."""
    tree = ast.parse((HERE / "main.py").read_text(encoding="utf-8"))
    for fn in tree.body:
        if isinstance(fn, ast.FunctionDef) and fn.name == "extract_and_save_code":
            for node in ast.walk(fn):
                if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "pattern":
                    src = ast.literal_eval(node.value.args[0])
                    return re.compile(src, re.MULTILINE)
    raise AssertionError("regex 'pattern' no encontrado en extract_and_save_code()")


PATTERN = pattern()


def extract(text, fmap, out_dir):
    saved = []
    for m in PATTERN.finditer(text):
        name = Path(m.group(1).strip()).name
        if name in fmap:
            dest = out_dir / fmap[name]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(m.group(2).rstrip(), encoding="utf-8")
            saved.append(name)
    return saved


def main():
    fmap = file_map()

    # 1. Todo destino hex/ cae dentro de una capa declarada en HEX_LAYERS
    hex_dests = {k: v for k, v in fmap.items() if v.startswith("hex/")}
    assert hex_dests, "FILE_MAP no mapea nada a hex/"
    for name, dest in hex_dests.items():
        layer = str(Path(dest).parent).replace("\\", "/")[len("hex/"):]
        assert layer in HEX_LAYERS, f"{name} -> '{layer}' no es una capa de HEX_LAYERS"
    print(f"1. FILE_MAP: {len(hex_dests)} archivos en capas hexagonales validas  OK")

    # 2. Las 7 capas quedan cubiertas por al menos un archivo
    cubiertas = {str(Path(d).parent).replace("\\", "/")[len("hex/"):] for d in hex_dests.values()}
    faltan = set(HEX_LAYERS) - cubiertas
    assert not faltan, f"capas sin ningun archivo en FILE_MAP: {sorted(faltan)}"
    print(f"2. Las {len(HEX_LAYERS)} capas de HEX_LAYERS tienen destino  OK")

    # 3. Backend limpio -> APROBADO ; con violacion -> RECHAZADO
    for clean, esperado in [(True, True), (False, False)]:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            n = extract(sample(clean), fmap, out)
            assert len(n) == 12, f"se esperaban 12 archivos extraidos, hubo {len(n)}"
            scaffold(out / "hex", "Test Feature")
            res = validate(out / "hex")
            etiqueta = "limpio" if clean else "con violacion"
            assert res["passed"] is esperado, (
                f"backend {etiqueta}: passed={res['passed']}, esperado={esperado}")
            if not clean:
                assert res["semantic"]["violaciones"], "no se reporto la violacion"
            print(f"3. Backend {etiqueta}: {'APROBADO' if res['passed'] else 'RECHAZADO'}  OK")

    # 4. Un nombre fuera de FILE_MAP deja su capa vacia -> RECHAZADO estructural.
    #    Es el caso que el aviso de extract_and_save_code() debe hacer visible.
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        roto = sample(True).replace("### `LoginService.java`", "### `AuthService.java`")
        extract(roto, fmap, out)
        scaffold(out / "hex", "Test Feature")
        res = validate(out / "hex")
        assert not res["passed"], "un archivo descartado deberia romper la validacion"
        assert not res["structural"]["hex/application/service"], \
            "application/service deberia quedar vacia"
        print("4. Nombre fuera de FILE_MAP deja application/service vacia: RECHAZADO  OK")

    print("\nTodo OK — cableado hexagonal de S2 verificado.")


if __name__ == "__main__":
    main()

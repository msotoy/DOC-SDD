"""Verifica que el workspace tenga lo que el día siguiente necesita.

Uso (desde la carpeta del laboratorio):
    python tools/check_handoff.py --day 1|2|3|4 ../reqflow-workspace

El argumento final es reqflow-workspace/, la carpeta que contiene los repos
workshop-*. Solo comprueba que los archivos existan; la calidad la evalúa la
rúbrica. El día 4 re-verifica el hilo completo (días 1-3) más su tag de cierre.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPOS = (
    "workshop-auth-backend",
    "workshop-requirements-api",
    "workshop-login-frontend",
)


def pending_rows(hallazgos: Path) -> int:
    return sum(
        1
        for line in hallazgos.read_text(encoding="utf-8").splitlines()
        if line.lstrip().startswith("|") and "pendiente" in line.lower()
    )


def has_tag(repo: Path, tag: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "tag", "-l", tag],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == tag


def has_traced_hu(repo: Path) -> bool:
    return any("H-" in hu.read_text(encoding="utf-8") for hu in repo.glob("HU-*.md"))


def has_specs(repo: Path) -> bool:
    specs = repo / "openspec" / "specs"
    return any(specs.rglob("*")) if specs.is_dir() else False


# Por día: (descripción del faltante, comprobación sobre el repo).
CHECKS = {
    1: [
        ("HALLAZGOS.md", lambda r: (r / "HALLAZGOS.md").is_file()),
        ("docs/ENDPOINTS.md", lambda r: (r / "docs/ENDPOINTS.md").is_file()),
        ("docs/TESTING.md", lambda r: (r / "docs/TESTING.md").is_file()),
        ("prompts/*.md (al menos 1 prompt que te funcionó)", lambda r: any((r / "prompts").glob("*.md"))),
        ("tag git 'day1-done'", lambda r: has_tag(r, "day1-done")),
    ],
    2: [
        ("HU-*.md con su Origen (Id H-xx)", has_traced_hu),
        (".github/skills/*/SKILL.md", lambda r: any(r.glob(".github/skills/*/SKILL.md"))),
        ("docs/mcp-evidence/mcp.json (copia sin tokens)", lambda r: (r / "docs" / "mcp-evidence" / "mcp.json").is_file()),
        ("tag git 'day2-done'", lambda r: has_tag(r, "day2-done")),
    ],
    3: [
        ("openspec/specs/* (al menos 1 archivo)", has_specs),
        ("openspec/changes/*/proposal.md", lambda r: any(r.glob("openspec/changes/*/proposal.md"))),
        (".github/agents/*.agent.md", lambda r: any(r.glob(".github/agents/*.agent.md"))),
        (".github/skills/*/SKILL.md", lambda r: any(r.glob(".github/skills/*/SKILL.md"))),
        ("tag git 'day3-done'", lambda r: has_tag(r, "day3-done")),
    ],
    4: [
        ("tag git 'day4-done'", lambda r: has_tag(r, "day4-done")),
    ],
}
NEXT_DAY_INPUTS = {
    1: "el Día 2 convierte las filas 'Pendiente' en HU",
    2: "el Día 3 trabaja sobre esos issues del Project ReqFlow",
    3: "el Día 4 usa esas specs como contrato del agente",
    4: "el ciclo completo hallazgo -> HU -> issue -> spec -> PR queda verificado",
}


def check_repo(repo: Path, day: int = 1) -> list[str]:
    """Devuelve la lista de faltantes; vacía si el repo está listo."""
    days = (1, 2, 3, 4) if day == 4 else (day,)
    missing = [label for d in days for label, ok in CHECKS[d] if not ok(repo)]
    hallazgos = repo / "HALLAZGOS.md"
    if day == 1 and hallazgos.is_file() and pending_rows(hallazgos) == 0:
        print(f"[!!] {repo.name}: sin filas 'Pendiente'; el Día 2 usará las HU de referencia")
    return missing


def main(workspace: Path, day: int = 1) -> int:
    ready = []
    for name in REPOS:
        repo = workspace / name
        if not repo.is_dir():
            print(f"[--] {name}: no clonado")
            continue
        missing = check_repo(repo, day)
        if missing:
            print(f"[KO] {name}: falta " + "; ".join(missing))
        else:
            print(f"[OK] {name}")
            ready.append(name)

    workspace_ok = day != 2 or (workspace / ".vscode" / "mcp.json").is_file()
    if not workspace_ok:
        print("[KO] reqflow-workspace: falta .vscode/mcp.json")

    label = "Cierre del programa" if day == 4 else f"Handoff del Día {day}"
    if ready and workspace_ok:
        print(f"\n{label} listo ({NEXT_DAY_INPUTS[day]}): "
              f"{len(ready)} de {len(REPOS)} repos completos.")
        return 0
    if day == 4:
        print("\nCierre del programa incompleto. Termínalo: revisa el tag 'day4-done' y la evidencia del PR.")
    else:
        print(
            f"\nHandoff del Día {day} incompleto. Termínalo o parte de la rama "
            f"'checkpoint/day{day}' que entrega el instructor."
        )
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--day", type=int, choices=sorted(CHECKS), default=1)
    parser.add_argument("workspace", nargs="?", default=".")
    args = parser.parse_args()
    sys.exit(main(Path(args.workspace), args.day))

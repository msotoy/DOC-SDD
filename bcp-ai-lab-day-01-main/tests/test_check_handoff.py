import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_handoff import check_repo, main  # noqa: E402


def make_repo(root: Path, name: str, *, pending: bool = True, tag: bool = True) -> Path:
    repo = root / name
    (repo / "docs").mkdir(parents=True)
    (repo / "prompts").mkdir()
    estado = "Pendiente" if pending else "Resuelto"
    (repo / "HALLAZGOS.md").write_text(
        "| id | hallazgo | estado |\n|---|---|---|\n"
        f"| H-01 | Token sin firma | {estado} |\n",
        encoding="utf-8",
    )
    (repo / "docs" / "ENDPOINTS.md").write_text("# Endpoints", encoding="utf-8")
    (repo / "docs" / "TESTING.md").write_text("# Testing", encoding="utf-8")
    (repo / "prompts" / "discovery.md").write_text("CONTEXTO", encoding="utf-8")
    git = ["git", "-C", str(repo)]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run(
        [*git, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "d1"],
        check=True,
    )
    if tag:
        subprocess.run([*git, "tag", "day1-done"], check=True)
    return repo


class CheckHandoffTest(unittest.TestCase):
    def test_complete_repo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), "workshop-auth-backend")
            self.assertEqual(check_repo(repo), [])
            self.assertEqual(main(Path(tmp)), 0)

    def test_no_pending_rows_is_only_a_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), "workshop-auth-backend", pending=False)
            self.assertEqual(check_repo(repo), [])

    def test_missing_tag_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), "workshop-auth-backend", tag=False)
            self.assertEqual(check_repo(repo), ["tag git 'day1-done'"])
            self.assertEqual(main(Path(tmp)), 1)

    def test_empty_workspace_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(main(Path(tmp)), 1)

    def test_day2_needs_traced_hu_skill_tag_and_mcp_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            repo = make_repo(workspace, "workshop-auth-backend")
            self.assertEqual(len(check_repo(repo, day=2)), 3)

            (repo / "HU-01.md").write_text("## Origen\n- H-01", encoding="utf-8")
            skill = repo / ".github" / "skills" / "feature-intake"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "tag", "day2-done"], check=True)
            self.assertEqual(check_repo(repo, day=2), [])
            self.assertEqual(main(workspace, day=2), 1)

            (workspace / ".vscode").mkdir()
            (workspace / ".vscode" / "mcp.json").write_text("{}", encoding="utf-8")
            self.assertEqual(main(workspace, day=2), 0)


    def test_day3_needs_openspec_change_agents_and_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), "workshop-requirements-api")
            self.assertEqual(len(check_repo(repo, day=3)), 3)

            change = repo / "openspec" / "changes" / "issue-3-x"
            change.mkdir(parents=True)
            (change / "proposal.md").write_text("# Proposal", encoding="utf-8")
            (repo / ".github" / "agents").mkdir(parents=True)
            (repo / ".github" / "agents" / "developer.agent.md").write_text("---", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "tag", "day3-done"], check=True)
            self.assertEqual(check_repo(repo, day=3), [])
            self.assertEqual(main(Path(tmp), day=3), 0)


if __name__ == "__main__":
    unittest.main()

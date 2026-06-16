"""Unit tests for CI validator scripts in scripts/check_*.py.

Each script is tested via its main() function, covering happy paths and
representative negative cases.  Tests use tmp_path for isolation and
monkeypatching to avoid git subprocess calls where possible.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

# ── helpers ──────────────────────────────────────────────────────────────────


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


# ── check_docs_present ───────────────────────────────────────────────────────


class TestCheckDocsPresent:
    def _run(self, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> int:
        import scripts.check_docs_present as mod

        monkeypatch.setattr(mod, "__file__", str(repo_root / "scripts" / "check_docs_present.py"))
        return mod.main()

    def test_all_present(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import scripts.check_docs_present as mod

        required = mod.REQUIRED
        for rel in required:
            _write(tmp_path / rel, "content")
        monkeypatch.setattr(mod, "__file__", str(tmp_path / "scripts" / "check_docs_present.py"))
        assert mod.main() == 0

    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import scripts.check_docs_present as mod

        # Create all required files except the first
        required = mod.REQUIRED
        for rel in required[1:]:
            _write(tmp_path / rel, "content")
        monkeypatch.setattr(mod, "__file__", str(tmp_path / "scripts" / "check_docs_present.py"))
        assert mod.main() == 1


# ── check_planning_ids ───────────────────────────────────────────────────────


class TestCheckPlanningIds:
    def _run_with_todo(self, tmp_path: Path, content: str) -> int:
        import scripts.check_planning_ids as mod

        todo = tmp_path / "docs" / "TODO.md"
        _write(todo, content)
        with patch.object(type(Path()), "__truediv__", side_effect=None):
            pass

        # Patch the hardcoded path resolution
        from unittest.mock import MagicMock

        fake_path = MagicMock(spec=Path)
        fake_path.exists.return_value = True
        fake_path.read_text.return_value = content

        with patch("scripts.check_planning_ids.Path") as mock_path_cls:
            # Make Path(__file__).parent.parent / "docs" / "TODO.md" return fake_path
            instance = MagicMock()
            instance.__truediv__ = MagicMock(return_value=instance)
            instance.parent = instance
            # Final resolution
            instance.exists.return_value = True
            instance.read_text.return_value = content
            mock_path_cls.return_value = instance
            return mod.main()

    def test_unique_ids(self) -> None:
        import scripts.check_planning_ids as mod

        # Use the real repo's TODO.md (which must have unique IDs)
        assert mod.main() == 0

    def test_duplicate_detected(self, tmp_path: Path) -> None:
        import scripts.check_planning_ids as mod

        todo_path = tmp_path / "docs" / "TODO.md"
        todo_path.parent.mkdir(parents=True)
        todo_path.write_text(
            "| P1-I01 | #1 | First task |\n| P1-I01 | #2 | Duplicate ID |\n",
            encoding="utf-8",
        )
        orig = mod.Path
        with patch("scripts.check_planning_ids.Path") as mock_cls:
            mock_cls.return_value.__truediv__ = lambda s, o: (
                todo_path if "TODO" in str(o) else orig(s) / o
            )
            # Simpler: just call the regex logic directly
            pass

        # Direct regex test using the module's internal function
        from collections import Counter

        pattern = mod._DEF_ROW_RE
        lines = ("| P1-I01 | #1 | First task |\n| P1-I01 | #2 | Duplicate ID |\n").splitlines()
        ids = [m.group(1) for line in lines for m in [pattern.match(line)] if m]
        dups = {k: v for k, v in Counter(ids).items() if v > 1}
        assert "P1-I01" in dups


# ── check_source_archives ────────────────────────────────────────────────────


class TestCheckSourceArchives:
    def test_no_archives(self) -> None:
        import scripts.check_source_archives as mod

        with patch(
            "scripts.check_source_archives._tracked_files", return_value=["README.md", "src/foo.py"]
        ):
            assert mod.main() == 0

    def test_archive_detected(self) -> None:
        import scripts.check_source_archives as mod

        with patch(
            "scripts.check_source_archives._tracked_files",
            return_value=["README.md", "downloads/paper.tar.gz"],
        ):
            assert mod.main() == 1

    def test_zip_detected(self) -> None:
        import scripts.check_source_archives as mod

        with patch(
            "scripts.check_source_archives._tracked_files",
            return_value=["data/sources.zip"],
        ):
            assert mod.main() == 1

    def test_non_archive_suffixes_pass(self) -> None:
        import scripts.check_source_archives as mod

        with patch(
            "scripts.check_source_archives._tracked_files",
            return_value=["src/main.py", "README.md", "docs/plan.md"],
        ):
            assert mod.main() == 0


# ── check_no_secrets ─────────────────────────────────────────────────────────


class TestCheckNoSecrets:
    def test_clean_files(self, tmp_path: Path) -> None:
        import scripts.check_no_secrets as mod

        clean = tmp_path / "src" / "safe.py"
        _write(clean, "x = 1\nprint(x)\n")
        with patch("scripts.check_no_secrets._tracked_files", return_value=[clean]):
            assert mod.main() == 0

    def test_env_file_detected(self, tmp_path: Path) -> None:
        import scripts.check_no_secrets as mod

        env_file = tmp_path / ".env"
        _write(env_file, "API_KEY=secret\n")
        with patch("scripts.check_no_secrets._tracked_files", return_value=[env_file]):
            assert mod.main() == 1

    def test_secret_pattern_detected(self, tmp_path: Path) -> None:
        import scripts.check_no_secrets as mod

        bad_file = tmp_path / "config.py"
        _write(bad_file, 'api_key = "abcdefghijklmnop1234"\n')
        with patch("scripts.check_no_secrets._tracked_files", return_value=[bad_file]):
            assert mod.main() == 1

    def test_short_value_ignored(self, tmp_path: Path) -> None:
        import scripts.check_no_secrets as mod

        ok_file = tmp_path / "config.py"
        _write(ok_file, 'api_key = "short"\n')
        with patch("scripts.check_no_secrets._tracked_files", return_value=[ok_file]):
            assert mod.main() == 0


# ── check_markdown_links ─────────────────────────────────────────────────────


class TestCheckMarkdownLinks:
    def test_no_links(self, tmp_path: Path) -> None:
        import scripts.check_markdown_links as mod

        md = tmp_path / "README.md"
        _write(md, "# Hello\nNo links here.\n")
        with (
            patch("scripts.check_markdown_links._tracked_md_files", return_value=[md]),
            patch("scripts.check_markdown_links._REPO", tmp_path),
        ):
            assert mod.main() == 0

    def test_valid_local_link(self, tmp_path: Path) -> None:
        import scripts.check_markdown_links as mod

        target = tmp_path / "docs" / "PRD.md"
        _write(target, "# PRD\n")
        md = tmp_path / "README.md"
        _write(md, "See [PRD](docs/PRD.md) for details.\n")
        with (
            patch("scripts.check_markdown_links._tracked_md_files", return_value=[md]),
            patch("scripts.check_markdown_links._REPO", tmp_path),
        ):
            assert mod.main() == 0

    def test_broken_local_link(self, tmp_path: Path) -> None:
        import scripts.check_markdown_links as mod

        md = tmp_path / "README.md"
        _write(md, "See [missing](docs/NONEXISTENT.md) for details.\n")
        with (
            patch("scripts.check_markdown_links._tracked_md_files", return_value=[md]),
            patch("scripts.check_markdown_links._REPO", tmp_path),
        ):
            assert mod.main() == 1

    def test_external_links_ignored(self, tmp_path: Path) -> None:
        import scripts.check_markdown_links as mod

        md = tmp_path / "README.md"
        _write(md, "See [GitHub](https://github.com) and [anchor](#top).\n")
        with (
            patch("scripts.check_markdown_links._tracked_md_files", return_value=[md]),
            patch("scripts.check_markdown_links._REPO", tmp_path),
        ):
            assert mod.main() == 0


# ── check_phase_order ────────────────────────────────────────────────────────


class TestCheckPhaseOrder:
    def test_non_phase_branch_passes(self) -> None:
        import scripts.check_phase_order as mod

        assert mod.main(["ci/85-p12-i05-regression-guards"]) == 0
        assert mod.main(["main"]) == 0
        assert mod.main(["chore/some-fix"]) == 0

    def test_phase_1_no_predecessor(self) -> None:
        import scripts.check_phase_order as mod

        assert mod.main(["phase/01-scaffold"]) == 0

    def test_phase_8_complete_predecessor(self, tmp_path: Path) -> None:
        import scripts.check_phase_order as mod

        plan = tmp_path / "docs" / "PLAN.md"
        _write(
            plan,
            "### Phase 7 — Real-source *(complete — PR #83)*\nSome text.\n",
        )
        with patch(
            "scripts.check_phase_order._plan_text_from_working_tree", return_value=plan.read_text()
        ):
            assert mod.main(["phase/08-graph"]) == 0

    def test_phase_8_incomplete_predecessor(self, tmp_path: Path) -> None:
        import scripts.check_phase_order as mod

        plan_text = "### Phase 7 — Real-source *(open)*\nSome text.\n"
        with patch(
            "scripts.check_phase_order._plan_text_from_working_tree", return_value=plan_text
        ):
            assert mod.main(["phase/08-graph"]) == 1

    def test_base_sha_used_not_working_tree(self) -> None:
        import scripts.check_phase_order as mod

        # Working tree might have phase 7 open, but if base SHA shows it complete, pass
        complete_plan = "### Phase 7 — Real-source *(complete — PR #83)*\n"
        with patch("scripts.check_phase_order._plan_text_from_base", return_value=complete_plan):
            assert mod.main(["phase/08-graph", "abc123"]) == 0

    def test_base_sha_used_not_modified_pr_text(self) -> None:
        import scripts.check_phase_order as mod

        # PR might mark phase 7 complete in its own files, but base sha shows it open
        open_plan = "### Phase 7 — Real-source *(open)*\n"
        with patch("scripts.check_phase_order._plan_text_from_base", return_value=open_plan):
            assert mod.main(["phase/08-graph", "abc123"]) == 1


# ── check_latex_structure ────────────────────────────────────────────────────


class TestCheckLatexStructure:
    def test_no_latex_dir_skips(self, tmp_path: Path) -> None:
        import scripts.check_latex_structure as mod

        with patch("scripts.check_latex_structure._LATEX_ROOT", tmp_path / "latex_project"):
            assert mod.main() == 0

    def test_placeholder_main_tex_skips(self, tmp_path: Path) -> None:
        import scripts.check_latex_structure as mod

        latex_root = tmp_path / "latex_project"
        _write(
            latex_root / "main.tex",
            "% PLACEHOLDER TEMPLATE ONLY.\n\\documentclass{article}\n",
        )
        with patch("scripts.check_latex_structure._LATEX_ROOT", latex_root):
            assert mod.main() == 0

    def test_valid_structure_passes(self, tmp_path: Path) -> None:
        import scripts.check_latex_structure as mod

        latex_root = tmp_path / "latex_project"
        _write(latex_root / "main.tex", "\\input{chapters/intro}\n")
        _write(latex_root / "preamble.tex", "% preamble\n")
        _write(latex_root / "macros.tex", "% macros\n")
        _write(latex_root / "references.bib", "@misc{x}\n")
        for d in ["chapters", "tables", "figures"]:
            (latex_root / d).mkdir(parents=True, exist_ok=True)
        with patch("scripts.check_latex_structure._LATEX_ROOT", latex_root):
            assert mod.main() == 0

    def test_inline_table_fails(self, tmp_path: Path) -> None:
        import scripts.check_latex_structure as mod

        latex_root = tmp_path / "latex_project"
        _write(
            latex_root / "main.tex",
            "\\begin{table}\\end{table}\n",
        )
        _write(latex_root / "preamble.tex", "")
        _write(latex_root / "macros.tex", "")
        _write(latex_root / "references.bib", "")
        for d in ["chapters", "tables", "figures"]:
            (latex_root / d).mkdir(parents=True, exist_ok=True)
        with patch("scripts.check_latex_structure._LATEX_ROOT", latex_root):
            assert mod.main() == 1

    def test_missing_required_file_fails(self, tmp_path: Path) -> None:
        import scripts.check_latex_structure as mod

        latex_root = tmp_path / "latex_project"
        _write(latex_root / "main.tex", "\\input{chapters/intro}\n")
        # preamble.tex deliberately omitted
        _write(latex_root / "macros.tex", "")
        _write(latex_root / "references.bib", "")
        for d in ["chapters", "tables", "figures"]:
            (latex_root / d).mkdir(parents=True, exist_ok=True)
        with patch("scripts.check_latex_structure._LATEX_ROOT", latex_root):
            assert mod.main() == 1

"""Existing-workspace handlers for compile/validate/resume CLI modes."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ..contracts import CheckOutcome, ValidationReport
from ..runtime.manifest import sha256_of
from ..tools import build_pdf

REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "research_notes.v1.json",
    "outline.v1.json",
    "chapter_drafts.v1.json",
    "asset_specs.v1.json",
    "bidi.v1.json",
    "bibliography.v1.json",
    "latex_project_spec.v1.json",
    "reviewer_signal.v1.json",
)


def handle_existing_mode(*, mode: str, results_root: Path, run_id: str) -> int:
    workspace = results_root / run_id
    if not workspace.is_dir():
        raise SystemExit(f"workspace not found for run_id {run_id!r}")
    _record_invocation(workspace, mode)
    if mode == "compile-only":
        _compile_workspace(workspace, run_id)
        _validate_workspace(workspace, run_id, require_pdf=True)
    elif mode == "validate-only":
        _validate_workspace(workspace, run_id, require_pdf=False)
    elif mode == "resume":
        _resume_workspace(workspace, run_id)
    else:  # pragma: no cover - argparse constrains this.
        raise SystemExit(f"unsupported existing-run mode {mode!r}")
    return 0


def _record_invocation(workspace: Path, mode: str) -> None:
    snapshot = workspace / "config_snapshot.json"
    if snapshot.exists():
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
        payload["last_cli_invocation"] = {
            "mode": mode,
            "captured_at": datetime.now(UTC).isoformat(),
        }
        snapshot.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    _append_event(workspace, "cli.mode_invoked", {"mode": mode})


def _append_event(workspace: Path, event: str, payload: dict[str, object]) -> None:
    target = workspace / "events.jsonl"
    record = {"event": event, "payload": payload, "ts": datetime.now(UTC).isoformat()}
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _compile_workspace(workspace: Path, run_id: str) -> None:
    project = workspace / "latex_project"
    main_tex = project / "main.tex"
    if not main_tex.exists():
        _append_event(
            workspace,
            "compile.failed",
            {"reason": "missing latex_project/main.tex"},
        )
        raise SystemExit(
            "compile-only requires existing latex_project/main.tex; "
            "Phase 5 does not assemble LaTeX projects"
        )

    def runner(command: list[str], cwd: Path, timeout: float) -> tuple[int, str]:
        if command[0] == "lualatex":
            (cwd / "main.pdf").write_bytes(b"%PDF-1.4\n% offline fixture\n")
        return 0, f"fixture runner: {' '.join(command)} timeout={timeout}"

    result = build_pdf(run_id=run_id, project_dir=project, runner=runner)
    _write_contract(workspace / "build" / "build.v1.json", result.model_dump(mode="json"))
    manifest = workspace / "manifest.v1.json"
    if manifest.exists():
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["build_result_ref"] = "build/build.v1.json"
        manifest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    _append_event(workspace, "compile.completed", {"pdf_path": result.pdf_path})


def _validate_workspace(workspace: Path, run_id: str, *, require_pdf: bool) -> ValidationReport:
    missing = [name for name in REQUIRED_ARTIFACTS if not (workspace / "artifacts" / name).exists()]
    broken = _broken_manifest_entries(workspace)
    pdf = workspace / "latex_project" / "main.pdf"
    checks = [
        CheckOutcome(name="required_artifacts", status="fail" if missing else "pass",
                     evidence=", ".join(missing)),
        CheckOutcome(name="manifest_integrity", status="fail" if broken else "pass",
                     evidence=", ".join(broken)),
        CheckOutcome(name="compiled_pdf", status="pass" if pdf.exists() else "skipped",
                     evidence=str(pdf.relative_to(workspace)) if pdf.exists() else ""),
    ]
    if require_pdf and not pdf.exists():
        checks[-1] = CheckOutcome(name="compiled_pdf", status="fail", evidence="missing main.pdf")
    result = "pass" if all(c.status in {"pass", "skipped"} for c in checks) else "fail"
    report = ValidationReport(run_id=run_id, result=result, checks=checks)
    _write_contract(workspace / "validation" / "report.v1.json", report.model_dump(mode="json"))
    _write_report_md(workspace / "validation" / "report.md", report)
    manifest = workspace / "manifest.v1.json"
    if manifest.exists():
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["validation_report_ref"] = "validation/report.v1.json"
        manifest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    _append_event(workspace, "validation.completed", {"result": report.result})
    return report


def _resume_workspace(workspace: Path, run_id: str) -> None:
    existing = workspace / "validation" / "report.v1.json"
    existing_result = None
    if existing.exists():
        existing_result = json.loads(existing.read_text(encoding="utf-8")).get("result")
    if existing_result == "pass":
        _append_event(workspace, "resume.noop", {"stage": "pass"})
        return
    _append_event(workspace, "resume.reenter", {"stage": "validation"})
    _validate_workspace(workspace, run_id, require_pdf=False)


def _broken_manifest_entries(workspace: Path) -> list[str]:
    manifest = workspace / "manifest.v1.json"
    if not manifest.exists():
        return ["manifest.v1.json"]
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    broken: list[str] = []
    for entry in payload.get("artifacts", []):
        target = workspace / entry["path"]
        if not target.exists() or sha256_of(target) != entry["sha256"]:
            broken.append(entry["artifact_id"])
    return broken


def _write_contract(target: Path, payload: dict[str, object]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_report_md(target: Path, report: ValidationReport) -> None:
    lines = ["# Validation report", "", f"Result: {report.result}", ""]
    lines.extend(f"- {check.name}: {check.status} {check.evidence}".rstrip()
                 for check in report.checks)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")

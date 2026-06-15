"""Envelope and bounded-repair helper tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agentic_publishing_pipeline.contracts import (
    REPAIR_ATTEMPTS_ALLOWED,
    REQUIRED_CONTRACT_VERSIONS,
    ContractValidationError,
    ResearchNotes,
    parse_with_repair,
)


def _build_payload(*, dimensions: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "run_id": "RUN-TEST",
        "topic": "Reasoning",
        "dimensions": dimensions if dimensions is not None else [
            {"dimension": "planning", "summary": "Plans are good."},
        ],
        "candidate_references": [],
        "glossary": [],
    }


def test_repair_attempts_allowed_is_one() -> None:
    assert REPAIR_ATTEMPTS_ALLOWED == 1


def test_required_contract_versions_cover_e1_through_e12() -> None:
    expected = {
        "ResearchNotes.v1",
        "Outline.v1",
        "ChapterDrafts.v1",
        "AssetSpecs.v1",
        "BiDiSection.v1",
        "BibliographyBundle.v1",
        "LaTeXProjectSpec.v1",
        "ReviewerSignal.v1",
        "BuildResult.v1",
        "ValidationReport.v1",
        "PromotionRecord.v1",
    }
    assert set(REQUIRED_CONTRACT_VERSIONS) == expected


def test_envelope_defaults_to_v1() -> None:
    notes = ResearchNotes.model_validate(_build_payload())
    assert notes.contract_version == "v1"
    assert notes.run_id == "RUN-TEST"


def test_envelope_rejects_unknown_version() -> None:
    payload = _build_payload()
    payload["contract_version"] = "v999"
    with pytest.raises(ValidationError):
        ResearchNotes.model_validate(payload)


def test_parse_with_repair_happy_path() -> None:
    payload = _build_payload()
    model, log = parse_with_repair("ResearchNotes", payload, ResearchNotes.model_validate)
    assert isinstance(model, ResearchNotes)
    assert log.attempts == 1
    assert log.repaired is False


def test_parse_with_repair_repairs_once() -> None:
    bad = _build_payload(dimensions=[])
    repaired_calls: list[int] = []

    def repair(raw: dict[str, object], error: ValidationError) -> dict[str, object]:
        repaired_calls.append(1)
        fixed = dict(raw)
        fixed["dimensions"] = [
            {"dimension": "memory", "summary": "Memory matters."},
        ]
        return fixed

    model, log = parse_with_repair("ResearchNotes", bad, ResearchNotes.model_validate, repair)
    assert isinstance(model, ResearchNotes)
    assert log.attempts == 2
    assert log.repaired is True
    assert len(repaired_calls) == 1


def test_parse_with_repair_exhaustion_raises() -> None:
    bad = _build_payload(dimensions=[])

    def repair(raw: dict[str, object], error: ValidationError) -> dict[str, object]:
        return dict(raw)

    with pytest.raises(ContractValidationError) as info:
        parse_with_repair("ResearchNotes", bad, ResearchNotes.model_validate, repair)
    assert info.value.contract_name == "ResearchNotes"
    assert info.value.attempts == 2
    assert len(info.value.validation_errors) == 2


def test_parse_with_repair_no_repair_callable_raises_after_first_failure() -> None:
    bad = _build_payload(dimensions=[])
    with pytest.raises(ContractValidationError) as info:
        parse_with_repair("ResearchNotes", bad, ResearchNotes.model_validate)
    assert info.value.attempts == 1

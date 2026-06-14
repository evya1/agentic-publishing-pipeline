"""Versioned typed artifact contracts for the publishing pipeline.

Every meaningful task edge in ``docs/architecture/artifact_contracts.md``
is backed by a Pydantic model defined here. The deterministic runtime
parses every agent output through these models (with at most one
bounded repair attempt — see :mod:`._repair` and ADR-0002) before any
downstream stage consumes it.

The version tag on every model is ``v1`` and is enforced by the shared
:class:`ContractEnvelope`. Adding a breaking field requires a new
model version (``v2``) rather than mutating ``v1`` in place.
"""

from __future__ import annotations

from ._common import CandidateReference, GlossaryTerm, Placeholder, PlaceholderKind
from ._envelope import ContractEnvelope, ContractVersion
from ._repair import (
    REPAIR_ATTEMPTS_ALLOWED,
    ContractValidationError,
    RepairLog,
    parse_with_repair,
)
from .asset_specs import AssetSpec, AssetSpecs, TheoremLikeKind
from .bibliography import BibEntry, BibliographyBundle, VerificationStatus
from .bidi_section import BiDiSection
from .build_result import BuildPass, BuildResult
from .chapter_drafts import ChapterDraft, ChapterDrafts
from .latex_project import (
    ChapterSpec,
    FigureRef,
    IndexSpec,
    LaTeXProjectSpec,
    MacroSpec,
    NomenclatureSpec,
    PreambleSpec,
    TableRef,
)
from .outline import ChapterOutline, Outline
from .promotion import PromotionRecord
from .research_notes import ReasoningDimension, ResearchDimensionNote, ResearchNotes
from .reviewer_signal import ReviewerSignal, ReviewVerdict, Severity
from .validation_report import (
    CheckOutcome,
    CheckStatus,
    CitationCheck,
    PageReport,
    ValidationReport,
    ValidationResult,
)

REQUIRED_CONTRACT_VERSIONS: tuple[str, ...] = (
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
)

__all__ = [
    "AssetSpec",
    "AssetSpecs",
    "BibEntry",
    "BibliographyBundle",
    "BiDiSection",
    "BuildPass",
    "BuildResult",
    "CandidateReference",
    "ChapterDraft",
    "ChapterDrafts",
    "ChapterOutline",
    "ChapterSpec",
    "CheckOutcome",
    "CheckStatus",
    "CitationCheck",
    "ContractEnvelope",
    "ContractValidationError",
    "ContractVersion",
    "FigureRef",
    "GlossaryTerm",
    "IndexSpec",
    "LaTeXProjectSpec",
    "MacroSpec",
    "NomenclatureSpec",
    "Outline",
    "PageReport",
    "Placeholder",
    "PlaceholderKind",
    "PreambleSpec",
    "PromotionRecord",
    "REPAIR_ATTEMPTS_ALLOWED",
    "REQUIRED_CONTRACT_VERSIONS",
    "ReasoningDimension",
    "RepairLog",
    "ResearchDimensionNote",
    "ResearchNotes",
    "ReviewVerdict",
    "ReviewerSignal",
    "Severity",
    "TableRef",
    "TheoremLikeKind",
    "ValidationReport",
    "ValidationResult",
    "VerificationStatus",
    "parse_with_repair",
]

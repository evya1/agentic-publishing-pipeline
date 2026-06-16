import pytest

from agentic_publishing_pipeline.latex.file_plan import (
    FilePlanError,
    LaTeXFilePlan,
    PlannedBinaryFile,
    PlannedTextFile,
)


def test_file_plan_normalizes_and_sorts() -> None:
    plan = LaTeXFilePlan.build(
        text_files=[PlannedTextFile("b.tex", "b"), PlannedTextFile("a.tex", "a")],
        binary_files=[PlannedBinaryFile("figures/a.png", b"png")],
    )
    assert [item.relative_path for item in plan.text_files] == ["a.tex", "b.tex"]
    assert plan.text_files[0].content.endswith("\n")


def test_file_plan_rejects_traversal_and_duplicates() -> None:
    with pytest.raises(FilePlanError):
        LaTeXFilePlan.build(text_files=[PlannedTextFile("../bad.tex", "x")])
    with pytest.raises(FilePlanError):
        LaTeXFilePlan.build(
            text_files=[PlannedTextFile("a.tex", "x"), PlannedTextFile("a.tex", "y")]
        )

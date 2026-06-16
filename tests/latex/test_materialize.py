from pathlib import Path

from agentic_publishing_pipeline.latex.file_plan import (
    LaTeXFilePlan,
    PlannedBinaryFile,
    PlannedTextFile,
)
from agentic_publishing_pipeline.latex.materialize import materialize_plan


class Events:
    def __init__(self) -> None:
        self.values: list[tuple[str, object]] = []

    def append(self, kind: str, payload: object) -> None:
        self.values.append((kind, payload))


class Paths:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def child(self, relative: str | Path) -> Path:
        target = (self.root / relative).resolve()
        target.relative_to(self.root)
        return target


class Context:
    def __init__(self, root: Path) -> None:
        self.paths = Paths(root)
        self.events = Events()
        self.registered: list[str] = []

    def register_artifact(self, **kwargs) -> None:
        assert self.paths.child(kwargs["relative_path"]).exists()
        self.registered.append(kwargs["artifact_id"])


def test_materialize_uses_fileio_and_registers(tmp_path: Path) -> None:
    context = Context(tmp_path)
    plan = LaTeXFilePlan.build(
        text_files=[PlannedTextFile("main.tex", "content")],
        binary_files=[PlannedBinaryFile("figures/a.png", b"png")],
    )
    paths = materialize_plan(context=context, plan=plan)  # type: ignore[arg-type]
    assert len(paths) == 2
    assert len(context.registered) == 2
    assert any(kind == "fileio.wrote" for kind, _ in context.events.values)

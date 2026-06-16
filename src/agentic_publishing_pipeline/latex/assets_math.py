"""Allowlisted equation, cross-reference, and theorem rendering."""

from __future__ import annotations

from ..tools.markdown import escape_latex
from .config_models import AssetConfig

_EQUATIONS = {
    "attention": r"\operatorname{Attention}(Q,K,V)=\operatorname{softmax}(QK^{\top}/\sqrt{d_k})V",
    "expected-value": r"\mathbb{E}[X]=\sum_x x\,\Pr(X=x)",
    "retrieval-score": r"s(q,d)=\frac{q\cdot d}{\lVert q\rVert_2\lVert d\rVert_2}",
    "weighted-sum": r"y=\sum_{i=1}^{n} w_i x_i",
}
_THEOREMS = {"definition", "theorem", "lemma", "example", "proposition"}


def render_equation(asset: AssetConfig) -> str:
    template = str(asset.payload.get("template", ""))
    if template not in _EQUATIONS:
        raise ValueError(f"{asset.asset_id}: unsupported equation template {template!r}")
    return "\n".join(
        (
            "\\begin{equation}",
            _EQUATIONS[template],
            f"\\label{{eq:{asset.label}}}",
            "\\end{equation}",
            "",
        )
    )


def render_equation_ref(asset: AssetConfig) -> str:
    target = str(asset.payload.get("target", "")).strip()
    sentence = str(asset.payload.get("sentence", "")).strip()
    if not target or not sentence:
        raise ValueError(f"{asset.asset_id}: equation_ref requires target and sentence")
    safe = escape_latex(sentence).replace("[EQUATION]", f"Equation~\\eqref{{eq:{target}}}")
    return safe + "\n"


def render_theorem(asset: AssetConfig) -> str:
    kind = str(asset.payload.get("kind", "definition")).strip().lower()
    title = escape_latex(str(asset.payload.get("title", "")).strip())
    statement = escape_latex(str(asset.payload.get("statement", "")).strip())
    if kind not in _THEOREMS or not statement:
        raise ValueError(f"{asset.asset_id}: invalid theorem-like payload")
    option = f"[{title}]" if title else ""
    return "\n".join(
        (
            f"\\begin{{{kind}}}{option}",
            statement,
            f"\\label{{{kind}:{asset.label}}}",
            f"\\end{{{kind}}}",
            "",
        )
    )

"""Deterministic thin-root, preamble, macro, and backmatter templates."""

from __future__ import annotations

from collections.abc import Sequence

from ..tools.markdown import escape_latex

_SAFE_MACROS = {
    "AgentState": r"\mathcal{S}_{t}",
    "ToolCall": r"\operatorname{ToolCall}",
    "MemoryStore": r"\mathcal{M}",
    "RetrievalScore": r"\operatorname{score}",
}


def render_preamble() -> str:
    return r"""\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{english}
\setotherlanguage{hebrew}
\setmainfont{Latin Modern Roman}
\newfontfamily\englishfont[Script=Latin]{Latin Modern Roman}
\IfFontExistsTF{David CLM}{
  \newfontfamily\hebrewfont[Script=Hebrew]{David CLM}
}{
  \PackageError{agentic-publishing}{Font David CLM unavailable}{Install David CLM.}
}
\usepackage{xcolor}
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{graphicx,float}
\usepackage{booktabs,tabularx,array}
\usepackage{amsmath,amssymb,amsthm,mathtools}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning}
\usepackage{fancyhdr,listings,nomencl,imakeidx,csquotes}
\usepackage[backend=biber,style=numeric,sorting=none]{biblatex}
\usepackage[hidelinks]{hyperref}
\usepackage[nameinlink,noabbrev]{cleveref}
\makeindex[title=Index]
\makenomenclature
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{example}[theorem]{Example}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\BookTitle}
\fancyhead[R]{\nouppercase{\leftmark}}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{14pt}
"""


def semantic_macro_body(name: str) -> str:
    try:
        return _SAFE_MACROS[name]
    except KeyError as exc:
        raise ValueError(f"unsupported semantic macro: {name}") from exc


def render_macros(names: Sequence[str]) -> str:
    unknown = sorted(set(names) - set(_SAFE_MACROS))
    if unknown:
        raise ValueError(f"unsupported semantic macros: {unknown}")
    lines = ["% Deterministic project notation"]
    lines.extend(f"\\newcommand{{\\{name}}}{{{semantic_macro_body(name)}}}" for name in names)
    return "\n".join(lines) + "\n"


def render_main(chapter_files: Sequence[str]) -> str:
    body = "\n".join(f"\\input{{{path}}}" for path in chapter_files)
    return f"""\\documentclass[11pt,a4paper,oneside]{{book}}
\\input{{preamble}}
\\input{{macros}}
\\input{{metadata}}
\\addbibresource{{references.bib}}
\\begin{{document}}
\\frontmatter
\\input{{titlepage}}
\\tableofcontents
\\mainmatter
{body}
\\backmatter
\\input{{nomenclature_entries}}
\\printnomenclature
\\printbibliography
\\printindex
\\end{{document}}
"""


def render_nomenclature(entries: Sequence[tuple[str, str]]) -> str:
    lines = [
        f"\\nomenclature{{{escape_latex(symbol)}}}{{{escape_latex(description)}}}"
        for symbol, description in entries
    ]
    return "\n".join(lines) + "\n"

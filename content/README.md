# content/

> **Status:** scaffold only — no draft content exists yet.

This directory holds approved Markdown drafts of the article/book before they
are converted to LaTeX. See [`markdown_drafts/`](markdown_drafts/).

The workflow:

1. CrewAI Writer agent produces Markdown drafts in `markdown_drafts/`.
2. Reviewer agent + human reviewers iterate on the Markdown.
3. Only after manual approval does the LaTeX Formatter agent translate the
   Markdown into the LaTeX project under `../latex_project/`.

No draft chapters exist yet.

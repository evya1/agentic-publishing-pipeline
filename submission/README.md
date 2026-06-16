# submission/

> **Status (2026-06-17):** `final.pdf` copied here from `results/final.pdf`
> (21 pages, 213 KB). Rename to `<GROUP_CODE>-ex03.pdf` before uploading
> to Moodle. Each group member submits separately.

## Files

- `final.pdf` — the final article PDF (copy of `results/final.pdf`).
  Rename to `<GROUP_CODE>-ex03.pdf` per the course filename convention.

## Submission steps

1. Rename: `mv final.pdf <GROUP_CODE>-ex03.pdf`
2. Each group member uploads `<GROUP_CODE>-ex03.pdf` independently in Moodle.
3. Tick the Moodle submission boxes in [`../SUBMISSION_CHECKLIST.md`](../SUBMISSION_CHECKLIST.md).

## Regenerating the PDF from a clean checkout

```sh
git clone <repo-url>
cd agentic-publishing-pipeline
uv sync --frozen --group dev
uv run python scripts/build_pdf.py
# Output: results/final.pdf
```

Requires LuaLaTeX (MacTeX or TeX Live full) and the David CLM Hebrew font.
See `README.md` §Installation for details.

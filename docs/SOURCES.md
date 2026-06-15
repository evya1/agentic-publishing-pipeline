# Source-verification ledger

> **Status (P7-I00, 2026-06-16).** This file is the **canonical
> per-source audit trail** for the agentic-publishing-pipeline
> bibliography, fixed under `docs/PRD_bibliography_and_citations.md`
> §13.1. The locked manifest is `config/article_sources.yaml`; the
> verifier is the Bibliography Agent (Phase 7); the boundary policy is
> the untrusted-archive policy (P7-I07).

## 1. Scope and authority

- `docs/SOURCES.md` carries one canonical entry per source from the
  locked manifest, with sufficient evidence to reconstruct
  `final citation key → references.bib entry → verification method →
  authoritative metadata snapshot → local archive presence` for any
  future reviewer.
- `docs/AI_USAGE.md` records AI-assisted activity (model identity,
  prompts used, limitations, human verification, cost). It links here
  by `verification.run_id` and citation key but does **not** duplicate
  per-source bibliographic facts.
- `docs/PROMPTS.md` records prompt-registry contents verbatim.

## 2. Verification procedure (binding)

The procedure is fixed in `docs/PRD_bibliography_and_citations.md` §7.1
and reproduced here for self-containment:

1. **Schema check** of the manifest record.
2. **Locked-manifest membership.** Candidate must be in
   `config/article_sources.yaml`; no silent additions, replacements, or
   model-generated entries.
3. **Authoritative metadata retrieval.** arXiv API/metadata for arXiv
   sources; DOI registration metadata when a DOI genuinely exists;
   publisher metadata otherwise.
4. **Field cross-check.** Title, year, ordered authors compared against
   authoritative response. Any mismatch is recorded; material mismatch
   rejects the entry.
5. **DOI presence** is recorded only when authoritative metadata
   provides one. No synthesis from arXiv identifiers.
6. **Local archive presence.** Archive opened in metadata-only mode per
   the P7-I07 boundary; **not** authoritative for bibliographic facts.
7. **Status flip** (`verified` or `rejected`) with `verified_at` (UTC
   ISO 8601) and `verified_by` per the honest-identity convention
   below.

## 3. Honest-identity convention for `verified_by`

`verified_by = "<verifier-id>:<github-account>"`.

- `<verifier-id>` names the mechanism that actually ran the
  verification (for example `bibliography-agent`,
  `claude-opus-4.7+arxiv-api`, `human-review`).
- `<github-account>` is the authenticated GitHub login that ran the
  pipeline (the assignee of the corresponding issue).
- `<verifier-id>` is `human-review` **only** when a human personally
  inspected the authoritative metadata; otherwise the value names the
  agent or tool that performed the lookup. Misrepresenting a
  machine-assisted verification as `human-review` is a content-policy
  violation under PRD §8.6 / CLAUDE.md.

## 4. Machine-readable mirror

A machine-readable mirror of the canonical entries is maintained at
`results/run_logs/source_verification.json` (one record per locked
source plus a `summary` block). The mirror is generated alongside this
Markdown file by the Phase 7 audit step (P7-I03) so that automated
consistency checks can run without parsing prose.

## 5. Per-source entries

> Populated by the P7-I03 audit generator
> (`src/agentic_publishing_pipeline/bibliography/run_audit.py`) from
> the verified manifest, the P7-I02 verification report, the P7-I05
> rekey ledger, the committed authoritative arXiv fixtures, and the
> P7-I07 metadata-only archive inspector. Regeneration is
> deterministic apart from the `generated_at` timestamp on the
> mirror JSON. The machine-readable mirror lives at
> `results/run_logs/source_verification.json`.

### Entry schema

```yaml
final_citation_key: <authorYYYYkey>          # after P7-I05
previous_citation_key: <tbd…>                # the provisional manifest key
canonical_url: <arxiv abs URL or DOI URL>
arxiv_id: <id>                               # if applicable
doi: <doi or null>                           # only when authoritative
verified_title: <title>
verified_authors:                            # ordered, populated by P7-I02
  - <Surname, Given>
verified_year: <YYYY>
verification:
  status: verified | rejected | pending
  method: arxiv_api | doi | publisher_catalog
  verified_at: <ISO 8601 UTC>
  verified_by: <verifier-id>:<github-account>
  run_id: <run id>
  authoritative_source: <URL or identifier of the metadata response>
  authoritative_snapshot: <path to committed fixture or `null`>
local_archive:
  path: data/sources/arxiv/source_zips/<file>
  archive_inspection: metadata_only           # per P7-I07
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: <text or null>
```

<!-- P7I03_SECTION_START -->
### Per-source entries (populated by P7-I03)

| Final key | Provisional key | arXiv ID | Year | Status |
|-----------|------------------|----------|------|--------|
| `ke2025reasoningfrontiers` | `tbd2025reasoningfrontiers` | `2504.09037` | 2025 | verified |
| `wu2025agenticreasoningtools` | `tbd2025agenticreasoningtools` | `2502.04644` | 2025 | verified |
| `correa2025planningperformance` | `tbd2025planningperformance` | `2511.09378` | 2025 | verified |
| `huang2025licomemory` | `tbd2025licomemory` | `2511.01448` | 2025 | verified |
| `chen2025telemem` | `tbd2026telemem` | `2601.06037` | 2025 | verified |
| `yao2025multimodalsurvey` | `tbd2025multimodalsurvey` | `2510.10991` | 2025 | verified |
| `wang2025proactiveretrievalmedical` | `tbd2025proactiveretrievalmedical` | `2510.18303` | 2025 | verified |
| `liu2025agenticmath` | `tbd2025agenticmath` | `2510.19361` | 2025 | verified |
| `ye2024mirai` | `tbd2024mirai` | `2407.01231` | 2024 | verified |
| `wei2026agenticreasoning` | `tbd2026agenticreasoning` | `2601.12538` | 2026 | verified |

```yaml
arxiv_id: '2504.09037'
canonical_url: https://arxiv.org/abs/2504.09037
correction_applied: null
doi: null
final_citation_key: ke2025reasoningfrontiers
intended_use: Background framing for the reasoning landscape (inference-time scaling, learning to reason, agentic systems).
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2504.09037.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2025reasoningfrontiers
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2504.09037.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2504.09037
  method: arxiv_api
  primary_category: cs.AI
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Ke, Zixuan
- Jiao, Fangkai
- Ming, Yifei
- Nguyen, Xuan-Phi
- Xu, Austin
- Long, Do Xuan
- Li, Minzhi
- Qin, Chengwei
- Wang, Peifeng
- Savarese, Silvio
- Xiong, Caiming
- Joty, Shafiq
verified_title: 'A Survey of Frontiers in LLM Reasoning: Inference Scaling, Learning to Reason, and Agentic Systems'
verified_year: 2025
```

```yaml
arxiv_id: '2502.04644'
canonical_url: https://arxiv.org/abs/2502.04644
correction_applied:
  applied_at: '2026-06-16'
  applied_by: claude-opus-4.7+arxiv-api:evya1
  authoritative_value: 'Agentic Reasoning: A Streamlined Framework for Enhancing LLM Reasoning with Agentic Tools'
  field: title
  original_manifest_value: 'Agentic Reasoning: Reasoning LLMs with Tools for the Deep Research'
  rationale: manifest title was an explicit placeholder pending Phase 7 verification; replaced with authoritative arXiv title.
doi: null
final_citation_key: wu2025agenticreasoningtools
intended_use: Tool-use dimension; agentic reasoning combined with tools for deep-research workflows.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2502.04644.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2025agenticreasoningtools
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2502.04644.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2502.04644
  method: arxiv_api
  primary_category: cs.AI
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Wu, Junde
- Zhu, Jiayuan
- Liu, Yuyuan
- Xu, Min
- Jin, Yueming
verified_title: 'Agentic Reasoning: A Streamlined Framework for Enhancing LLM Reasoning with Agentic Tools'
verified_year: 2025
```

```yaml
arxiv_id: '2511.09378'
canonical_url: https://arxiv.org/abs/2511.09378
correction_applied:
  applied_at: '2026-06-16'
  applied_by: claude-opus-4.7+arxiv-api:evya1
  authoritative_value: Frontier Large Language Models Rival State-of-the-Art Planners
  field: title
  original_manifest_value: The 2025 Planning Performance of Frontier Large Language Models
  rationale: manifest title was an explicit placeholder pending Phase 7 verification; replaced with authoritative arXiv title.
doi: null
final_citation_key: correa2025planningperformance
intended_use: Planning dimension; empirical state of planning in frontier LLMs as of 2025.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2511.09378.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2025planningperformance
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2511.09378.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2511.09378
  method: arxiv_api
  primary_category: cs.AI
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Corrêa, Augusto B.
- Pereira, André G.
- Seipp, Jendrik
verified_title: Frontier Large Language Models Rival State-of-the-Art Planners
verified_year: 2025
```

```yaml
arxiv_id: '2511.01448'
canonical_url: https://arxiv.org/abs/2511.01448
correction_applied: null
doi: null
final_citation_key: huang2025licomemory
intended_use: Memory dimension; lightweight long-term memory architecture for agentic LLMs.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2511.01448.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2025licomemory
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2511.01448.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2511.01448
  method: arxiv_api
  primary_category: cs.IR
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Huang, Zhengjun
- Tian, Zhoujin
- Guo, Qintian
- Zhang, Fangyuan
- Zhou, Yingli
- Jiang, Di
- Xie, Zeying
- Zhou, Xiaofang
verified_title: 'LiCoMemory: Lightweight and Cognitive Agentic Memory for Efficient Long-Term Reasoning'
verified_year: 2025
```

```yaml
arxiv_id: '2601.06037'
canonical_url: https://arxiv.org/abs/2601.06037
correction_applied:
  applied_at: '2026-06-16'
  applied_by: claude-opus-4.7+arxiv-api:evya1
  authoritative_value: 2025
  field: year
  original_manifest_value: 2026
  rationale: manifest year was an estimate from the arXiv submission month (2601 = 2026/01); arXiv <published> reports 2025.
doi: null
final_citation_key: chen2025telemem
intended_use: Memory dimension; long-term + multimodal memory case study.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2601.06037.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2026telemem
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2601.06037.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2601.06037
  method: arxiv_api
  primary_category: cs.CL
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Chen, Chunliang
- Guan, Ming
- Lin, Xiao
- Li, Jiaxu
- Lin, Luxi
- Wang, Qiyi
- Chen, Xiangyu
- Luo, Jixiang
- Sun, Changzhi
- Zhang, Dell
- Li, Xuelong
verified_title: 'TeleMem: Building Long-Term and Multimodal Memory for Agentic AI'
verified_year: 2025
```

```yaml
arxiv_id: '2510.10991'
canonical_url: https://arxiv.org/abs/2510.10991
correction_applied: null
doi: null
final_citation_key: yao2025multimodalsurvey
intended_use: Multimodal reasoning dimension; survey-level background.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2510.10991.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2025multimodalsurvey
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2510.10991.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2510.10991
  method: arxiv_api
  primary_category: cs.CV
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Yao, Huanjin
- Zhang, Ruifei
- Huang, Jiaxing
- Zhang, Jingyi
- Wang, Yibo
- Fang, Bo
- Zhu, Ruolin
- Jing, Yongcheng
- Liu, Shunyu
- Li, Guanbin
- Tao, Dacheng
verified_title: A Survey on Agentic Multimodal Large Language Models
verified_year: 2025
```

```yaml
arxiv_id: '2510.18303'
canonical_url: https://arxiv.org/abs/2510.18303
correction_applied: null
doi: null
final_citation_key: wang2025proactiveretrievalmedical
intended_use: Retrieval + multimodal dimensions; reasoning-with-retrieval case study in the medical domain.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2510.18303.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2025proactiveretrievalmedical
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2510.18303.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2510.18303
  method: arxiv_api
  primary_category: cs.CV
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Wang, Lehan
- Qin, Yi
- Yang, Honglong
- Li, Xiaomeng
verified_title: Proactive Reasoning-with-Retrieval Framework for Medical Multimodal Large Language Models
verified_year: 2025
```

```yaml
arxiv_id: '2510.19361'
canonical_url: https://arxiv.org/abs/2510.19361
correction_applied: null
doi: null
final_citation_key: liu2025agenticmath
intended_use: Reasoning data generation; supports the evaluation / data chapter.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2510.19361.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2025agenticmath
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2510.19361.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2510.19361
  method: arxiv_api
  primary_category: cs.CL
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Liu, Xianyang
- Liu, Yilin
- Wang, Shuai
- Cheng, Hao
- Estornell, Andrew
- Zhao, Yuzhi
- Shu, Jun
- Wei, Jiaheng
verified_title: 'AgenticMath: Enhancing LLM Reasoning via Agentic-based Math Data Generation'
verified_year: 2025
```

```yaml
arxiv_id: '2407.01231'
canonical_url: https://arxiv.org/abs/2407.01231
correction_applied: null
doi: null
final_citation_key: ye2024mirai
intended_use: Evaluation chapter; benchmark for LLM agents on event forecasting.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2407.01231.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2024mirai
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2407.01231.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2407.01231
  method: arxiv_api
  primary_category: cs.CL
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Ye, Chenchen
- Hu, Ziniu
- Deng, Yihe
- Huang, Zijie
- Ma, Mingyu Derek
- Zhu, Yanqiao
- Wang, Wei
verified_title: 'MIRAI: Evaluating LLM Agents for Event Forecasting'
verified_year: 2024
```

```yaml
arxiv_id: '2601.12538'
canonical_url: https://arxiv.org/abs/2601.12538
correction_applied: null
doi: null
final_citation_key: wei2026agenticreasoning
intended_use: Agentic-reasoning core; ties planning, tool use, and memory into a single reasoning loop.
local_archive:
  archive_inspection: metadata_only
  path: data/sources/arxiv/source_zips/2601.12538.zip
  policy_ref: docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)
mismatch_or_rejection_rationale: null
previous_citation_key: tbd2026agenticreasoning
verification:
  authoritative_snapshot: tests/fixtures/arxiv/2601.12538.xml
  authoritative_source: http://export.arxiv.org/api/query?id_list=2601.12538
  method: arxiv_api
  primary_category: cs.AI
  status: verified
  verified_at: '2026-06-15T22:10:40.997179+00:00'
  verified_by: claude-opus-4.7+arxiv-api:evya1
verified_authors:
- Wei, Tianxin
- Li, Ting-Wei
- Liu, Zhining
- Ning, Xuying
- Yang, Ze
- Zou, Jiaru
- Zeng, Zhichen
- Qiu, Ruizhong
- Lin, Xiao
- Fu, Dongqi
- Li, Zihao
- Ai, Mengting
- Zhou, Duo
- Bao, Wenxuan
- Li, Yunzhe
- Li, Gaotang
- Qian, Cheng
- Wang, Yu
- Tang, Xiangru
- Xiao, Yin
- Fang, Liri
- Liu, Hui
- Tang, Xianfeng
- Zhang, Yuji
- Wang, Chi
- You, Jiaxuan
- Ji, Heng
- Tong, Hanghang
- He, Jingrui
verified_title: Agentic Reasoning for Large Language Models
verified_year: 2026
```

<!-- P7I03_SECTION_END -->

## 6. Rejection and replacement

A rejected manifest entry is **not** silently replaced. The procedure
is:

1. Record the rejection here with mismatch evidence, run id, and
   timestamp.
2. Open a follow-up issue describing the rejected source and the
   proposed handling.
3. Update `config/article_sources.yaml` and the canonical ten-source
   citation coverage (`docs/PRD_bibliography_and_citations.md` §10.2)
   only through a reviewed PR.

A rejected entry remains visible in this ledger as historical
evidence; it is **not** removed.

## 7. Re-verification

Verification is idempotent. Re-running over an entry already marked
`verified` must not silently flip its status. If a re-run produces a
material mismatch, that re-run constitutes a rejection event under
§6.

## 8. Cross-references

- `config/article_sources.yaml` — locked source manifest.
- `docs/PRD_bibliography_and_citations.md` §7.1, §7.3, §13.1 —
  binding policy.
- `docs/AI_USAGE.md` — AI-assisted activity log.
- `docs/PROMPTS.md` — prompt registry.
- `latex_project/references.bib` — verified bibliography emission
  target (P7-I04).
- `results/run_logs/source_verification.json` — machine-readable
  mirror (P7-I03).

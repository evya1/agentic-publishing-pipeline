# Retrieval-Augmented Generation

Retrieval-augmented generation grounds language model outputs in external
knowledge by retrieving relevant documents at inference time and conditioning
generation on both the query and the retrieved content. This chapter examines
retrieval architectures designed for agentic settings where queries are complex,
knowledge requirements are heterogeneous, and latency budgets are tight.

## Motivation for Retrieval in Agentic Settings

Parametric knowledge encoded in model weights has two critical limitations for
agentic applications. First, it cannot be updated after training, making it
stale for rapidly evolving domains. Second, it cannot be traced to sources,
making it difficult to verify correctness or explain reasoning chains to users.

Retrieval addresses both limitations. An external knowledge store can be updated
continuously without model retraining. Retrieved passages carry source identifiers
that enable provenance tracking and citation. These properties are especially
valuable in high-stakes domains such as medicine, law, and scientific research,
where factual accuracy and traceability are non-negotiable requirements
\cite{wang2025proactiveretrievalmedical}.

## Retrieval Pipeline Architecture

A typical retrieval pipeline consists of four stages. The first stage encodes
the query using a dense encoder trained to produce embeddings that capture
semantic meaning. The second stage retrieves candidate documents from an indexed
corpus using approximate nearest-neighbor search. The third stage reranks
candidates using a cross-encoder that scores query-document relevance jointly.
The fourth stage integrates retrieved content into the generation context.

Each stage introduces opportunities for error and latency. Dense encoders can
fail on out-of-distribution queries. Approximate nearest-neighbor search can
miss relevant documents. Rerankers can misorder results. Generation can ignore
retrieved content in favor of parametric knowledge. Robust retrieval systems
design around all four failure modes.

## Proactive Retrieval

A limitation of standard retrieval-augmented generation is that it is reactive:
it retrieves documents only when the user explicitly asks a question. Proactive
retrieval systems monitor the conversation context and retrieve documents
preemptively when they detect that forthcoming reasoning will require external
knowledge. This approach reduces latency at query time and enables agents to
reason with relevant context already loaded into working memory.

Medical agentic systems have demonstrated particularly strong results with
proactive retrieval, because clinical reasoning frequently requires background
knowledge about conditions and treatments that the model may not have encountered
during training \cite{wang2025proactiveretrievalmedical}.

## Open Challenges

The retrieval-reasoning interface remains an open problem. Current systems treat
retrieval as a preprocessing step and reasoning as a postprocessing step, with
a clean boundary between them. In practice, reasoning often reveals gaps in
retrieved context that require additional retrieval, and retrieved content often
shifts the direction of reasoning. Tight integration of retrieval and reasoning
within a single iterative loop is an important research frontier.

Evaluation of retrieval-augmented systems is also challenging. Standard
question-answering benchmarks test final answer accuracy but do not measure
whether the system retrieved the right documents or used them correctly.
End-to-end evaluation that measures retrieval quality, reasoning quality, and
answer quality independently is necessary for diagnosing failures and guiding
improvements.

## Indexing at Scale

Production retrieval systems operate over corpora containing millions or
billions of documents. Exact nearest-neighbor search over such corpora is
computationally intractable, making approximate algorithms essential. Hierarchical
navigable small-world graphs and inverted file indexes with product quantization
are the dominant approaches at scale. Both trade a small amount of retrieval
accuracy for dramatic reductions in latency and memory usage.

Incremental indexing is a second scaling challenge. Agentic systems that
learn continuously must update their indexes as new documents arrive without
reindexing the entire corpus. Efficient incremental index updates enable
real-time knowledge integration, which is essential for applications that
require up-to-date information about fast-changing domains.

# Planning and Task Decomposition

Frontier LLMs have demonstrated significant improvements in planning by
decomposing complex goals into executable sub-tasks. This chapter surveys the
planning landscape as of 2025, covering formal objective functions, empirical
benchmark evidence, and the architectural innovations that make hierarchical
task decomposition tractable at scale.

## Formal Objective

Planning in agentic systems can be defined as the problem of selecting a
sequence of actions that maximizes expected cumulative reward given an initial
state and a goal specification. The formal objective function over a horizon
of $T$ steps is central to understanding how modern LLMs approximate planning
through learned heuristics rather than explicit search.

Researchers have shown that models fine-tuned with process-reward signals learn
to produce step-by-step plans that significantly outperform single-shot
chain-of-thought generation on complex multi-hop tasks. The key insight is that
intermediate reasoning steps should themselves be evaluated and rewarded, not
just final answers \cite{correa2025planningperformance}.

## Hierarchical Task Decomposition

The dominant paradigm for planning in large language models is hierarchical task
decomposition. A high-level goal is broken into a tree of sub-tasks, each
delegated to either a specialized subagent or a tool call. The model maintains
a task stack and updates it as subtasks complete or fail. This architecture
closely mirrors classical AI planning systems such as STRIPS and HTN planners,
but replaces manually specified domain models with learned world knowledge.

Empirical results on planning benchmarks such as ALFWorld, AgentBench, and
WebArena consistently show that hierarchical decomposition outperforms flat
single-step generation by wide margins. Models that generate a plan before
executing actions achieve substantially higher task completion rates and produce
fewer irreversible errors.

## Benchmark Evidence

A systematic review of planning benchmarks reveals several robust findings.
First, model scale is a strong predictor of planning ability. GPT-4o, o1-preview,
and Claude 3.5 Sonnet all substantially outperform their smaller predecessors on
multi-step reasoning tasks \cite{wei2026agenticreasoning}.

Second, explicit reasoning traces improve planning accuracy even when the traces
are not optimal. Models trained to produce intermediate steps generalize better
to novel task structures than models trained only on input-output pairs.

Third, the gap between in-context learning and fine-tuning narrows as task
complexity increases. For simple planning tasks, prompting with a few examples
suffices. For complex long-horizon tasks requiring many sequential decisions,
supervised fine-tuning with process rewards is substantially more effective.

## Open Challenges

Despite impressive progress, fundamental challenges remain. Most benchmarks test
planning on short horizons of fewer than twenty steps. Real-world agentic
applications often require hundreds of sequential decisions with irreversible
consequences. Evaluation on longer horizons reveals significant degradation in
plan quality for all current models.

Recovery from plan failures is a second open problem. When a subtask fails,
current agents often repeat the same approach or abandon the goal entirely.
Human planners, by contrast, diagnose the root cause and revise the plan
selectively. Building this diagnostic capability into language model agents
is an active area of research.

## Plan Verification and Validation

Before executing a plan, an agent should verify that the plan is feasible
given the current state and available tools. Plan verification involves
checking that each step has the necessary preconditions satisfied by the
state resulting from the previous step. This static check can catch many
common planning errors before execution begins and avoid wasting computational
resources on plans that are guaranteed to fail.

Dynamic validation during execution checks that each step produces the expected
postconditions before proceeding to the next step. If a postcondition is not
satisfied, the agent pauses and either revises the plan or requests human
intervention. This approach provides a natural checkpoint mechanism that makes
long-horizon plans more robust to partial failures and unexpected environmental
changes.

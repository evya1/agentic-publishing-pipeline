# Evaluation of Agentic AI Systems

Evaluating agentic AI systems is fundamentally harder than evaluating static
language models. Agents act over multiple steps, interact with dynamic
environments, and pursue long-horizon goals. Standard benchmarks designed for
single-turn question answering capture only a small slice of agent capability.
This chapter surveys the methodology for measuring agent performance and
examines the most influential evaluation frameworks developed through 2025.

## Challenges in Agentic Evaluation

Static benchmarks evaluate models on fixed input-output pairs. Agentic
evaluation must assess entire trajectories: sequences of actions, observations,
and intermediate states that may span hundreds of steps. Several properties of
trajectories make evaluation difficult.

First, trajectories are long and expensive to generate. Running a frontier
model for hundreds of steps on a complex task requires substantial computation
and time. Large-scale agentic evaluation demands significant infrastructure
investment.

Second, many agentic tasks have multiple valid solution trajectories. An agent
that reaches the goal by a non-standard route should receive full credit, but
automated evaluation systems often check for specific expected outputs rather
than goal achievement. Designing goal-based evaluation metrics that are robust
to trajectory variation is a key methodological challenge.

Third, agentic tasks often interact with external systems whose state changes
over time, making exact reproducibility impossible. A web browsing agent
evaluated on a live website will encounter different page content on different
evaluation dates. Controlled reproducibility requires either static snapshots
or sandboxed simulation environments.

## The MIRAI Benchmark

MIRAI is a comprehensive benchmark for evaluating agentic reasoning across
multiple capability dimensions \cite{ye2024mirai}. It tests agents on tasks
that require planning, memory, retrieval, tool use, and multimodal perception
in combination. MIRAI tasks are designed to be long-horizon, requiring dozens
of sequential decisions to complete, and to test recovery from intermediate
failures.

The benchmark provides a standardized evaluation harness that sandboxes
agent interactions, records full trajectories for analysis, and computes a
rich set of metrics including task completion rate, step efficiency, error
recovery rate, and reasoning trace quality. Standardized evaluation enables
fair comparison across different agent architectures and model families.

MIRAI results reveal consistent patterns across agent systems. Stronger base
models achieve higher task completion rates. Explicit planning before action
improves step efficiency. External memory stores improve performance on tasks
that require integrating information from earlier in the trajectory. Tool use
is essential for tasks that require precise computation or current information.

## Mathematical Reasoning Evaluation

Mathematical reasoning provides a particularly clean evaluation setting because
problems have unambiguous correct answers that can be verified automatically.
Agentic mathematical reasoning benchmarks test agents on competition problems
that require multiple steps of algebraic manipulation, geometric reasoning, or
combinatorial enumeration \cite{liu2025agenticmath}.

Performance on mathematical benchmarks correlates strongly with general agentic
capability, making these benchmarks useful proxies for overall agent quality.
Models that achieve high mathematical reasoning scores also tend to achieve
high scores on planning, retrieval, and tool-use benchmarks.

## Open Problems in Evaluation Methodology

Several important methodological gaps remain. Most benchmarks test single-agent
systems. Multi-agent systems where several specialized agents collaborate on a
shared task require new evaluation frameworks that measure coordination quality
in addition to task outcome. Developing multi-agent evaluation infrastructure
is an important direction for future work.

Evaluation of safety and alignment properties is also underdeveloped. Most
current benchmarks measure task performance but not safety. Agents that achieve
high task performance by taking risky or unethical actions should not be
considered high-quality systems. Developing evaluation frameworks that jointly
measure performance and safety is an urgent research priority.

## Human Evaluation Protocols

Automated metrics are necessary for scalable evaluation but insufficient on
their own. Human evaluation provides ground truth for tasks where automated
metrics disagree with human judgment. Well-designed human evaluation protocols
specify rating rubrics, annotator training procedures, and inter-annotator
agreement targets. Agreement statistics such as Cohen's kappa or Krippendorff's
alpha should be reported alongside task performance scores to characterize
evaluation reliability. Combining automated and human evaluation provides the
most complete picture of agent capability.

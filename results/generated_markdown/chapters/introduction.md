# Introduction to Agentic AI Systems

Large language models have evolved from static text predictors into active
participants in complex, multi-step workflows. This transformation, driven by
improvements in reasoning, tool integration, and memory, marks the beginning of
the agentic era in artificial intelligence. An agentic system acts autonomously
within an environment, perceives observations, selects actions, and pursues
long-horizon goals with minimal human intervention \cite{ke2025reasoningfrontiers}.

## Motivation

The promise of agentic AI is profound. Where conventional language models
respond to isolated prompts, agentic systems maintain state across many
interactions, delegate subtasks to specialized tools, and recover from failures
through iterative self-correction. These capabilities unlock applications ranging
from scientific literature review to autonomous software engineering and clinical
decision support.

The research community has responded with a surge of frameworks, benchmarks, and
theoretical analyses. Yet the field remains fragmented. Different groups use
inconsistent definitions of agency, measure performance on incomparable tasks,
and report results under non-reproducible conditions. This survey aims to
consolidate findings from the most influential work published through 2025 and to
present a unified view of the landscape \cite{wei2026agenticreasoning}.

## Scope and Contributions

This document surveys four interconnected dimensions of agentic AI: planning
and task decomposition, memory and state persistence, retrieval-augmented
generation, tool use, multimodal perception, and systematic evaluation.

For each dimension we ask three questions. First, what is the theoretical
basis that makes the capability possible? Second, what empirical evidence
demonstrates that frontier models have acquired that capability? Third, what
open challenges remain and which research directions appear most promising?

## Overview in Hebrew

מערכות בינה מלאכותית אגנטיות מייצגות שינוי פרדיגמה יסודי. במקום להגיב לשאלות
בודדות, מודלים אלה תכננים ומבצעים רצפי פעולות מורכבים. יכולות
ה-\textenglish{planning}, הזיכרון, והשימוש בכלים הופכות אותם לשותפים
אמיתיים בפתרון בעיות מורכבות. מחקרים עדכניים כמו \cite{ke2025reasoningfrontiers}
מצביעים על שיפורים משמעותיים ביכולות ה-\textenglish{reasoning} של מודלים אלה.

## Chapter Outline

The remainder of this document is organized as follows. The planning chapter
presents formal models of goal-directed reasoning and surveys benchmark evidence.
The memory chapter examines how agents maintain and retrieve context across
extended interactions. The retrieval chapter covers techniques for grounding
generation in external knowledge. The tool-use chapter analyzes how agents
interface with APIs, code executors, and web browsers. The multimodal chapter
surveys visual and audio inputs that broaden agent perception. The evaluation
chapter synthesizes methodology for measuring agent capability. The conclusion
identifies open problems and future research directions.

Each chapter is self-contained and may be read independently. Cross-references
connect related ideas and allow readers to trace concepts across capability
dimensions. The bibliography lists all cited works with arXiv identifiers for
accessibility.

This survey is intended for researchers entering the agentic AI field,
practitioners designing production systems, and engineers building evaluation
infrastructure. We assume familiarity with transformer architectures and
basic reinforcement learning but not with the specific frontier models or
benchmarks discussed.

## Terminology and Notation

Throughout this survey we use the term **agent** to refer to a system that
takes actions in an environment with the goal of maximizing a reward or
achieving a specified objective. A **frontier model** refers to a large
language model at or near the current state of the art in terms of benchmark
performance. A **trajectory** is a sequence of observations, actions, and
intermediate states produced by an agent during a single task episode.

We use **tool** to refer to any external function that an agent can invoke,
including code executors, search APIs, web browsers, and database clients.
A **workflow** is a predefined sequence of agent calls designed to accomplish
a specific class of tasks. We distinguish workflows from fully autonomous
agent behavior, in which the agent itself decides which actions to take without
following a predefined script.

Mathematical notation follows standard reinforcement learning conventions
where applicable. Deviations from convention are noted inline at the point
of first use. A full nomenclature table is provided in the back matter.

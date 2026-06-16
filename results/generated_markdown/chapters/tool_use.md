# Tool Use and External Action

Tool use is the mechanism by which language model agents extend their
capabilities beyond pure text generation. By calling external APIs, executing
code, querying databases, and browsing the web, agents can perform actions with
real-world consequences. This chapter surveys the design space of tool-using
agents and the empirical evidence on their performance across diverse tasks.

## Tool Call Formalism

A tool call is a structured output produced by a language model that specifies
a function name and a set of typed arguments. The runtime environment executes
the function and returns a result that the model can incorporate into subsequent
reasoning. This simple interface enables language models to interact with
arbitrary external systems without requiring changes to the model itself.

The tool call formalism was popularized by OpenAI function calling and has since
been adopted across all major frontier model providers. Standardization of the
interface has enabled the development of reusable tool libraries that can be
plugged into any compliant agent framework. This ecosystem effect has
dramatically accelerated the development of capable tool-using agents
\cite{wu2025agenticreasoningtools}.

## Code Execution as a Tool

Code execution is among the most powerful tools available to language model
agents. A code-executing agent can solve mathematical problems, analyze data,
generate and test hypotheses, and build software components by writing and running
Python or other languages within a sandboxed environment.

Mathematical reasoning is a domain where code execution tools provide dramatic
performance improvements. Models that can write and execute code to verify
algebraic manipulations, enumerate cases, and test conjectures achieve near-human
performance on competition mathematics benchmarks \cite{liu2025agenticmath}.
Without code execution, even the largest language models make algebraic errors
that cascade into incorrect final answers.

## Web Browsing Agents

Web browsing agents interact with live websites through a browser automation
interface. They can navigate pages, fill forms, click buttons, and extract
structured information from dynamically rendered content. These capabilities
make web browsing agents useful for tasks that require current information or
interaction with systems that lack programmatic APIs.

The primary challenges for web browsing agents are reliability and robustness.
Websites change their layout and content frequently, breaking navigation scripts
that worked previously. Agents must adapt to unexpected page structures,
handle CAPTCHAs and authentication flows, and recover from navigation errors.
Robust web agents use visual perception to understand page layout rather than
relying on fragile DOM selectors.

## Tool Selection and Composition

When many tools are available, agents must select the right tool for each step
and compose multiple tools to accomplish complex goals. Tool selection is
nontrivial: different tools may be applicable to the same subtask with different
trade-offs in latency, cost, and reliability.

Research on tool selection shows that models benefit from tool documentation that
clearly describes preconditions, postconditions, and failure modes. Agents
provided with rich tool documentation make fewer selection errors and recover
more successfully from tool failures than agents provided with minimal signatures.

## Open Challenges

Safety is a paramount concern for tool-using agents. An agent that can write
to databases, send emails, and execute code can cause irreversible harm through
errors or adversarial manipulation. Research on safe tool use explores constrained
execution environments, permission systems, and human-in-the-loop approval
workflows that limit the blast radius of agent errors.

## Tool Discovery and Learning

Static tool libraries require developers to manually curate and document all
tools an agent may need. Dynamic tool discovery allows agents to search for and
learn to use new tools at runtime. This capability is important for agents that
must operate in open-ended environments where the set of available tools is
not known in advance.

Tool learning research investigates how agents can generalize from documented
tools to undocumented or partially documented ones by analogy and exploration.
Agents that can read API documentation and infer correct usage patterns from
a few examples are substantially more flexible than agents that can only use
tools they were explicitly trained on. This flexibility is a key enabler for
deploying agents in enterprise environments with proprietary tooling.

# tasks/

> **Status:** scaffold only — no CrewAI tasks defined yet.

Future home of CrewAI task definitions. Each task will declare:

- `description`
- `expected_output`
- `agent`
- `context` (the earlier tasks it depends on)

Planned task sequence:

```
Research -> Writing -> Review -> Markdown assembly
  -> LaTeX generation -> PDF validation
```

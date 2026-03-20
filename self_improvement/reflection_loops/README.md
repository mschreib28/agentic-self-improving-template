# Reflection Loops (Tier 1)

## What This Is

A reflection loop is a step inserted between task execution and completion signaling. The agent evaluates its own output against the task requirements, identifies gaps, and optionally revises before emitting `done`.

This is the simplest and highest-ROI self-improvement pattern. It requires no additional infrastructure — just an extra prompt call.

## Pattern

```
Execute task
     │
     ▼
Generate output
     │
     ▼
Run critic prompt on own output ◄─── critic_prompt.md
     │
     ├─ Output is good → emit `done`
     ├─ Output has fixable issues → revise once → emit `done`
     └─ Output has fundamental issues → emit `needs-review`
```

## Files in This Directory

| File | Purpose |
|---|---|
| `critic_prompt.md` | Template prompt for self-critique, parameterized by department |
| `reflection_loop.py` | Python stub showing how to wire a reflection loop into an agent |

## How to Use

1. Copy `critic_prompt.md` and customize for your department.
2. Insert the reflection loop into your agent's execution flow (see `reflection_loop.py`).
3. The agent should run the critic prompt on its output before emitting a completion signal.
4. Log the reflection result as part of the episode (see `docs/logging_and_episodes.md`).

## Design Decisions

- **One revision max** — to prevent infinite loops, agents revise at most once. If the revision still doesn't pass critique, signal `needs-review`.
- **Critic sees the original task** — the critic prompt receives both the task description and the output, so it can check alignment.
- **Department-specific criteria** — each department should customize the critic prompt with domain-relevant checks.

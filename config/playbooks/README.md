# Config: Playbooks

Per-department playbook files — the **long-term declarative memory** of each department head agent.

## What Lives Here

One `{department}_playbook.md` per department. Each file contains learned guidelines derived from past episodes by the Tier 3 meta-agent.

## How It Works

```
Tier 3 meta-agent analyzes scored episodes
        │
        ▼
Derives guidelines (what worked, what didn't)
        │
        ▼
Appends rules to {department}_playbook.md
        │
        ▼
Next invocation: department head reads playbook as context
```

## Conventions

- **One file per department**: `build_playbook.md`, `growth_playbook.md`, `research_playbook.md`, etc.
- **Append-only by default**: the meta-agent adds rules; it does not edit or remove them.
- **Superseded rules** are moved to the "Archived" section at the bottom, never deleted.
- **Each rule includes**: the rule statement, evidence (episode ID + metrics), confidence level, and date.
- **Human overrides** are allowed — just add a comment explaining why you're overriding.

## How Agents Use These Files

Department heads load their playbook file as part of their context stack (see `architecture/SYSTEM_DESIGN.md`, "Agent Context Assembly"):

1. System prompt (identity)
2. **Playbook (this file)** — long-term learned knowledge
3. Recent episodes — short-term episodic memory
4. Task assignment — current work

## Creating a New Playbook

Copy the template from `AGENTS.md` (see "Department Playbook Convention") or use `examples/growth_agent/growth_playbook.md` as a reference.

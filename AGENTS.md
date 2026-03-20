# AGENTS.md — Agent Team Structure and Protocols

This document defines the agent hierarchy, responsibilities, communication protocols, and the Completion Signal Standard used across the system.

## Team Org Chart

```
                         ┌─────────────┐
                         │   Foreman   │
                         │    (R2)     │
                         └──────┬──────┘
                                │
        ┌───────┬───────┬───────┼───────┬───────┬───────┬───────┬───────┐
        │       │       │       │       │       │       │       │       │
   ┌────┴──┐ ┌──┴───┐ ┌┴────┐ ┌┴────┐ ┌┴───┐ ┌┴─────┐ ┌┴──────┐ ┌┴──────┐
   │Research│ │Archi-│ │Build│ │De-  │ │ QA │ │Growth│ │Report-│ │PM-    │
   │  Head  │ │tect  │ │Head │ │sign │ │Head│ │ Head │ │  er   │ │ Sync  │
   └────┬───┘ └──┬───┘ └┬────┘ └┬────┘ └┬───┘ └┬─────┘ └┬──────┘ └┬──────┘
        │        │      │       │       │      │        │         │
     sub-agents  ...   ...    ...     ...    ...      ...       ...
```

## Role Definitions

### Foreman (R2)

| Field | Value |
|---|---|
| **Responsibilities** | Receives high-level objectives. Decomposes into department-level tasks. Manages cross-department dependencies. Resolves escalations. |
| **Tools** | Task queue, department spawn API, episode log reader, policy reader |
| **Can spawn** | Any department head |
| **Escalation** | Escalates to human operator if blocked for > N cycles or if a policy update is proposed |

### Department Heads

Each department head follows the same interface but with domain-specific prompts and tools.

| Department | Responsibilities | Tools | Can Spawn | Escalation Target |
|---|---|---|---|---|
| **Research** | Gather information, synthesize findings, produce briefs | Web search, document reader, summarizer | Research sub-agents | Foreman |
| **Architect** | Design system components, define interfaces, review technical decisions | Diagramming, schema validators, code reader | Architecture sub-agents | Foreman |
| **Build** | Write code, run tests, fix bugs | Code editor, test runner, linter, build tools | Build sub-agents, QA handoff | Foreman |
| **Design** | Create UX flows, wireframes, design specs | Design tools, component library, style guide reader | Design sub-agents | Foreman |
| **QA** | Test features, validate acceptance criteria, report defects | Test runner, browser automation, log reader | QA sub-agents | Foreman |
| **Growth** | Run content experiments, optimize conversion, track campaign metrics | Analytics API, content generator, A/B test tools | Growth sub-agents | Foreman |
| **Reporter** | Generate status reports, dashboards, summaries | Log reader, metrics aggregator, template renderer | Reporter sub-agents | Foreman |
| **PM-Sync** | Sync with external project management tools, maintain task status | PM tool API (Jira, Linear, etc.), calendar, notification tools | None | Foreman |

### Sub-Agents

Sub-agents are spawned by department heads for focused, single-responsibility tasks. They:

- Receive a scoped task description and context from their department head.
- Execute the task using their permitted tool set.
- Return a result with a completion signal.
- Do **not** spawn other agents (leaf nodes in the hierarchy).

## Completion Signal Standard

Every agent, upon finishing a unit of work, emits one of three signals:

| Signal | Meaning | Who Handles It |
|---|---|---|
| `done` | Task completed successfully. Output is attached. | Parent agent consumes the result and continues. |
| `blocked` | Cannot proceed. Reason and context are attached. | Parent agent attempts to resolve or escalates to Foreman. |
| `needs-review` | Output is ready but requires human or peer review before proceeding. | Parent agent routes to the appropriate reviewer (human or QA agent). |

### Signal Schema

```json
{
  "signal": "done | blocked | needs-review",
  "agent_id": "build-sub-003",
  "task_id": "TASK-1234",
  "parent_id": "build-head",
  "timestamp": "2025-01-15T10:32:00Z",
  "payload": {
    "summary": "Short description of what was done or why it's blocked.",
    "artifacts": ["path/to/output"],
    "blockers": [],
    "review_notes": ""
  }
}
```

### Signal Flow

```
Sub-agent completes work
        │
        ▼
  Emit signal ──────────────────────────────┐
        │                                   │
   ┌────┴────┐                              │
   │  done   │──► Parent consumes result    │
   └─────────┘                              │
   ┌─────────┐                              │
   │ blocked  │──► Parent attempts fix ─────┤
   └─────────┘    or escalates to Foreman   │
   ┌─────────────┐                          │
   │ needs-review │──► Route to reviewer ───┘
   └─────────────┘    (human or QA agent)
```

## Spawning Rules

See [`config/policies/spawn_rules.yaml`](config/policies/spawn_rules.yaml) for the machine-readable version.

Core rules:
1. Only the Foreman can spawn department heads.
2. Department heads can spawn sub-agents within their own department.
3. Cross-department work requires Foreman coordination (e.g., Build requesting QA).
4. Sub-agents cannot spawn other agents.
5. Maximum concurrent sub-agents per department: configurable (default 3).

## Escalation Rules

See [`config/policies/escalation_rules.yaml`](config/policies/escalation_rules.yaml) for the machine-readable version.

| Condition | Action |
|---|---|
| Sub-agent blocked for > 2 attempts | Escalate to department head |
| Department head blocked for > 1 cycle | Escalate to Foreman |
| Foreman blocked | Escalate to human operator |
| Any agent proposes a policy change | Route to human review |
| Quality score < threshold for 3 consecutive episodes | Flag for review |

## How to Map Your Current Setup

If you already have a multi-agent system running, use this section to plug it in.

### 1. Identify Your Agents

Fill in this table with your actual agent names and IDs. Not every row needs to be filled — delete departments you don't have, add ones you do.

| Template Role | Your Agent Name / ID | Framework / Runtime | Notes |
|---|---|---|---|
| Foreman (R2) | **\[Your orchestrator name\]** | **\[e.g., CrewAI, LangGraph, custom\]** | |
| Research Head | **\[Your agent or "N/A"\]** | | |
| Architect Head | **\[Your agent or "N/A"\]** | | |
| Build Head | **\[Your agent or "N/A"\]** | | |
| Design Head | **\[Your agent or "N/A"\]** | | |
| QA Head | **\[Your agent or "N/A"\]** | | |
| Growth Head | **\[Your agent or "N/A"\]** | | |
| Reporter Head | **\[Your agent or "N/A"\]** | | |
| PM-Sync Head | **\[Your agent or "N/A"\]** | | |
| **\[Your custom dept\]** | **\[Your agent\]** | | |

### 2. Update Policies

Once the table above is filled in, propagate those names into:

- `config/policies/spawn_rules.yaml` — replace template agent IDs with yours.
- `config/policies/escalation_rules.yaml` — adjust thresholds for your system's cadence.

### 3. Copy Prompts

For each department you're using, copy `config/prompts/department_head.md` to a department-specific file (e.g., `config/prompts/build.md`) and fill in the `{{template}}` variables with your actual tools and quality criteria.

### 4. Start Small

Pick one department — ideally the one producing the most output — and wire in Tier 1 reflection first. See [`docs/getting_started.md`](docs/getting_started.md) for the step-by-step.

## Adding a New Department

1. Add a row to the Department Heads table above.
2. Create a system prompt in `config/prompts/`.
3. Add spawn and escalation entries in `config/policies/`.
4. Create an evaluation rubric in `self_improvement/evaluation/`.
5. Optionally add an example under `examples/`.

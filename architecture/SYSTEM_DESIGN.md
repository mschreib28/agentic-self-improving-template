# System Design

## Overview

The system is a hierarchical multi-agent architecture with a single orchestrator (Foreman), domain-specialized department heads, and task-specific sub-agents. A parallel self-improvement subsystem observes, evaluates, and proposes changes to the operational system.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OPERATIONAL LAYER                            │
│                                                                     │
│  ┌───────────┐     ┌──────────────┐     ┌──────────────┐          │
│  │  Foreman  │────►│ Dept. Heads  │────►│  Sub-Agents  │          │
│  │  (R2)     │◄────│ (8 depts)    │◄────│  (N per dept)│          │
│  └─────┬─────┘     └──────┬───────┘     └──────────────┘          │
│        │                  │                                         │
│        │    Completion Signals (done / blocked / needs-review)      │
│        │                  │                                         │
└────────┼──────────────────┼─────────────────────────────────────────┘
         │                  │
         ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       OBSERVABILITY LAYER                           │
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐       │
│  │ Episode Log  │   │   Metrics    │   │  Signal Tracker  │       │
│  │  (.jsonl)    │   │  Aggregator  │   │                  │       │
│  └──────┬───────┘   └──────┬───────┘   └────────┬─────────┘       │
│         │                  │                     │                  │
└─────────┼──────────────────┼─────────────────────┼──────────────────┘
          │                  │                     │
          ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SELF-IMPROVEMENT LAYER                           │
│                                                                     │
│  ┌────────────┐   ┌────────────────┐   ┌──────────────────┐       │
│  │ Reflection │   │   Evaluator    │   │   Meta-Agent     │       │
│  │   Loops    │   │  (Rubric-based)│   │ (Policy Updates) │       │
│  │  (Tier 1)  │   │   (Tier 2)    │   │    (Tier 3)      │       │
│  └────────────┘   └────────────────┘   └────────┬─────────┘       │
│                                                  │                  │
│                                         ┌────────▼─────────┐       │
│                                         │  Human Review    │       │
│                                         │  Gate            │       │
│                                         └──────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Operational Layer

| Component | Responsibility | State |
|---|---|---|
| **Foreman** | Receives objectives, decomposes into department tasks, manages dependencies, resolves escalations | Reads `GOALS.md`, `config/policies/` |
| **Department Heads** | Receive department-scoped tasks, spawn sub-agents, aggregate results, run reflection loops | Read their role prompt from `config/prompts/`, their rubric from `self_improvement/evaluation/` |
| **Sub-Agents** | Execute single-responsibility tasks, return results with completion signals | Stateless — receive context, produce output |

### Observability Layer

| Component | Responsibility | Storage |
|---|---|---|
| **Episode Log** | Append-only record of every task execution | `.jsonl` files, one per day or per department |
| **Metrics Aggregator** | Computes rolling quality scores, completion rates, escalation rates | In-memory or time-series DB |
| **Signal Tracker** | Monitors completion signal flow, detects stuck agents, tracks cycle counts | Event stream or queue |

### Self-Improvement Layer

| Component | Responsibility | Trigger |
|---|---|---|
| **Reflection Loops** (Tier 1) | Agent self-critiques output before marking `done` | Every task completion |
| **Evaluator** (Tier 2) | Scores completed episodes against department rubrics | After episode is logged |
| **Meta-Agent** (Tier 3) | Reviews scored episodes, proposes prompt/policy changes | Periodic (e.g., daily or after N episodes) |
| **Human Review Gate** | Approves or rejects proposed policy changes | On every Tier 3 proposal |

## Data Flow

### Task Lifecycle

```
1. Objective arrives (human or upstream system)
       │
2. Foreman decomposes into department tasks
       │
3. Department head receives task
       │
4. Department head spawns sub-agent(s)
       │
5. Sub-agent executes, runs reflection loop (Tier 1)
       │
6. Sub-agent emits completion signal
       │
7. Department head aggregates results
       │
8. Episode is logged (Observability Layer)
       │
9. Evaluator scores episode (Tier 2)
       │
10. Meta-agent reviews scored episodes periodically (Tier 3)
       │
11. Proposed changes go through human review gate
```

### Episode Data Model

Each episode captures the full context of a task execution:

```json
{
  "episode_id": "ep-20250115-001",
  "task_id": "TASK-1234",
  "department": "build",
  "agent_id": "build-sub-003",
  "timestamp_start": "2025-01-15T10:30:00Z",
  "timestamp_end": "2025-01-15T10:32:00Z",
  "task_description": "Implement pagination for /api/users endpoint",
  "context": { "relevant_files": ["src/api/users.ts"], "prior_attempts": 0 },
  "actions": [
    { "step": 1, "action": "read_file", "target": "src/api/users.ts" },
    { "step": 2, "action": "edit_file", "target": "src/api/users.ts", "summary": "Added offset/limit params" },
    { "step": 3, "action": "run_tests", "result": "12 passed, 0 failed" }
  ],
  "result": { "signal": "done", "artifacts": ["src/api/users.ts"] },
  "reflection": { "self_score": 4, "self_notes": "Clean implementation, but no edge case tests for limit=0" },
  "evaluation": { "rubric_version": "build-v3", "score": 3.8, "feedback": "Missing edge case coverage" },
  "human_feedback": null
}
```

## Communication Protocols

### Inter-Agent Messages

Agents communicate via structured messages, not free-form text:

```json
{
  "from": "foreman",
  "to": "build-head",
  "type": "task_assignment",
  "task_id": "TASK-1234",
  "payload": {
    "description": "...",
    "context": {},
    "constraints": { "max_cycles": 5, "deadline": "2025-01-15T12:00:00Z" },
    "priority": "high"
  }
}
```

### State Machine per Agent

```
IDLE ──► ASSIGNED ──► EXECUTING ──► REFLECTING ──► SIGNALING
  ▲                                                    │
  └────────────────────────────────────────────────────┘
```

Each agent transitions through these states. The `REFLECTING` state is where Tier 1 self-improvement happens — the agent critiques its own output before emitting a completion signal.

## Scaling Considerations

- **Horizontal**: Each department can run independently. Adding departments doesn't affect existing ones.
- **Vertical**: Sub-agent concurrency per department is configurable via `config/policies/spawn_rules.yaml`.
- **Storage**: Episode logs grow linearly. Implement rotation or archival for production use.
- **Cost**: Track LLM calls per episode. Set budgets via `max_cycles` in task assignments.

# Workflows

## The Core Loop: Plan → Execute → Evaluate → Improve

Every unit of work in the system follows this four-phase loop. The loop operates at multiple levels — individual tasks, department-level batches, and system-wide improvement cycles.

```
    ┌──────────┐
    │   PLAN   │  Decompose objective into tasks, assign to agents
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │ EXECUTE  │  Agents perform work, emit completion signals
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │ EVALUATE │  Score results against rubrics, log episodes
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │ IMPROVE  │  Reflect, propose changes, apply (with review)
    └────┬─────┘
         │
         └──────► Back to PLAN (next cycle)
```

## Workflow Levels

### Level 1: Task Workflow (Sub-Agent)

The innermost loop. A single sub-agent working on a single task.

```
Input: Task assignment from department head
  │
  ├─► 1. Parse task description and constraints
  ├─► 2. Gather context (read files, query APIs)
  ├─► 3. Execute core action (write code, generate content, run analysis)
  ├─► 4. Self-reflect (Tier 1): "Did I meet the requirements?"
  │       ├─ Yes → emit `done`
  │       ├─ Partially → revise once, then emit `done` or `needs-review`
  │       └─ No / stuck → emit `blocked` with context
  └─► 5. Log episode
```

**Cycle budget**: Typically 3-8 LLM calls. Configurable per task type.

### Level 2: Department Workflow (Department Head)

A department head managing a batch of related tasks.

```
Input: Department-scoped objective from Foreman
  │
  ├─► 1. PLAN: Break objective into sub-tasks
  ├─► 2. EXECUTE: Spawn sub-agents, monitor signals
  │       ├─ On `done` → collect result
  │       ├─ On `blocked` → attempt fix or escalate
  │       └─ On `needs-review` → route to reviewer
  ├─► 3. EVALUATE: Run department rubric on completed episodes
  │       └─ Log aggregated quality score
  ├─► 4. IMPROVE: Review patterns in recent episodes
  │       └─ If quality trend is declining → flag for meta-agent
  └─► 5. Report results to Foreman
```

### Level 3: System Workflow (Foreman)

The Foreman orchestrating across departments.

```
Input: High-level objective (from human or upstream system)
  │
  ├─► 1. PLAN: Decompose into department-level tasks
  │       └─ Identify cross-department dependencies
  ├─► 2. EXECUTE: Assign to department heads, manage order
  │       ├─ Parallel: Independent departments work concurrently
  │       └─ Sequential: Dependent tasks wait for predecessors
  ├─► 3. EVALUATE: Check system-level metrics (GOALS.md Section 3)
  │       ├─ Task completion rate
  │       ├─ Escalation rate
  │       └─ Mean cycles to completion
  ├─► 4. IMPROVE: Trigger meta-agent review if thresholds are breached
  └─► 5. Report to human operator
```

### Level 4: Improvement Workflow (Meta-Agent)

The meta-agent operates on a slower cadence — daily or after N episodes.

```
Input: Batch of scored episodes + current policies/prompts
  │
  ├─► 1. ANALYZE: Identify patterns in low-scoring episodes
  │       ├─ Common failure modes per department
  │       ├─ Recurring blockers
  │       └─ Unused or misused tools
  ├─► 2. PROPOSE: Draft changes to prompts or policies
  │       ├─ Prompt edits (add clarifications, examples)
  │       ├─ Policy changes (adjust spawn limits, escalation thresholds)
  │       └─ Rubric updates (refine scoring criteria)
  ├─► 3. VALIDATE: Check proposed changes against constraints
  │       ├─ No removal of safety guardrails
  │       ├─ Changes are backward-compatible
  │       └─ Diff is human-readable
  ├─► 4. SUBMIT: Create a policy update proposal for human review
  └─► 5. APPLY: If approved, update versioned config files
```

## Cross-Department Workflow Example

A realistic sequence for a feature build:

```
Foreman receives: "Build and ship user profile editing feature"
  │
  ├─► 1. Foreman assigns to Architect: "Design the profile editing API and UI flow"
  │       └─ Architect produces: API spec + UI wireframe description
  │
  ├─► 2. Foreman assigns to Build (depends on step 1):
  │       "Implement the profile editing API per this spec"
  │       └─ Build produces: Code + tests
  │
  ├─► 3. Foreman assigns to Design (parallel with step 2):
  │       "Create profile editing UI components"
  │       └─ Design produces: Component specs
  │
  ├─► 4. Foreman assigns to QA (depends on steps 2 + 3):
  │       "Test profile editing feature end-to-end"
  │       └─ QA produces: Test results, defect list
  │
  ├─► 5. If defects found → Foreman routes back to Build with QA feedback
  │
  └─► 6. Foreman assigns to Reporter: "Summarize feature completion status"
```

## Failure Handling

| Failure Type | Detection | Response |
|---|---|---|
| Sub-agent stuck in loop | Cycle count exceeds budget | Force `blocked` signal, escalate |
| Department head can't resolve blocker | Repeated `blocked` from sub-agents | Escalate to Foreman |
| Cross-department dependency deadlock | Both departments waiting on each other | Foreman detects cycle, breaks it by re-sequencing |
| Quality score below threshold | Evaluator flags low score | Route to human review, pause auto-approval |
| Meta-agent proposes unsafe change | Validation check fails | Reject proposal, log reason |

## Workflow Configuration

Workflows are configured via `config/policies/` YAML files:

- `spawn_rules.yaml` — who can spawn whom, concurrency limits
- `escalation_rules.yaml` — when and how to escalate

Task-level parameters are set in the task assignment message:

```yaml
max_cycles: 5
deadline: "2025-01-15T12:00:00Z"
priority: high
allow_revision: true
revision_limit: 1
```

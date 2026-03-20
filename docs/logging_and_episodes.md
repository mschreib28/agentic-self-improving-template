# Logging and Episodes

## What Is an Episode?

An **episode** is a complete record of one task execution: what was assigned, what the agent did, what it produced, and how it was scored. Episodes are the foundation of the self-improvement system — without them, evaluation and policy adaptation have no data to work with.

## Storage Format

Episodes are stored as **JSONL** (JSON Lines) — one JSON object per line, one file per department per day.

```
logs/
  episodes/
    build/
      2025-01-15.jsonl
      2025-01-16.jsonl
    growth/
      2025-01-15.jsonl
    ...
```

Why JSONL:
- Append-friendly (no need to read/parse the whole file to add an entry).
- Line-oriented (easy to grep, tail, stream).
- Standard tooling (jq, Python json module, pandas).

## Episode Schema

See `self_improvement/evaluation/episode_schema.yaml` for the full schema. Here's the minimum viable episode:

```json
{
  "episode_id": "ep-20250115-001",
  "task_id": "TASK-1234",
  "department": "build",
  "agent_id": "build-sub-003",
  "prompt_version": "1.2",
  "timestamp_start": "2025-01-15T10:30:00Z",
  "timestamp_end": "2025-01-15T10:32:00Z",
  "task_description": "Implement pagination for /api/users endpoint",
  "actions": [
    { "step": 1, "action": "read_file", "target": "src/api/users.ts" },
    { "step": 2, "action": "edit_file", "target": "src/api/users.ts", "summary": "Added offset/limit params" },
    { "step": 3, "action": "run_tests", "result": "12 passed, 0 failed" }
  ],
  "result": {
    "signal": "done",
    "artifacts": ["src/api/users.ts"],
    "summary": "Implemented offset/limit pagination"
  }
}
```

## Progressive Detail Levels

Start minimal and add fields as you enable higher tiers:

### Level 1: Basic (start here)

Required for any self-improvement:

```json
{
  "episode_id": "...",
  "task_id": "...",
  "department": "...",
  "agent_id": "...",
  "prompt_version": "1.0",
  "timestamp_start": "...",
  "timestamp_end": "...",
  "task_description": "...",
  "result": { "signal": "done | blocked | needs-review" }
}
```

`prompt_version` is technically optional but **strongly recommended from day one** — it costs nothing to log and becomes essential once you start iterating on prompts. Without it you can't tell whether a quality change came from a prompt update or something else.

### Level 2: With Actions

Adds visibility into what the agent actually did:

```json
{
  "...": "...level 1 fields...",
  "playbook_hash": "a3f8c91d",
  "actions": [
    { "step": 1, "action": "...", "target": "...", "summary": "..." }
  ],
  "llm_calls": 4,
  "cost_usd": 0.03
}
```

`playbook_hash` is a short hash of the department playbook file at execution time. Lets you correlate whether having a newer playbook improved quality.

### Level 3: With Reflection (Tier 1)

Adds the agent's self-critique:

```json
{
  "...": "...level 2 fields...",
  "reflection": {
    "verdict": "pass",
    "score": 4,
    "issues": [],
    "summary": "Output meets requirements"
  }
}
```

### Level 4: With Evaluation (Tier 2)

Adds the external rubric-based score:

```json
{
  "...": "...level 3 fields...",
  "evaluation": {
    "rubric_version": "build-v3",
    "weighted_score": 4.2,
    "scores": {
      "correctness": { "score": 5, "reasoning": "..." },
      "test_coverage": { "score": 4, "reasoning": "..." }
    },
    "recommendation": "approve"
  }
}
```

### Level 5: With Human Feedback

Adds human review data:

```json
{
  "...": "...level 4 fields...",
  "human_feedback": {
    "reviewer": "alice",
    "score": 4,
    "notes": "Good implementation, minor style nits",
    "timestamp": "2025-01-15T11:00:00Z"
  }
}
```

## Episode ID Convention

Format: `ep-{YYYYMMDD}-{sequence}`

- `ep-20250115-001` — first episode on Jan 15, 2025
- `ep-20250115-042` — 42nd episode that day

Sequence numbers are per-department, per-day. Generate them with a simple counter or use UUIDs if coordination is hard.

## Querying Episodes

Common queries you'll want to support:

| Query | Method |
|---|---|
| All episodes for a department today | Read the day's `.jsonl` file |
| Low-scoring episodes | Filter by `evaluation.weighted_score < 3.0` |
| Episodes with a specific failure pattern | Grep `actions` or `reflection.issues` |
| Average score trend | Aggregate `evaluation.weighted_score` over time |
| Cost per department | Sum `cost_usd` grouped by `department` |
| Score delta after prompt change | Compare scores before/after a `prompt_version` bump |
| Playbook effectiveness | Compare scores for episodes with vs. without playbook context |

With `jq`:

```bash
# All low-scoring build episodes today
cat logs/episodes/build/2025-01-15.jsonl | jq 'select(.evaluation.weighted_score < 3.0)'

# Average score for growth this week
cat logs/episodes/growth/2025-01-1*.jsonl | jq '.evaluation.weighted_score' | awk '{sum+=$1; n++} END {print sum/n}'

# Average score by prompt version (did the prompt update help?)
cat logs/episodes/build/*.jsonl | jq -r '[.prompt_version, .evaluation.weighted_score] | @csv' | sort
```

## Retention and Archival

- **Active window**: Keep 30 days of episodes in the hot path.
- **Archive**: Move older episodes to cold storage (S3, GCS, etc.).
- **Aggregates**: Compute daily/weekly summaries and keep those permanently.
- **Privacy**: If episodes contain user data, apply your data retention policies.

## Implementation Tips

- Use a simple append function that serializes to JSON and writes a line to the file.
- Buffer writes if you're producing many episodes per second (unlikely for most agent systems).
- Add a `flush` call after each episode if you need real-time visibility.
- Consider a log rotation library if files get large (> 100MB).

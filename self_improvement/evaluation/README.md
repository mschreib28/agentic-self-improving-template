# Evaluation (Tier 2)

## What This Is

Tier 2 adds structured scoring to every completed episode. An evaluator (LLM-based or rule-based) scores outputs against a department-specific rubric, producing a numeric score and structured feedback.

This enables:
- Quality tracking over time (trend lines per department)
- Identifying systemic failure patterns
- Providing the data foundation for Tier 3 (policy updates)

## Prerequisites

- Tier 1 reflection loops are active.
- Episode logs are being captured (see `docs/logging_and_episodes.md`).
- You have defined what "good" looks like for each department.

## Files in This Directory

| File | Purpose |
|---|---|
| `rubrics.yaml` | Scoring rubrics per department — criteria, weights, and scales |
| `evaluator_prompt.md` | LLM prompt template for rubric-based evaluation |
| `episode_schema.yaml` | Canonical schema for episode log entries |

## How Evaluation Works

```
Episode is logged
       │
       ▼
Evaluator loads rubric for the department
       │
       ▼
Evaluator scores the episode (LLM call or rule-based)
       │
       ▼
Score + feedback appended to episode log
       │
       ▼
Metrics aggregator updates rolling averages
```

## Scoring Scale

All rubrics use a 1-5 scale for consistency:

| Score | Meaning |
|---|---|
| 5 | Exceptional — exceeds requirements, no issues |
| 4 | Good — meets requirements, minor issues only |
| 3 | Acceptable — meets most requirements, some gaps |
| 2 | Below standard — significant gaps, needs revision |
| 1 | Unacceptable — does not meet requirements |

## Calibration

Before trusting automated scores, calibrate against human judgment:

1. Have humans score 20-30 episodes per department.
2. Run the evaluator on the same episodes.
3. Compare distributions. Adjust rubric weights and prompt wording until correlation is > 0.7.
4. Re-calibrate monthly or after rubric changes.

# Optional Paths — Self-Improvement Trade-offs

This document explains which parts of the self-improvement system are optional, when to enable them, and the trade-offs involved.

## Decision Framework

```
Do you have agents producing output?
  │
  YES → Enable Tier 1 (Reflection Loops) — no reason not to
  │
  │     Do you have episode logs?
  │       │
  │       YES → Enable Tier 2 (Evaluation)
  │       │
  │       │     Do you have 50+ scored episodes per department?
  │       │       │
  │       │       YES → Are your rubrics calibrated against human judgment?
  │       │       │       │
  │       │       │       YES → Do you have a human review process?
  │       │       │       │       │
  │       │       │       │       YES → Enable Tier 3 (Policy Updates)
  │       │       │       │       │
  │       │       │       │       NO → Set up human review first
  │       │       │       │
  │       │       │       NO → Calibrate rubrics first
  │       │       │
  │       │       NO → Accumulate more episodes
  │       │
  │       NO → Set up episode logging first
  │
  NO → Focus on building your agent system first
```

## Tier 1: Reflection Loops

**Status: Recommended for everyone.**

### What It Costs

- One extra LLM call per task (the critic prompt).
- ~10-30% more tokens per task.
- Slight latency increase (one additional round trip).

### What You Get

- Fewer obviously bad outputs reaching completion.
- Agents catch their own mistakes before marking `done`.
- Foundation for higher tiers (reflection data feeds evaluation).

### When to Skip

- If latency is hyper-critical (sub-second response requirements).
- If you've verified that your agents already have very high first-pass quality (> 95% of outputs are acceptable without revision).

### Configuration

| Parameter | Location | Default | Notes |
|---|---|---|---|
| Max revisions | Agent execution flow | 1 | Higher values risk infinite loops |
| Critic prompt | `self_improvement/reflection_loops/critic_prompt.md` | Generic | Customize per department |
| Reflection required | Agent signal emission | true | Set false to disable for specific agents |

---

## Tier 2: Evaluation

**Status: Recommended once you have episode logs.**

### What It Costs

- One LLM call per episode (evaluator prompt) — runs async, not in the hot path.
- Storage for scores and feedback.
- Human time for initial calibration (20-30 episodes per department).

### What You Get

- Objective quality scores per episode.
- Trend tracking — is a department getting better or worse?
- Data foundation for Tier 3 (the meta-agent needs scores to identify patterns).
- Ability to detect regressions early.

### When to Skip

- If you're still iterating on agent prompts rapidly and rubrics would be outdated quickly.
- If you have fewer than 10 episodes per department — not enough signal.

### Prerequisites

| Prerequisite | How to Check | How to Fix |
|---|---|---|
| Episode logs are flowing | Check `logs/episodes/` for `.jsonl` files | Implement logging (see `docs/logging_and_episodes.md`) |
| Rubrics are defined | Check `self_improvement/evaluation/rubrics.yaml` | Define criteria and weights per department |
| Rubrics are calibrated | Human-evaluator score correlation > 0.7 | Score 20-30 episodes manually and compare |

### Configuration

| Parameter | Location | Default | Notes |
|---|---|---|---|
| Auto-approve threshold | `rubrics.yaml` → `thresholds.auto_approve` | 4.0 | Episodes above this don't need human review |
| Flag-for-review threshold | `rubrics.yaml` → `thresholds.flag_for_review` | 2.5 | Episodes below this get flagged |
| Trend alert delta | `rubrics.yaml` → `thresholds.trend_alert` | -0.5 | Alert if rolling average drops by this much |

---

## Tier 3: Policy Updates

**Status: Optional. Enable only when Tiers 1 and 2 are stable.**

### What It Costs

- One meta-agent run per cycle (daily or after N episodes) — multiple LLM calls.
- Human time to review and approve proposed changes.
- Risk: bad proposals could degrade quality if approved without scrutiny.

### What You Get

- Continuous improvement of prompts and policies without manual analysis.
- Data-driven changes based on actual failure patterns.
- Documented audit trail of every change (versioned configs + change log).

### When to Skip

- If your agent system is still in early development — changing prompts manually is faster.
- If you don't have a reliable human review process for proposed changes.
- If your evaluation rubrics aren't calibrated — the meta-agent would be optimizing for the wrong thing.
- If you have fewer than 50 scored episodes per department — not enough patterns to detect.

### Prerequisites

| Prerequisite | How to Check | How to Fix |
|---|---|---|
| Tier 2 is stable | Scores are consistent, no wild swings | Calibrate rubrics, fix logging gaps |
| 50+ scored episodes per dept | Count episodes in log files | Wait and accumulate |
| Human review process exists | Someone is designated to review proposals | Assign a reviewer, set up notification channel |
| Configs are versioned | Files have `version` fields | Add YAML front matter with version |
| Rollback is possible | Previous versions are kept | Enable backups in `policy_diff.py` |

### Risk Mitigation

| Risk | Mitigation |
|---|---|
| Meta-agent proposes harmful change | Safety checks in `meta_agent.py` block removal of guardrails |
| Change degrades quality | Monitor scores after applying a change; rollback if quality drops |
| Human approver is rubber-stamping | Require written justification for approvals; rotate reviewers |
| Too many proposals (noisy) | Rate-limit proposals; increase minimum episode threshold |
| Proposals are too vague to act on | Require specific diffs (before/after), not just descriptions |

### Configuration

| Parameter | Location | Default | Notes |
|---|---|---|---|
| Run frequency | Cron / scheduler | Daily | Or trigger after N episodes |
| Min episodes for analysis | `meta_agent.py` | 10 per cycle | Below this, skip the cycle |
| Allowed change categories | `meta_agent.py` safety checks | All except guardrail removal | Restrict further if needed |
| Notification channel | `escalation_rules.yaml` | Slack / email / GitHub | Where proposals are sent for review |

---

## Advanced Paths (Future)

These are not implemented in this template but are natural extensions:

### Synthetic Data Generation

- Generate training examples from high-scoring episodes.
- Use low-scoring episodes as negative examples.
- **When**: You have 500+ scored episodes and want to fine-tune a model.

### Fine-Tuning Hooks

- Periodically fine-tune agent models on curated episode data.
- **When**: You have domain-specific tasks where fine-tuning outperforms prompting.
- **Risk**: High. Requires careful evaluation before and after fine-tuning.

### A/B Testing of Prompts

- Run two prompt versions in parallel and compare scores.
- **When**: You want to validate a prompt change before full rollout.
- **How**: Split tasks 50/50 between prompt versions, compare evaluation scores.

### Multi-Agent Negotiation

- Allow department heads to negotiate resource allocation or task priority.
- **When**: You have competing departments with limited resources.
- **Risk**: Medium. Can lead to deadlocks if not carefully designed.

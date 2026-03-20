# Policy Updates (Tier 3)

## What This Is

Tier 3 is the most advanced self-improvement capability: a meta-agent that periodically reviews scored episodes and proposes changes to system prompts, policies, and rubrics.

**This tier is optional and should only be enabled when:**
- Tier 2 evaluation is stable and calibrated against human judgment.
- You have accumulated enough episodes to see patterns (50+ per department).
- A human review process is in place for approving changes.

## How It Works

```
Scored episodes accumulate
        │
        ▼
Meta-agent runs on schedule (e.g., daily)
        │
        ├─► Analyzes low-scoring episodes for patterns
        ├─► Identifies common failure modes
        ├─► Drafts proposed changes (prompts, policies, rubrics)
        │
        ▼
Proposal is validated against safety constraints
        │
        ▼
Proposal is submitted for human review
        │
        ├─► Approved → apply to versioned config
        └─► Rejected → log rejection reason for learning
```

## Files in This Directory

| File | Purpose |
|---|---|
| `meta_agent.py` | Python stub for the meta-agent that analyzes episodes and proposes changes |
| `policy_diff.py` | Utility for generating and applying diffs to policy/prompt files |

## Safety Guardrails

Policy updates are the riskiest part of the self-improvement system. These guardrails are non-negotiable:

1. **Human review gate** — every proposed change must be approved by a human before applying.
2. **No removal of safety constraints** — the meta-agent cannot propose removing guardrails, escalation rules, or human review gates.
3. **Versioned configs** — all prompts and policies use version numbers. Changes create new versions, never overwrite.
4. **Rollback capability** — keep previous versions so you can revert if a change degrades quality.
5. **Gradual rollout** — apply changes to one department first, monitor for a defined period, then expand.

## Change Categories

The meta-agent can propose changes in these categories:

| Category | Example | Risk Level |
|---|---|---|
| Prompt clarification | Add an example to the critic prompt | Low |
| Checklist addition | Add "check for edge cases" to build rubric | Low |
| Tool usage guidance | "Prefer X tool over Y for this task type" | Medium |
| Spawn limit adjustment | Increase max sub-agents from 3 to 5 | Medium |
| Escalation threshold change | Change blocked-cycles threshold from 2 to 3 | Medium |
| Rubric weight adjustment | Shift weight from aesthetics to accessibility | High |
| Role scope change | Expand/restrict what a department can do | High |

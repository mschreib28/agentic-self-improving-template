# Self-Improvement

This directory contains the three tiers of the self-improvement subsystem.

## Tiers

| Tier | Directory | What It Does | Prerequisite |
|---|---|---|---|
| **1 — Reflection** | `reflection_loops/` | Agents critique their own output before signaling `done` | None — start here |
| **2 — Evaluation** | `evaluation/` | Score episodes against rubrics, track quality over time | Tier 1 + episode logging |
| **3 — Policy Updates** | `policy_updates/` | Meta-agent proposes changes to prompts and configs | Tier 2 + stable metrics |

## Adoption Order

Enable these in order. Each tier builds on the previous one.

1. **Start with Tier 1** — it's free (no extra infra) and immediately improves output quality.
2. **Add Tier 2** once you have episode logs flowing and want to track trends.
3. **Enable Tier 3** only when you trust your evaluation rubrics and have a human review process.

See [`docs/optional_paths.md`](../docs/optional_paths.md) for detailed guidance on when to enable each tier.

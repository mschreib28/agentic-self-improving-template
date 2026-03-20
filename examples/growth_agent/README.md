# Example: Growth Agent

## Overview

A fully worked, end-to-end example of the **Plan → Execute → Evaluate → Improve** loop applied to a content/growth campaign. The demo script (`growth_agent.py`) runs without an LLM — it reads `campaign_task.yaml` and `metrics.csv`, scores results, updates the growth playbook, and logs a structured episode. Swap in real LLM calls when you're ready.

## Files

| File | Purpose |
|---|---|
| `growth_agent.py` | Runnable end-to-end demo — reads task + metrics, scores, updates playbook, logs episode |
| `campaign_task.yaml` | Task definition: goal, audience, channels, budget, variant angles, success criteria |
| `metrics.csv` | Sample experiment results (impressions, clicks, signups per variant) |
| `growth_playbook.md` | Living playbook — the meta-agent appends guidelines here after each campaign |

## Try It

```bash
pip install pyyaml
python examples/growth_agent/growth_agent.py
```

Output: scored variants in the terminal, an appended entry in `growth_playbook.md`, and a new line in `episodes.jsonl`.

---

## The Full Loop, Step by Step

### 1. Task Definition

A campaign task is a YAML document that gives the Growth Head all the context it needs. Key fields:

```yaml
goal: "Increase email signups for Product X by 20% over 2 weeks"
channels: [email, landing_page]
budget_usd: 2000
guardrails:
  brand_voice: "Friendly, practical — no hype"
  forbidden: ["free", "guaranteed", "limited time"]
success_metric:
  primary: signups_per_1k_impressions
  primary_threshold: 5.0
  secondary: unsubscribe_rate
  secondary_max: 0.02
```

See `campaign_task.yaml` for the full structure. The Foreman passes this to the Growth Head as a task assignment.

---

### 2. Plan

The Growth Head reads the task and produces a short experiment plan before spawning any sub-agents:

- **Variant count** — e.g., 3 variants (one control + two treatments)
- **Variant angles** — what hypothesis each variant tests (curiosity vs. social proof vs. urgency)
- **Traffic split** — e.g., 33/33/33 across variants, or 40% control / 30% / 30% for lower risk
- **Measurement window** — e.g., 48 hours before calling a winner

The plan is embedded in `campaign_task.yaml` under `experiment.plan` so sub-agents know which angle to use. In the runnable demo, variant stubs are pre-defined; in production, you replace them with LLM calls that use the angle as a generation directive.

---

### 3. Execute

Sub-agents generate the creative content:

- One sub-agent per variant, receiving the campaign brief + its specific angle
- Each sub-agent produces: subject line / headline, body copy, call-to-action
- A deployment step (human or tool) pushes each variant to your channel (ESP, ads platform, etc.) with IDs that match the experiment definition

In the demo, `growth_agent.py` uses hardcoded variant stubs. Replace `_stub_generate_variant()` with a real LLM call that formats the `CONTENT_GENERATION_PROMPT`.

---

### 4. Evaluate

After the measurement window, an evaluator agent collects metrics and scores each variant:

**Scoring rubric (growth department):**

| Metric | Weight | Source |
|---|---|---|
| `signups_per_1k` | 40% | Primary success metric |
| `ctr` | 30% | Engagement proxy |
| `unsubscribe_rate` | 20% | Audience fit signal (lower is better) |
| `spam_complaints` | 10% | Deliverability health (lower is better) |

The evaluator reads from `metrics.csv` (in the demo) or your real analytics API, produces a score per variant, and identifies the winner. Results are structured as a `CampaignEpisode` conforming to `self_improvement/evaluation/episode_schema.yaml`.

---

### 5. Improve

A "growth meta-agent" reads the completed episode and updates the team playbook:

1. **Summarizes what worked** — which angles, CTAs, and subject patterns drove signups
2. **Summarizes what didn't** — what correlated with high unsubscribe or low CTR
3. **Appends guidelines** to `growth_playbook.md` — versioned, with evidence and confidence level
4. **Optionally proposes prompt changes** — e.g., "add a 'curiosity-first' directive to the subject line sub-agent prompt" — routed through the Tier 3 review gate before applying

The next campaign's Growth Head reads `growth_playbook.md` as part of its context, so improvement is visible in behavior without any model retraining.

---

### 6. Log

Every campaign produces one episode appended to `episodes.jsonl`:

```json
{
  "episode_id": "ep-20250115-001",
  "task_id": "GROWTH-042",
  "department": "growth",
  "variants": [
    { "variant_id": "GROWTH-042-v1", "angle": "curiosity", "headline": "..." }
  ],
  "results": [
    { "variant_id": "GROWTH-042-v1", "signups_per_1k": 7.2, "ctr": 0.041 }
  ],
  "winner": "GROWTH-042-v1",
  "evaluation_score": 4.1,
  "lessons": ["Curiosity-based headlines outperformed urgency by 2× for this segment"],
  "timestamp": "2025-01-15T10:32:00Z"
}
```

The Growth Head reads the last N episodes as context for the next campaign. Self-improvement is just **reading your own history**.

---

## Adapting This Example

| To do this | Change this |
|---|---|
| Use a real LLM | Replace `_stub_generate_variant()` and `_stub_derive_guidelines()` with `call_llm()` calls |
| Pull real metrics | Replace `load_metrics_from_csv()` with calls to your analytics API |
| Add more variant angles | Extend `experiment.plan.variants` in `campaign_task.yaml` |
| Change scoring weights | Edit `RUBRIC_WEIGHTS` in `growth_agent.py` |
| Push to a real ESP | Add a `deploy_variant()` function after generation |
| Run on a schedule | Wrap `run_campaign()` in a cron job or task queue |

"""
Growth agent — end-to-end campaign loop demo.

Runs without an LLM. Shows the full Plan → Execute → Evaluate → Improve
cycle using campaign_task.yaml for the task definition and metrics.csv
for simulated experiment results.

Usage:
    pip install pyyaml
    python examples/growth_agent/growth_agent.py

What this script does:
  1. PLAN   — reads campaign_task.yaml, extracts variant angles and experiment config
  2. EXECUTE — generates stub variant content (replace with LLM calls when ready)
  3. EVALUATE — reads metrics.csv, scores each variant using a weighted rubric
  4. IMPROVE  — derives guidelines, appends them to growth_playbook.md
  5. LOG      — writes a structured episode entry to episodes.jsonl

To plug in a real LLM:
  - Replace _stub_generate_variant() with a call_llm() call using CONTENT_GENERATION_PROMPT.
  - Replace _stub_derive_guidelines() with a call_llm() call using GUIDELINE_PROMPT.
  - Replace load_metrics_from_csv() with your real analytics API call.
"""

import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# pyyaml is the only non-stdlib dependency
try:
    import yaml
except ImportError as e:
    raise SystemExit("Install pyyaml first:  pip install pyyaml") from e

# ---------------------------------------------------------------------------
# Paths (relative to repo root; adjust if running from a different directory)
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent
TASK_FILE = _HERE / "campaign_task.yaml"
METRICS_FILE = _HERE / "metrics.csv"
PLAYBOOK_FILE = _HERE / "growth_playbook.md"
EPISODES_FILE = _HERE / "episodes.jsonl"

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ContentVariant:
    variant_id: str
    angle: str
    headline: str
    subheadline: str
    body: str
    call_to_action: str


@dataclass
class VariantMetrics:
    variant_id: str
    angle: str
    impressions: int
    clicks: int
    signups: int
    unsubscribes: int
    spam_complaints: int
    ctr: float = 0.0
    signups_per_1k: float = 0.0
    unsubscribe_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.impressions > 0:
            self.ctr = self.clicks / self.impressions
            self.signups_per_1k = (self.signups / self.impressions) * 1000
            self.unsubscribe_rate = self.unsubscribes / self.impressions


@dataclass
class VariantScore:
    variant_id: str
    angle: str
    weighted_score: float
    breakdown: dict[str, float]
    meets_primary_threshold: bool
    meets_secondary_threshold: bool


@dataclass
class Guideline:
    rule: str
    evidence: str
    confidence: str  # high | medium | low


@dataclass
class CampaignEpisode:
    episode_id: str
    task_id: str
    department: str = "growth"
    variants: list[dict[str, Any]] = field(default_factory=list)
    results: list[dict[str, Any]] = field(default_factory=list)
    scores: list[dict[str, Any]] = field(default_factory=list)
    winner: str | None = None
    evaluation_score: float = 0.0
    lessons: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Scoring rubric
# Weights must sum to 1.0. Adjust to match your success criteria.
# ---------------------------------------------------------------------------

RUBRIC_WEIGHTS = {
    "signups_per_1k": 0.40,   # primary metric
    "ctr":            0.30,   # engagement proxy
    "unsubscribe_rate": 0.20, # lower is better (we invert this below)
    "spam_complaints":  0.10, # lower is better (we invert this below)
}

def _score_metric(metric_name: str, value: float, all_values: list[float]) -> float:
    """Normalize a single metric to 1–5 relative to the field.

    For 'good is high' metrics (signups, ctr): best gets 5, worst gets 1.
    For 'good is low' metrics (unsubscribes, spam): inverted.
    """
    if not all_values or max(all_values) == min(all_values):
        return 3.0

    low_is_good = metric_name in ("unsubscribe_rate", "spam_complaints")
    lo, hi = min(all_values), max(all_values)

    if low_is_good:
        normalized = 1.0 - (value - lo) / (hi - lo)
    else:
        normalized = (value - lo) / (hi - lo)

    return 1.0 + normalized * 4.0  # scale to [1, 5]


def score_variants(
    metrics: list[VariantMetrics],
    task: dict,
) -> list[VariantScore]:
    """Score all variants using the rubric weights."""
    primary_threshold = task["success_metric"]["primary_threshold"]
    secondary_max = task["success_metric"]["secondary_max"]

    field_values: dict[str, list[float]] = {
        k: [getattr(m, k) for m in metrics] for k in RUBRIC_WEIGHTS
    }

    scores = []
    for m in metrics:
        breakdown = {}
        for metric, weight in RUBRIC_WEIGHTS.items():
            raw = getattr(m, metric)
            normalized = _score_metric(metric, raw, field_values[metric])
            breakdown[metric] = round(normalized, 2)

        weighted = sum(breakdown[k] * w for k, w in RUBRIC_WEIGHTS.items())
        scores.append(VariantScore(
            variant_id=m.variant_id,
            angle=m.angle,
            weighted_score=round(weighted, 2),
            breakdown=breakdown,
            meets_primary_threshold=m.signups_per_1k >= primary_threshold,
            meets_secondary_threshold=m.unsubscribe_rate <= secondary_max,
        ))

    return sorted(scores, key=lambda s: s.weighted_score, reverse=True)


# ---------------------------------------------------------------------------
# Step 1: PLAN — load task
# ---------------------------------------------------------------------------

def load_task(path: Path = TASK_FILE) -> dict:
    """Read and return the campaign task definition."""
    with path.open() as f:
        doc = yaml.safe_load(f)
    return doc["task"]


# ---------------------------------------------------------------------------
# Step 2: EXECUTE — generate variant content
# ---------------------------------------------------------------------------

# Production: replace _stub_generate_variant with this prompt + your LLM client.
CONTENT_GENERATION_PROMPT = """\
You are a growth content specialist writing an email campaign variant.

Campaign goal: {goal}
Target audience: {audience}
Brand voice: {brand_voice}
Angle for this variant: {angle}
Directive: {directive}
Forbidden words/phrases: {forbidden}
Max length: {max_words} words

Write a complete variant with:
- headline
- subheadline
- body (email copy)
- call_to_action

Respond with JSON:
{{
  "headline": "...",
  "subheadline": "...",
  "body": "...",
  "call_to_action": "..."
}}
"""

def _stub_generate_variant(task: dict, variant_def: dict) -> dict:
    """Hardcoded stub — replace with call_llm(CONTENT_GENERATION_PROMPT.format(...))."""
    stubs = {
        "curiosity": {
            "headline": "Why are 500 developers switching their API setup on Tuesday mornings?",
            "subheadline": "It's not what you'd expect — and it takes 4 minutes.",
            "body": (
                "We noticed a pattern in our usage data. Developers who adopt Product X "
                "on a Tuesday morning ship their first integration by Wednesday. "
                "No docs marathon. No Slack threads. Just a working example and an hour. "
                "Here's the setup they used."
            ),
            "call_to_action": "Show me the Tuesday setup →",
        },
        "social_proof": {
            "headline": "Priya cut her API integration time from 3 days to 45 minutes",
            "subheadline": "Here's the exact setup she used (copy-paste ready).",
            "body": (
                "Priya's team was burning 3 days per integration — reading docs, "
                "wrestling with auth, debugging edge cases. With Product X, her first "
                "working call took 45 minutes. The second took 12. "
                "Her words: 'I didn't expect it to just work.'"
            ),
            "call_to_action": "Get the same setup →",
        },
        "practical_value": {
            "headline": "Working API integration in 5 minutes — or we'll walk you through it live",
            "subheadline": "One command. No account required to try it.",
            "body": (
                "Product X is built around one constraint: your first successful API call "
                "should happen before you finish your coffee. "
                "Run one command, get a working response, then build from there. "
                "No YAML config. No OAuth dance. No 'getting started' guide that's 40 pages long."
            ),
            "call_to_action": "Try it now — takes 5 minutes →",
        },
    }
    content = stubs.get(variant_def["angle"], stubs["practical_value"])
    return content


def generate_variants(task: dict) -> list[ContentVariant]:
    """Generate one ContentVariant per angle defined in the task."""
    variants = []
    for v_def in task["experiment"]["variants"]:
        content = _stub_generate_variant(task, v_def)
        variant_id = f"{task['task_id']}-{v_def['id']}"
        variants.append(ContentVariant(
            variant_id=variant_id,
            angle=v_def["angle"],
            headline=content["headline"],
            subheadline=content["subheadline"],
            body=content["body"],
            call_to_action=content["call_to_action"],
        ))
    return variants


# ---------------------------------------------------------------------------
# Step 3: EVALUATE — load metrics, score variants
# ---------------------------------------------------------------------------

def load_metrics_from_csv(path: Path = METRICS_FILE) -> list[VariantMetrics]:
    """Read experiment results from a CSV file.

    CSV columns: variant_id, angle, impressions, clicks, signups,
                 unsubscribes, spam_complaints
    Replace this with a real analytics API call in production.
    """
    results = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(VariantMetrics(
                variant_id=row["variant_id"],
                angle=row["angle"],
                impressions=int(row["impressions"]),
                clicks=int(row["clicks"]),
                signups=int(row["signups"]),
                unsubscribes=int(row["unsubscribes"]),
                spam_complaints=int(row["spam_complaints"]),
            ))
    return results


# ---------------------------------------------------------------------------
# Step 4: IMPROVE — derive guidelines, update playbook
# ---------------------------------------------------------------------------

# Production: replace _stub_derive_guidelines with this prompt + call_llm().
GUIDELINE_PROMPT = """\
You are a growth analytics specialist reviewing A/B test results.

Campaign goal: {goal}
Measurement window: {window_hours} hours

Results by variant:
{results_table}

Winner: {winner_id} (angle: {winner_angle}, score: {winner_score})

Based on these results, derive 2-3 actionable content guidelines for
the team's playbook. Be specific: reference the angle, metric delta, and
what the data suggests about this audience.

Respond with JSON:
{{
  "guidelines": [
    {{
      "rule": "Concise actionable statement (what to do or avoid)",
      "evidence": "Specific metric or comparison that supports this",
      "confidence": "high | medium | low"
    }}
  ]
}}
"""

def _stub_derive_guidelines(
    task: dict,
    metrics: list[VariantMetrics],
    scores: list[VariantScore],
) -> list[Guideline]:
    """Stub guideline derivation — replace with call_llm(GUIDELINE_PROMPT.format(...))."""
    winner = scores[0]
    loser = scores[-1]
    return [
        Guideline(
            rule=(
                f"Lead with practical value for this audience segment. "
                f"The '{winner.angle}' angle outperformed '{loser.angle}' "
                f"by {winner.weighted_score - loser.weighted_score:.1f} points."
            ),
            evidence=(
                f"Variant {winner.variant_id} achieved "
                f"{next(m.signups_per_1k for m in metrics if m.variant_id == winner.variant_id):.1f} "
                f"signups/1k vs "
                f"{next(m.signups_per_1k for m in metrics if m.variant_id == loser.variant_id):.1f} "
                f"for {loser.variant_id}."
            ),
            confidence="medium",
        ),
        Guideline(
            rule=(
                f"Unsubscribe rate is a reliable signal for audience fit with this segment. "
                f"Variants with unsubscribe_rate > {task['success_metric']['secondary_max']} "
                f"consistently underperformed on primary metrics."
            ),
            evidence=(
                f"Variant {loser.variant_id} had the highest unsubscribe rate "
                f"({next(m.unsubscribe_rate for m in metrics if m.variant_id == loser.variant_id):.3f}) "
                f"and the lowest score ({loser.weighted_score})."
            ),
            confidence="medium",
        ),
    ]


def derive_guidelines(
    task: dict,
    metrics: list[VariantMetrics],
    scores: list[VariantScore],
) -> list[Guideline]:
    return _stub_derive_guidelines(task, metrics, scores)


def update_playbook(
    guidelines: list[Guideline],
    episode_id: str,
    playbook_path: Path = PLAYBOOK_FILE,
) -> None:
    """Append new guidelines to the growth playbook."""
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    content = playbook_path.read_text()

    new_rules = []
    existing_rule_count = content.count("\n### Rule ")
    for i, g in enumerate(guidelines, start=existing_rule_count + 1):
        new_rules.append(
            f"\n### Rule {i} — {today}\n"
            f"**Rule:** {g.rule}\n"
            f"**Evidence:** {g.evidence}\n"
            f"**Confidence:** {g.confidence}\n"
            f"**Source episode:** {episode_id}\n"
        )

    updated = content.replace(
        "*No guidelines yet. Run `growth_agent.py` to generate the first entry.*",
        "\n".join(new_rules).lstrip(),
    )
    if updated == content:
        updated = content.replace(
            "<!-- The meta-agent appends entries in this format:",
            "\n".join(new_rules) + "\n\n<!-- The meta-agent appends entries in this format:",
        )

    playbook_path.write_text(updated)


# ---------------------------------------------------------------------------
# Step 5: LOG — write episode
# ---------------------------------------------------------------------------

def log_episode(episode: CampaignEpisode, path: Path = EPISODES_FILE) -> None:
    """Append the episode as a JSON line to episodes.jsonl."""
    with path.open("a") as f:
        f.write(json.dumps(asdict(episode)) + "\n")


# ---------------------------------------------------------------------------
# Orchestration — Growth Head
# ---------------------------------------------------------------------------

def run_campaign(
    task_path: Path = TASK_FILE,
    metrics_path: Path = METRICS_FILE,
) -> CampaignEpisode:
    """Full Plan → Execute → Evaluate → Improve → Log cycle."""

    # 1. PLAN
    task = load_task(task_path)
    episode_id = f"ep-{datetime.now(tz=timezone.utc).strftime('%Y%m%d')}-001"
    print(f"\n{'='*60}")
    print(f"Campaign: {task['task_id']}  |  Episode: {episode_id}")
    print(f"Goal: {task['goal']}")
    print(f"Variants: {len(task['experiment']['variants'])} angles to test")

    # 2. EXECUTE
    print(f"\n{'─'*60}")
    print("EXECUTE — generating variant content...")
    variants = generate_variants(task)
    for v in variants:
        print(f"  [{v.angle}]  {v.headline}")

    # 3. EVALUATE
    print(f"\n{'─'*60}")
    print("EVALUATE — loading metrics and scoring variants...")
    metrics = load_metrics_from_csv(metrics_path)
    scores = score_variants(metrics, task)

    print(f"\n  {'Variant':<25} {'Score':>6}  {'sig/1k':>7}  {'CTR':>6}  {'Unsub':>6}  {'Threshold':>9}")
    print(f"  {'─'*25} {'─'*6}  {'─'*7}  {'─'*6}  {'─'*6}  {'─'*9}")
    for s in scores:
        m = next(x for x in metrics if x.variant_id == s.variant_id)
        threshold_ok = "✓ PASS" if s.meets_primary_threshold else "✗ MISS"
        print(
            f"  {s.variant_id:<25} {s.weighted_score:>6.2f}  "
            f"{m.signups_per_1k:>7.1f}  {m.ctr:>6.3f}  "
            f"{m.unsubscribe_rate:>6.3f}  {threshold_ok:>9}"
        )

    winner = scores[0] if scores[0].meets_primary_threshold else None
    if winner:
        print(f"\n  Winner: {winner.variant_id} (angle: {winner.angle}, score: {winner.weighted_score})")
    else:
        print(f"\n  No variant met the primary threshold "
              f"({task['success_metric']['primary_threshold']} sig/1k). "
              f"Top scorer: {scores[0].variant_id} — flagging for human review.")

    # 4. IMPROVE
    print(f"\n{'─'*60}")
    print("IMPROVE — deriving guidelines and updating playbook...")
    guidelines = derive_guidelines(task, metrics, scores)
    update_playbook(guidelines, episode_id)
    for g in guidelines:
        print(f"  [{g.confidence}] {g.rule}")
    print(f"  Playbook updated: {PLAYBOOK_FILE}")

    # 5. LOG
    episode = CampaignEpisode(
        episode_id=episode_id,
        task_id=task["task_id"],
        variants=[asdict(v) for v in variants],
        results=[asdict(m) for m in metrics],
        scores=[asdict(s) for s in scores],
        winner=winner.variant_id if winner else None,
        evaluation_score=scores[0].weighted_score,
        lessons=[g.rule for g in guidelines],
    )
    log_episode(episode)
    print(f"\n{'─'*60}")
    print(f"LOG — episode written to {EPISODES_FILE}")
    print(f"{'='*60}\n")

    return episode


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_campaign()

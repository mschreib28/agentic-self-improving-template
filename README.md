# Agentic Self-Improving Template

A framework-agnostic template for building **multi-agent systems that evaluate and improve their own performance** over time.

> This repo started as a way for me and a friend to turn our "agent teams" into **self-improving coworkers**, not just workflow glue. The structure and examples here (Foreman + departments, reflection loops, evaluation rubrics, and a meta-agent for policy updates) are meant to be adapted, forked, and argued with.
>
> If you're already running agents in your own stack, you can map your setup into `AGENTS.md`, fill in the bold placeholders in `GOALS.md`, and start by wiring Tier 1 reflection and episode logging into one department. From there, please open issues/PRs with what works, what breaks, and what patterns you discover — this is very much a living playbook.

## Who This Is For

You already have a multi-agent system — a Foreman orchestrating department heads, each with their own sub-agents. You want a structured way to add **self-evaluation, reflection, and iterative improvement** without coupling to a specific agent framework.

## Design Philosophy

1. **Structure over framework.** This repo defines patterns, not a library. Swap in LangChain, CrewAI, AutoGen, or raw API calls — the patterns remain the same.
2. **Three tiers of self-improvement.** Start with reflection loops (free, no training). Add evaluation metrics when ready. Enable policy adaptation only when you have stable data.
3. **Human-in-the-loop by default.** Every automated change path is gated by review. You opt _in_ to autonomy, not out.
4. **Convention over configuration.** Folder names, file patterns, and completion signals are consistent so that agents can navigate this repo programmatically.

## Repository Structure

```
├── README.md                  ← You are here
├── AGENTS.md                  ← Agent team org chart, roles, signals
├── GOALS.md                   ← Business & system goals (fill in placeholders)
│
├── architecture/
│   ├── SYSTEM_DESIGN.md       ← System diagrams and component descriptions
│   └── WORKFLOWS.md           ← Plan → Execute → Evaluate → Improve loop
│
├── self_improvement/
│   ├── reflection_loops/      ← Tier 1: Think → Do → Evaluate → Improve
│   ├── evaluation/            ← Tier 2: Rubrics, scoring, episode logging
│   └── policy_updates/        ← Tier 3: Meta-agent prompt/policy adaptation
│
├── examples/
│   ├── growth_agent/          ← Content experiments with self-evaluation
│   └── build_agent/           ← Code generation with review loop
│
├── config/
│   ├── prompts/               ← System and role prompts (versioned)
│   ├── playbooks/             ← Per-department learned guidelines (long-term memory)
│   └── policies/              ← Spawn rules, escalation, constraints (YAML)
│
└── docs/
    ├── getting_started.md     ← Setup and adoption guide
    ├── logging_and_episodes.md← Episode format and storage patterns
    └── optional_paths.md      ← When to enable each self-improvement tier
```

## Quick Start

1. **Read [`GOALS.md`](GOALS.md)** — fill in the bold placeholders with your actual business KPIs and quality metrics.
2. **Read [`AGENTS.md`](AGENTS.md)** — map your existing agent team onto the role template. Add or remove departments as needed.
3. **Start with Tier 1** — wire up the reflection loop from [`self_improvement/reflection_loops/`](self_improvement/reflection_loops/) into your existing agent execution flow.
4. **Add evaluation** when you have logs — use the rubrics in [`self_improvement/evaluation/`](self_improvement/evaluation/) to score episodes.
5. **Enable policy adaptation** only when Tier 2 is stable — see [`docs/optional_paths.md`](docs/optional_paths.md) for prerequisites.

See [`docs/getting_started.md`](docs/getting_started.md) for a detailed walkthrough.

## Key Concepts

| Concept | Where Defined | Summary |
|---|---|---|
| Completion signals | `AGENTS.md` | `done`, `blocked`, `needs-review` — standard status protocol |
| Episode | `docs/logging_and_episodes.md` | A single unit of work: task → actions → result → score |
| Reflection loop | `self_improvement/reflection_loops/` | Agent critiques its own output before marking done |
| Rubric | `self_improvement/evaluation/` | Scoring criteria per department or task type |
| Policy update | `self_improvement/policy_updates/` | Proposed change to a prompt or config, gated by review |
| Playbook | `config/playbooks/` | Per-department learned guidelines — long-term agent memory |
| Context assembly | `architecture/SYSTEM_DESIGN.md` | How agents reconstruct identity + knowledge on each invocation |

## Conventions

- **Prompt files** use `.md` with YAML front matter for metadata (version, role, department).
- **Policy files** use `.yaml` for machine-readable configs.
- **Episode logs** use `.jsonl` (one JSON object per line) for append-friendly storage.
- **Bold placeholders** in docs look like this: **\[YOUR VALUE HERE\]** — search for `**[` to find them all.

## License

MIT — use this however you want.

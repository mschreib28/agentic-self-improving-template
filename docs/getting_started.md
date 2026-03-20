# Getting Started

This guide walks you through adopting the template for your existing multi-agent system.

## Prerequisites

### 1. You have a working multi-agent system with some form of orchestrator

**What this means in practice:**

You have _some_ "Foreman" / orchestrator that:
- Receives a user or business request.
- Breaks it into subtasks.
- Routes those to specialist agents.
- Collects their outputs and returns a result.

This can be:
- A custom Python or TypeScript script coordinating multiple LLM calls.
- A framework like [LangGraph](https://github.com/langchain-ai/langgraph), [AutoGen](https://github.com/microsoft/autogen), [CrewAI](https://github.com/crewAIInc/crewAI), or [AWS Multi-Agent Orchestrator](https://github.com/awslabs/multi-agent-orchestrator).
- A simple "router" agent plus a set of tool-like agents behind an API.

You do **not** need anything fancy. But you should be able to point to one place in your code and say: "This is where tasks get decomposed and delegated." If you can do that, you satisfy this prerequisite.

> **Not there yet?** A good starting reference is the [AWS Multi-Agent Orchestrator guide](https://github.com/awslabs/multi-agent-orchestrator) or the patterns in [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems) on GitHub, which covers orchestration patterns across multiple frameworks.

---

### 2. You can modify agent system prompts and execution flows

**What this means in practice:**

You can edit:
- The **system/role prompts** for your Foreman and department heads — what they think their job is, what tools they have, what "done" looks like.
- The **order of steps** they run — e.g., inserting "generate → self-critique → revise → return" instead of "generate → return".

Concretely, you can change either a prompt file _or_ a small piece of code that defines a workflow or state machine. You don't need to own the full agent runtime, just the parts that define your agents' behavior.

In this repo, that maps to:
- `config/prompts/*` for role prompts (system messages).
- `architecture/WORKFLOWS.md` and the example scripts for execution flow patterns.

> **Why it matters here:** Tier 1 reflection is just one extra step in the execution flow (call critic prompt, handle the verdict). If you can add a step, you can wire Tier 1 in an afternoon.

---

### 3. You have a way to make LLM calls

**What this means in practice:**

You can already send a prompt to a model and get back text:
- Via API: OpenAI, Anthropic, Google Gemini, Mistral, etc.
- Via local runtime: Ollama, vLLM, LM Studio, etc.

The minimum capability is:
```python
response = llm_client.complete(system_prompt, user_prompt)  # returns string
```

You do **not** need streaming, tool use, or function calling for Tiers 1 and 2. Structured JSON responses (either native JSON mode or parsed from text) are useful for the evaluation and reflection prompts.

In the examples, every Python stub assumes a simple `call_llm(prompt) -> dict` abstraction. Replace it with whatever client you use — the pattern doesn't change.

> **Starter references:** [OpenAI Python client](https://github.com/openai/openai-python) and [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) both have minimal working examples in their READMEs.

---

> **Already have a Foreman + department heads running?** You probably satisfy all three prerequisites. Your first move is just:
> 1. Map your agents into `AGENTS.md` (the "How to Map Your Current Setup" table).
> 2. Wire the Tier 1 reflection loop (critic + revise) for one department — Growth is a good starting point, see `examples/growth_agent/` for a runnable demo.
> 3. Start logging episodes using `self_improvement/evaluation/episode_schema.yaml`.
>
> Once those three are in place, the evaluation and policy-update layers become "just configuration and prompts" — not a redesign.

## If You Already Have Agents Running

If you've got a Foreman (or equivalent orchestrator) and department-head agents already executing tasks, you don't need to rebuild anything. Focus on wiring in two things first:

### Wire Tier 1 Reflection (highest ROI, ~1 hour)

1. Pick your highest-volume department (the one producing the most output per day).
2. In that agent's execution flow, insert one additional LLM call **after** it produces output but **before** it emits a completion signal. Use `self_improvement/reflection_loops/critic_prompt.md` as the prompt template.
3. Parse the critic's JSON response. If `verdict` is `"pass"`, proceed as normal. If `"revise"`, let the agent fix the issues once. If `"escalate"`, signal `needs-review`.
4. That's it. You now have a self-checking agent. Expand to other departments once you see the pattern working.

### Add Episode Logging (enables everything else, ~1 hour)

1. After each task completes (regardless of signal), append a JSON object to a `.jsonl` file. One file per department per day works well.
2. Start with the minimum fields: `episode_id`, `task_id`, `department`, `agent_id`, `task_description`, `result.signal`, and the reflection verdict if you've wired it.
3. You don't need a database. Flat files are fine for the first 1000+ episodes.
4. Once logs are flowing, you have the data foundation for Tier 2 evaluation and Tier 3 policy adaptation.

See `docs/logging_and_episodes.md` for the full schema and progressive detail levels.

### What to Ignore for Now

- **Tier 2 (evaluation rubrics)** — skip until you have 20+ logged episodes per department.
- **Tier 3 (meta-agent policy updates)** — skip until Tier 2 is calibrated. See `docs/optional_paths.md` for the full decision tree.
- **Prompt versioning** — useful but not urgent. Add YAML front matter to your prompts when you're ready to track changes.

### Map Your Agents into the Repo

Open `AGENTS.md` and fill in the "How to Map Your Current Setup" table with your actual agent names and IDs. This makes the repo a live reference for your system, not just a template.

---

## Full Walkthrough (Starting From Scratch)

The steps below are for adopting the full template systematically. If you've already done the quick-start above, skip to Step 3.

## Step 1: Map Your Team (30 minutes)

Open [`AGENTS.md`](../AGENTS.md) and map your existing agents onto the template:

1. **Identify your Foreman** — whatever orchestrates your top-level task decomposition.
2. **List your departments** — add or remove rows from the Department Heads table to match your actual team.
3. **Document sub-agents** — for each department, note what focused tasks sub-agents handle.
4. **Define permissions** — update `config/policies/spawn_rules.yaml` with your actual spawning rules.

If you have departments not in the template (e.g., "legal review", "data pipeline"), add them. The pattern is the same.

## Step 2: Fill In Goals (30 minutes)

Open [`GOALS.md`](../GOALS.md) and fill in every **bold placeholder**:

1. **Business KPIs** — what are you actually optimizing for?
2. **Department goals** — what does "good output" look like per department?
3. **Quality targets** — set initial targets. You'll calibrate these later.
4. **Self-improvement milestones** — what does "better" mean for your system?

Tip: Start with conservative targets. You can tighten them once you have baseline data.

## Step 3: Add Reflection Loops — Tier 1 (1-2 hours)

This is the highest-ROI first step. For each agent:

1. **Copy the critic prompt** from `self_improvement/reflection_loops/critic_prompt.md`.
2. **Customize it** for the agent's domain (use the department-specific additions as a starting point).
3. **Wire it in** — after the agent produces output but before it emits a completion signal, insert a call to the critic prompt. See `self_improvement/reflection_loops/reflection_loop.py` for the pattern.
4. **Handle the verdict**:
   - `pass` → emit `done`
   - `revise` → revise once, then emit `done` or `needs-review`
   - `escalate` → emit `needs-review`

Start with 1-2 departments (we recommend Build and Growth). Expand once you see the pattern working.

## Step 4: Set Up Episode Logging (1-2 hours)

Before you can evaluate quality trends, you need data.

1. **Define your log storage** — `.jsonl` files work fine to start. One file per department per day.
2. **Implement the logger** — see `docs/logging_and_episodes.md` for the schema and `self_improvement/evaluation/episode_schema.yaml` for the full field list.
3. **Log at minimum**: task_id, department, agent_id, task_description, result signal, reflection verdict.
4. **Verify** by running a few tasks and checking the log files.

## Step 5: Add Evaluation — Tier 2 (2-4 hours)

Once you have 20+ logged episodes per department:

1. **Review the rubrics** in `self_improvement/evaluation/rubrics.yaml`. Adjust criteria and weights for your departments.
2. **Set up the evaluator** — after episodes are logged, run the evaluator prompt from `self_improvement/evaluation/evaluator_prompt.md` to score them.
3. **Calibrate** — have humans score 20-30 episodes and compare with the automated evaluator. Adjust until correlation is acceptable (> 0.7).
4. **Track trends** — compute rolling averages per department. Set up alerts for declining quality.

## Step 6: Enable Policy Adaptation — Tier 3 (When Ready)

See [`docs/optional_paths.md`](optional_paths.md) for detailed prerequisites. In short:

- Don't enable this until Tier 2 is stable.
- Ensure you have a human review process for proposed changes.
- Start with low-risk changes only (prompt clarifications, checklist additions).

## Quick Reference: What to Edit First

| Priority | File | Action |
|---|---|---|
| 1 | `GOALS.md` | Fill in all bold placeholders |
| 2 | `AGENTS.md` | Add/remove departments to match your team |
| 3 | `config/policies/spawn_rules.yaml` | Set your actual spawn permissions |
| 4 | `config/policies/escalation_rules.yaml` | Set your escalation thresholds |
| 5 | `config/prompts/foreman.md` | Customize for your Foreman's actual behavior |
| 6 | `config/prompts/department_head.md` | One copy per department, customized |
| 7 | `self_improvement/reflection_loops/critic_prompt.md` | Customize critic for your first department |

## Common Questions

**Q: Do I need to use Python?**
No. The `.py` files are stubs illustrating patterns. Implement in whatever language your agent system uses.

**Q: Can I skip Tier 1 and go straight to Tier 2?**
You can, but Tier 1 is nearly free (one extra LLM call) and catches obvious issues. Start there.

**Q: How many episodes do I need before Tier 3 is useful?**
At least 50 per department with Tier 2 scores. Fewer than that and the meta-agent won't have enough signal.

**Q: Can I use this with LangChain / CrewAI / AutoGen / etc.?**
Yes. This template defines patterns and configs, not a runtime. Map the concepts onto your framework's abstractions.

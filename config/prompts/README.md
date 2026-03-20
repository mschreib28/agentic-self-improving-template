# Config: Prompts

System and role prompts for every agent in the hierarchy. These are the **versioned source of truth** for agent behavior.

## Conventions

- Each prompt file is a `.md` file with **YAML front matter** containing metadata:
  - `version` — semantic version, bumped on every change
  - `role` — which agent role this prompt is for
  - `department` — which department (or `system` for cross-cutting)
  - `updated` — ISO date of last change
- The body is the actual system prompt in Markdown.
- Comments in the prompt (HTML `<!-- -->`) explain design choices to human editors.

## Files

| File | For | Description |
|---|---|---|
| `foreman.md` | Foreman (R2) | Top-level orchestrator prompt |
| `department_head.md` | All dept. heads | Template prompt (parameterized by department) |
| `sub_agent.md` | All sub-agents | Template prompt (parameterized by task type) |

## How Agents Load Prompts

1. Agent starts up and reads its prompt file from this directory.
2. The prompt loader fills in template variables (`{{department}}`, `{{tools}}`, etc.) from `config/policies/`.
3. If a prompt version changes, the agent reloads on next invocation.

## Editing Prompts

- **Manual edits**: change the file, bump the version, note the change.
- **Meta-agent proposals** (Tier 3): the meta-agent in `self_improvement/policy_updates/` proposes diffs. These go through human review before being applied via `policy_diff.py`.
- **Never edit without bumping the version.** The version trail is how you track what changed and roll back if needed.

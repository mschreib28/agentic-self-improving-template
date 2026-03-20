# Config: Policies

Machine-readable YAML configs that govern agent behavior, permissions, and constraints.

## Files

| File | Purpose |
|---|---|
| `spawn_rules.yaml` | Who can spawn whom, concurrency limits |
| `escalation_rules.yaml` | When and how agents escalate issues |

## How Policies Are Used

1. **At agent startup**: The agent loader reads the relevant policy files to configure permissions and constraints.
2. **At runtime**: Agents check policies before spawning sub-agents or escalating.
3. **By the meta-agent** (Tier 3): Policy files are inputs to the improvement analysis and targets for proposed changes.

## Editing Policies

- Policies are versioned (see `version` field in each file).
- Manual edits: change the value, bump the version.
- Meta-agent proposals: reviewed by a human before applying.
- Keep a change log (comment or separate file) for audit trails.

# Example: Build Agent

## Overview

This example shows a code-generation-and-review loop with:

- A **Build Head** agent that receives implementation tasks.
- A **Build sub-agent** that generates code.
- A **Review sub-agent** that critiques the code and runs tests.
- A **single revision pass** where the build agent fixes issues.
- **Episode logging** and optional guideline updates.

## Architecture

```
Build Head receives task from Foreman
  │
  ├─► 1. Build Sub-Agent: generates code
  │
  ├─► 2. Review Sub-Agent: critiques + runs tests
  │       ├─ All good → done
  │       └─ Issues found → feedback to Build Sub-Agent
  │
  ├─► 3. Build Sub-Agent: revises based on feedback (max 1 revision)
  │
  ├─► 4. Review Sub-Agent: re-reviews revised code
  │       ├─ Pass → done
  │       └─ Fail → needs-review (escalate to human)
  │
  └─► 5. Build Head: logs episode, optionally flags for guideline update
```

## Files

| File | Purpose |
|---|---|
| `build_agent.py` | Python stub implementing the build-review-revise loop |
| `review_agent.py` | Python stub for the code review sub-agent |

## Key Pattern: Review-Then-Revise

This is the recommended pattern for any generative task where quality matters:

1. **Generate first draft** — the build agent writes code based on the task spec.
2. **Independent review** — a separate review agent (different prompt, different perspective) critiques the output.
3. **One revision** — the build agent revises based on specific feedback. Only one revision to prevent infinite loops.
4. **Final check** — the review agent verifies the revision. If it still fails, escalate rather than loop.

## Adapting This Example

- Plug in actual file I/O, test runners, and linters.
- Adjust the review prompt for your project's coding standards.
- The guideline update mechanism feeds into the Tier 3 meta-agent (see `self_improvement/policy_updates/`).

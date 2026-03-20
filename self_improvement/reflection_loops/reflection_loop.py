"""
Reflection loop stub — Tier 1 self-improvement.

Wire this into your agent's execution flow between task completion
and completion signal emission.

Replace the placeholder functions with your actual LLM client,
logging, and signal emission logic.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Verdict(Enum):
    PASS = "pass"
    REVISE = "revise"
    ESCALATE = "escalate"


class Signal(Enum):
    DONE = "done"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs-review"


@dataclass
class CriticResult:
    verdict: Verdict
    score: float
    issues: list[dict[str, str]]
    summary: str


@dataclass
class Episode:
    task_id: str
    department: str
    agent_id: str
    task_description: str
    output: Any
    reflection: CriticResult | None = None
    signal: Signal | None = None


# ---------------------------------------------------------------------------
# Replace these stubs with your actual implementations
# ---------------------------------------------------------------------------

def call_llm(prompt: str) -> dict:
    """Call your LLM and return parsed JSON. Swap in your client."""
    raise NotImplementedError("Plug in your LLM client here")


def load_critic_prompt(department: str) -> str:
    """Load the critic prompt template for a department.

    In production, read from config/prompts/ or self_improvement/reflection_loops/critic_prompt.md
    and fill in department-specific additions.
    """
    raise NotImplementedError("Load and template the critic prompt")


def log_episode(episode: Episode) -> None:
    """Append episode to the episode log (.jsonl)."""
    raise NotImplementedError("Implement episode logging — see docs/logging_and_episodes.md")


def emit_signal(signal: Signal, episode: Episode) -> None:
    """Emit a completion signal to the parent agent."""
    raise NotImplementedError("Implement signal emission for your framework")


# ---------------------------------------------------------------------------
# Core reflection loop
# ---------------------------------------------------------------------------

def run_reflection(
    task_id: str,
    department: str,
    agent_id: str,
    task_description: str,
    task_constraints: str,
    agent_output: Any,
    max_revisions: int = 1,
) -> Episode:
    """Execute the reflection loop on an agent's output.

    Flow:
      1. Run critic prompt on the output.
      2. If pass → done.
      3. If revise → revise once, re-critique, then done or needs-review.
      4. If escalate → needs-review immediately.
    """
    episode = Episode(
        task_id=task_id,
        department=department,
        agent_id=agent_id,
        task_description=task_description,
        output=agent_output,
    )

    critic_prompt = load_critic_prompt(department)
    prompt = critic_prompt.replace("{{department}}", department)
    prompt = prompt.replace("{{task_description}}", task_description)
    prompt = prompt.replace("{{task_constraints}}", task_constraints)
    prompt = prompt.replace("{{agent_output}}", str(agent_output))

    critic_response = call_llm(prompt)
    result = CriticResult(
        verdict=Verdict(critic_response["verdict"]),
        score=critic_response["score"],
        issues=critic_response["issues"],
        summary=critic_response["summary"],
    )
    episode.reflection = result

    match result.verdict:
        case Verdict.PASS:
            episode.signal = Signal.DONE

        case Verdict.REVISE:
            if max_revisions > 0:
                revised_output = _revise(agent_output, result.issues, department)
                episode.output = revised_output

                # Re-run critic on revised output
                prompt = prompt.replace(str(agent_output), str(revised_output))
                re_critique = call_llm(prompt)
                re_result = CriticResult(
                    verdict=Verdict(re_critique["verdict"]),
                    score=re_critique["score"],
                    issues=re_critique["issues"],
                    summary=re_critique["summary"],
                )
                episode.reflection = re_result

                if re_result.verdict == Verdict.PASS:
                    episode.signal = Signal.DONE
                else:
                    episode.signal = Signal.NEEDS_REVIEW
            else:
                episode.signal = Signal.NEEDS_REVIEW

        case Verdict.ESCALATE:
            episode.signal = Signal.NEEDS_REVIEW

    log_episode(episode)
    emit_signal(episode.signal, episode)
    return episode


def _revise(original_output: Any, issues: list[dict[str, str]], department: str) -> Any:
    """Ask the agent to revise its output based on critic feedback.

    In production, this calls the same agent LLM with the issues as
    additional context.
    """
    revision_prompt = (
        f"You are a {department} agent. Your previous output had these issues:\n\n"
    )
    for issue in issues:
        revision_prompt += f"- [{issue['severity']}] {issue['description']}\n"
        revision_prompt += f"  Suggestion: {issue['suggestion']}\n"

    revision_prompt += (
        "\nPlease produce a revised version that addresses these issues.\n\n"
        f"Original output:\n{original_output}"
    )
    return call_llm(revision_prompt)

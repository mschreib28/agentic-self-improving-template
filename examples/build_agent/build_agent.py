"""
Build agent example — code generation with review-revise loop.

Demonstrates:
  - Code generation from a task spec
  - Independent code review
  - Single-pass revision based on feedback
  - Episode logging with quality scores
  - Optional guideline update flagging

Replace stub functions with your actual implementations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from review_agent import ReviewResult, review_code


@dataclass
class BuildTask:
    task_id: str
    description: str
    requirements: list[str]
    target_files: list[str]
    test_command: str | None = None
    coding_standards: str | None = None


@dataclass
class BuildOutput:
    files: dict[str, str]  # filename → content
    test_results: str | None = None
    build_log: str | None = None


@dataclass
class BuildEpisode:
    task_id: str
    agent_id: str
    first_draft: BuildOutput
    review: ReviewResult
    revision: BuildOutput | None = None
    re_review: ReviewResult | None = None
    final_signal: str = "done"
    evaluation_score: float = 0.0
    guideline_flag: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Stubs — replace with real implementations
# ---------------------------------------------------------------------------

def call_llm(prompt: str) -> dict:
    """Call your LLM and return parsed response."""
    raise NotImplementedError("Plug in your LLM client")


def run_tests(command: str, files: dict[str, str]) -> str:
    """Run the test suite. Returns stdout/stderr."""
    raise NotImplementedError("Plug in your test runner")


def read_file(path: str) -> str:
    """Read a source file from the project."""
    raise NotImplementedError("Plug in file I/O")


def write_files(files: dict[str, str]) -> None:
    """Write generated files to the project."""
    raise NotImplementedError("Plug in file I/O")


def log_episode(episode: BuildEpisode) -> None:
    """Append episode to build department episode log."""
    raise NotImplementedError("Implement .jsonl logging")


# ---------------------------------------------------------------------------
# Build sub-agent: Code generation
# ---------------------------------------------------------------------------

CODE_GENERATION_PROMPT = """You are a senior software engineer.

## Task
{description}

## Requirements
{requirements}

## Existing Code Context
{context}

## Coding Standards
{standards}

## Instructions
1. Write clean, well-tested code that fulfills all requirements.
2. Include unit tests.
3. Follow the coding standards provided.

Respond with JSON:
{{
  "files": {{
    "path/to/file.py": "file contents...",
    "path/to/test_file.py": "test contents..."
  }},
  "explanation": "Brief explanation of approach"
}}
"""


def generate_code(task: BuildTask) -> BuildOutput:
    """Have the build sub-agent generate code for the task."""
    context_parts = []
    for f in task.target_files:
        try:
            context_parts.append(f"### {f}\n```\n{read_file(f)}\n```")
        except (FileNotFoundError, NotImplementedError):
            context_parts.append(f"### {f}\n(new file)")

    prompt = CODE_GENERATION_PROMPT.format(
        description=task.description,
        requirements="\n".join(f"- {r}" for r in task.requirements),
        context="\n\n".join(context_parts) if context_parts else "(no existing files)",
        standards=task.coding_standards or "(use best practices)",
    )

    result = call_llm(prompt)

    test_results = None
    if task.test_command:
        test_results = run_tests(task.test_command, result["files"])

    return BuildOutput(
        files=result["files"],
        test_results=test_results,
    )


# ---------------------------------------------------------------------------
# Build sub-agent: Revision based on review feedback
# ---------------------------------------------------------------------------

REVISION_PROMPT = """You are a senior software engineer revising code based on review feedback.

## Original Task
{description}

## Your Previous Code
{previous_code}

## Review Feedback
{feedback}

## Issues to Fix
{issues}

## Instructions
1. Address EVERY issue listed above.
2. Do not introduce new issues.
3. Keep changes minimal — only fix what was flagged.

Respond with the same JSON format:
{{
  "files": {{
    "path/to/file.py": "revised file contents...",
  }},
  "changes_made": ["list of specific changes"]
}}
"""


def revise_code(task: BuildTask, original: BuildOutput, review: ReviewResult) -> BuildOutput:
    """Revise code based on review feedback."""
    previous_code = "\n\n".join(
        f"### {path}\n```\n{content}\n```"
        for path, content in original.files.items()
    )

    issues = "\n".join(
        f"- [{i['severity']}] {i['description']}: {i['suggestion']}"
        for i in review.issues
    )

    prompt = REVISION_PROMPT.format(
        description=task.description,
        previous_code=previous_code,
        feedback=review.summary,
        issues=issues,
    )

    result = call_llm(prompt)

    test_results = None
    if task.test_command:
        test_results = run_tests(task.test_command, result["files"])

    return BuildOutput(
        files=result["files"],
        test_results=test_results,
    )


# ---------------------------------------------------------------------------
# Build Head: Orchestration
# ---------------------------------------------------------------------------

def run_build_task(task: BuildTask, agent_id: str = "build-sub-001") -> BuildEpisode:
    """Full build loop: generate → review → revise → re-review → log.

    This is what the Build Head executes when it receives a task.
    """
    # Step 1: Generate first draft
    first_draft = generate_code(task)

    # Step 2: Independent review
    review = review_code(task, first_draft)

    episode = BuildEpisode(
        task_id=task.task_id,
        agent_id=agent_id,
        first_draft=first_draft,
        review=review,
    )

    if review.verdict == "pass":
        episode.final_signal = "done"
        episode.evaluation_score = review.score
    else:
        # Step 3: Revise based on feedback (max 1 revision)
        revision = revise_code(task, first_draft, review)
        episode.revision = revision

        # Step 4: Re-review
        re_review = review_code(task, revision)
        episode.re_review = re_review

        if re_review.verdict == "pass":
            episode.final_signal = "done"
            episode.evaluation_score = re_review.score
        else:
            episode.final_signal = "needs-review"
            episode.evaluation_score = re_review.score

    # Step 5: Check if this episode should flag a guideline update
    episode.guideline_flag = _check_guideline_flag(episode)

    log_episode(episode)
    return episode


def _check_guideline_flag(episode: BuildEpisode) -> str | None:
    """Determine if this episode reveals a pattern worth updating guidelines for.

    Flags episodes where:
    - The same issue type appeared in both review and re-review (persistent pattern)
    - The test suite caught something the review missed
    - The revision introduced new issues
    """
    if not episode.review or not episode.re_review:
        return None

    first_issue_types = {i["description"] for i in episode.review.issues}
    second_issue_types = {i["description"] for i in episode.re_review.issues}
    persistent = first_issue_types & second_issue_types

    if persistent:
        return f"Persistent issues across revision: {persistent}"

    if episode.re_review.score < episode.review.score:
        return "Revision degraded quality — review revision prompt"

    return None

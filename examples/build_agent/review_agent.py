"""
Review sub-agent — independent code review.

This agent is invoked by the Build Head to review code produced by
the Build sub-agent. It operates independently with its own prompt
and criteria.
"""

from dataclasses import dataclass


@dataclass
class ReviewResult:
    verdict: str  # pass | revise | escalate
    score: float  # 1-5
    issues: list[dict[str, str]]  # severity, description, suggestion
    summary: str
    tests_passed: bool


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

def call_llm(prompt: str) -> dict:
    """Call your LLM and return parsed response."""
    raise NotImplementedError("Plug in your LLM client")


# ---------------------------------------------------------------------------
# Review prompt
# ---------------------------------------------------------------------------

REVIEW_PROMPT = """You are a senior code reviewer. Review this code strictly and thoroughly.

## Task Requirements
{requirements}

## Code to Review
{code}

## Test Results
{test_results}

## Coding Standards
{standards}

## Review Criteria
1. **Correctness**: Does the code fulfill all requirements?
2. **Tests**: Are there sufficient tests? Do they pass?
3. **Code quality**: Is the code readable, maintainable, and idiomatic?
4. **Edge cases**: Are error states and boundary conditions handled?
5. **Security**: Any obvious vulnerabilities?

## Response Format
{{
  "verdict": "pass | revise | escalate",
  "score": <1-5>,
  "issues": [
    {{
      "severity": "minor | major | critical",
      "description": "What's wrong",
      "suggestion": "How to fix it",
      "file": "which file",
      "line_hint": "approximate location"
    }}
  ],
  "summary": "Overall assessment in 1-2 sentences",
  "tests_passed": true | false
}}

Rules:
- "pass" if score >= 4 and no critical issues.
- "revise" if issues are fixable in one pass.
- "escalate" if fundamental design problems exist.
- Be specific: reference actual code in your issues.
"""


def review_code(task, build_output) -> ReviewResult:
    """Run an independent code review on the build output.

    Args:
        task: The original BuildTask.
        build_output: The BuildOutput to review.
    """
    code_blocks = "\n\n".join(
        f"### {path}\n```\n{content}\n```"
        for path, content in build_output.files.items()
    )

    prompt = REVIEW_PROMPT.format(
        requirements="\n".join(f"- {r}" for r in task.requirements),
        code=code_blocks,
        test_results=build_output.test_results or "(no tests run)",
        standards=task.coding_standards or "(use best practices)",
    )

    result = call_llm(prompt)

    return ReviewResult(
        verdict=result["verdict"],
        score=result["score"],
        issues=result["issues"],
        summary=result["summary"],
        tests_passed=result.get("tests_passed", False),
    )

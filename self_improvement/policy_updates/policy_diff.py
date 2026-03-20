"""
Policy diff utility — generates and applies diffs to versioned config files.

Supports YAML policy files and Markdown prompt files with YAML front matter.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from difflib import unified_diff
from pathlib import Path


@dataclass
class VersionedFile:
    path: str
    version: str
    content: str


def read_versioned_file(path: str) -> VersionedFile:
    """Read a file and extract its version from YAML front matter.

    Expects files to have a `version: "X.Y"` field in YAML front matter
    (between `---` delimiters) or in a YAML comment header.
    """
    content = Path(path).read_text()

    version_match = re.search(r'version:\s*["\']?(\d+\.\d+)["\']?', content)
    version = version_match.group(1) if version_match else "0.0"

    return VersionedFile(path=path, version=version, content=content)


def bump_version(version: str, bump_type: str = "minor") -> str:
    """Increment a version string.

    Args:
        version: Current version (e.g., "1.2")
        bump_type: "minor" (1.2 → 1.3) or "major" (1.2 → 2.0)
    """
    parts = version.split(".")
    major, minor = int(parts[0]), int(parts[1])

    if bump_type == "major":
        return f"{major + 1}.0"
    return f"{major}.{minor + 1}"


def generate_diff(old_content: str, new_content: str, file_path: str) -> str:
    """Generate a unified diff between old and new content."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff = unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
    )
    return "".join(diff)


def apply_versioned_update(
    path: str,
    new_content: str,
    bump_type: str = "minor",
    backup: bool = True,
) -> tuple[str, str]:
    """Apply an update to a versioned config file.

    1. Reads the current file and extracts its version.
    2. Bumps the version.
    3. Updates the version in the new content.
    4. Optionally backs up the old file.
    5. Writes the new file.

    Returns: (new_version, diff)
    """
    current = read_versioned_file(path)
    new_version = bump_version(current.version, bump_type)

    new_content = re.sub(
        r'(version:\s*["\']?)\d+\.\d+(["\']?)',
        f"\\g<1>{new_version}\\2",
        new_content,
    )

    diff = generate_diff(current.content, new_content, path)

    if backup:
        backup_path = f"{path}.v{current.version}.bak"
        Path(backup_path).write_text(current.content)

    Path(path).write_text(new_content)

    return new_version, diff


def create_change_log_entry(
    proposal_id: str,
    file_path: str,
    old_version: str,
    new_version: str,
    diff: str,
    rationale: str,
    approved_by: str,
) -> dict:
    """Create a structured change log entry for auditing."""
    return {
        "proposal_id": proposal_id,
        "timestamp": datetime.now().isoformat(),
        "file_path": file_path,
        "old_version": old_version,
        "new_version": new_version,
        "diff": diff,
        "rationale": rationale,
        "approved_by": approved_by,
    }

#!/usr/bin/env python3
"""PreToolUse guard: any write to .claude/documentation/ requires explicit user approval.

The documentation skills write these files legitimately, so the hook asks instead of denying.
"""
import json
import re
import sys

DOC_DIR = ".claude/documentation/"
# Bash commands that can modify files. Heuristic: catches redirects, in-place edits,
# file moves, and interpreters that may write; plain reads (cat, grep, ls) pass through.
BASH_WRITE = re.compile(
    r"(>|\btee\b|\bsed\s+(-\w*\s+)*-i|\bperl\s+(-\w*\s+)*-i|\bmv\b|\bcp\b|\brm\b|"
    r"\btruncate\b|\bpython3?\b|\bnode\b|\bruby\b|\bgit\s+(checkout|restore|apply)\b)"
)

REASON = (
    "Files in .claude/documentation/ are maintained only by the documentation skills "
    "(refresh-documentation, create-documentation, update-documentation-index). If this write "
    "is not part of one of those skills the user invoked, don't make it: list the affected "
    "doc files and sections in your final summary and recommend running refresh-documentation."
)


def touches_docs(path: str) -> bool:
    path = path.replace("\\", "/")
    return path.startswith(DOC_DIR) or ("/" + DOC_DIR) in path


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}

    if tool == "Bash":
        command = tool_input.get("command", "")
        hit = DOC_DIR.rstrip("/") in command and BASH_WRITE.search(command)
    else:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        hit = touches_docs(path)

    if hit:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": REASON,
                }
            },
            sys.stdout,
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""PreToolUse guard: any write to .claude/documentation/ requires explicit user approval.

The documentation skills write these files legitimately, so the hook asks instead of denying.
Reads pass through: for Bash, only the actual write targets of each simple command (redirect
destinations, tee/sed -i/cp/mv/rm/... operands) are checked against the docs directory.
"""
import json
import shlex
import sys

DOC_DIR = ".claude/documentation"

REASON = (
    "Files in .claude/documentation/ are maintained only by the documentation skills "
    "(refresh-documentation, create-documentation, update-documentation-index). If this write "
    "is not part of one of those skills the user invoked, don't make it: list the affected "
    "doc files and sections in your final summary and recommend running refresh-documentation."
)

SEPARATORS = {";", "&&", "||", "|", "|&", "&", "(", ")", "\n"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", ">&"}
PREFIXES = {"sudo", "env", "command", "nohup", "time", "exec", "xargs"}
# Every operand is a write target (mv removes its source, so all operands count).
ALL_OPERANDS = {"rm", "rmdir", "touch", "truncate", "mkdir", "mv", "tee", "unlink", "shred"}
# Only the last operand is written.
LAST_OPERAND = {"cp", "rsync", "ln", "install", "ditto", "scp"}
# Writes can't be read off the command line; ask whenever they mention the docs dir.
OPAQUE = {"python", "python3", "node", "ruby", "perl", "bash", "sh", "zsh", "awk", "dd"}
GIT_WRITES = {"checkout", "restore", "apply", "rm", "mv", "clean", "stash"}


def touches_docs(path: str) -> bool:
    path = path.replace("\\", "/").rstrip("/")
    return path == DOC_DIR or path.startswith(DOC_DIR + "/") or ("/" + DOC_DIR) in path


def tokenize(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    return list(lexer)


def segments(tokens: list[str]):
    current: list[str] = []
    for token in tokens:
        if token in SEPARATORS:
            if current:
                yield current
            current = []
        else:
            current.append(token)
    if current:
        yield current


def write_targets(segment: list[str]) -> list[str]:
    """Paths a simple command writes to, plus all its words for opaque interpreters."""
    targets: list[str] = []
    words: list[str] = []
    i = 0
    while i < len(segment):
        token = segment[i]
        if token in REDIRECTS and i + 1 < len(segment):
            targets.append(segment[i + 1])
            i += 2
            continue
        if token in {"<", "<<", "<<<"}:
            i += 2
            continue
        words.append(token)
        i += 1

    while words and ("=" in words[0] and not words[0].startswith("-") or words[0] in PREFIXES):
        words.pop(0)
    if not words:
        return targets

    name = words[0].rsplit("/", 1)[-1]
    operands = [w for w in words[1:] if not w.startswith("-")]

    if name in ALL_OPERANDS:
        targets += operands
    elif name in LAST_OPERAND:
        targets += operands[-1:]
    elif name in {"sed", "gsed"} and any(w.startswith("-i") or w == "--in-place" for w in words):
        targets += operands
    elif name == "perl" and any(w.startswith("-") and "i" in w for w in words[1:]):
        targets += operands
    elif name in OPAQUE or name.startswith("python"):
        targets += words[1:]
    elif name == "find" and any(w in {"-delete", "-exec", "-execdir"} for w in words):
        targets += words[1:]
    elif name == "git" and len(words) > 1 and words[1] in GIT_WRITES:
        targets += words[2:]
    return targets


def bash_writes_docs(command: str) -> bool:
    if DOC_DIR not in command:
        return False
    try:
        tokens = tokenize(command)
    except ValueError:
        return True  # unparseable (e.g. unbalanced quotes) and mentions docs: fail closed
    return any(
        mentions_docs(target) for segment in segments(tokens) for target in write_targets(segment)
    )


def mentions_docs(word: str) -> bool:
    """A word may be a bare path or embed one (python -c "open('.../a.md')")."""
    return DOC_DIR + "/" in word or word.rstrip("/").endswith(DOC_DIR)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}

    if tool == "Bash":
        hit = bash_writes_docs(tool_input.get("command", ""))
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

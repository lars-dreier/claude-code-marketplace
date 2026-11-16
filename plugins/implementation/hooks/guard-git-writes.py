#!/usr/bin/env python3
"""PreToolUse guard for the implement-feature skill: git commands that change history or discard
work require explicit user approval.

Registered in the skill's frontmatter, so it runs from the skill's invocation until the session
ends. It asks instead of denying, so a commit the developer requests later in the session can
still be approved.
"""
import json
import re
import shlex
import sys

REASON = (
    "implement-feature leaves commits and other history or working-tree changes to the developer. "
    "Unless the developer asked for this exact command in this conversation, don't run it: give "
    "them the command to run themselves."
)

GUARDED = {
    "commit", "push", "reset", "rebase", "merge", "cherry-pick", "revert", "am",
    "stash", "checkout", "switch", "restore", "clean",
}
STASH_READ_ONLY = {"list", "show"}
BRANCH_DESTRUCTIVE = {"-d", "-D", "--delete", "-f", "--force", "-m", "-M", "--move"}
# Global options that take their value as the next word (`git -C <path> commit`).
GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}

SEPARATORS = {";", "&&", "||", "|", "|&", "&", "(", ")", "\n"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", ">&", "<", "<<", "<<<"}
PREFIXES = {"sudo", "env", "command", "nohup", "time", "exec", "xargs"}
# Commands can't be read off these command lines; fall back to a text match on their arguments.
OPAQUE = {"bash", "sh", "zsh", "eval", "python", "python3", "node", "ruby", "perl"}
TEXT_MATCH = re.compile(
    r"\bgit\b.*?\b(" + "|".join(re.escape(s) for s in sorted(GUARDED)) + r")\b", re.DOTALL
)


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


def command_words(segment: list[str]) -> list[str]:
    """The words of a simple command, without redirects, env assignments and prefixes."""
    words: list[str] = []
    i = 0
    while i < len(segment):
        if segment[i] in REDIRECTS:
            i += 2
            continue
        words.append(segment[i])
        i += 1
    while words and (("=" in words[0] and not words[0].startswith("-")) or words[0] in PREFIXES):
        words.pop(0)
    return words


def git_is_guarded(args: list[str]) -> bool:
    """args: the words after `git`."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in GLOBAL_WITH_VALUE else 1
    if i >= len(args):
        return False
    sub, rest = args[i], args[i + 1:]
    if sub == "stash":
        operands = [w for w in rest if not w.startswith("-")]
        return not (operands and operands[0] in STASH_READ_ONLY)
    if sub == "branch":
        return any(w in BRANCH_DESTRUCTIVE for w in rest)
    return sub in GUARDED


def segment_is_guarded(segment: list[str]) -> bool:
    words = command_words(segment)
    if not words:
        return False
    name = words[0].rsplit("/", 1)[-1]
    if name == "git":
        return git_is_guarded(words[1:])
    if name in OPAQUE or name.startswith("python"):
        return any(TEXT_MATCH.search(w) for w in words[1:])
    return False


def bash_is_guarded(command: str) -> bool:
    if "git" not in command:
        return False
    try:
        tokens = tokenize(command)
    except ValueError:
        return bool(TEXT_MATCH.search(command))  # unparseable: fail closed on a text match
    return any(segment_is_guarded(segment) for segment in segments(tokens))


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    if event.get("tool_name") != "Bash":
        return
    command = (event.get("tool_input") or {}).get("command", "")
    if bash_is_guarded(command):
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

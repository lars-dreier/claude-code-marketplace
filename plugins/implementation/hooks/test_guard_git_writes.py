"""Tests for guard-git-writes.py. Run: python3 -m unittest discover plugins/implementation/hooks"""
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "guard_git_writes", Path(__file__).with_name("guard-git-writes.py")
)
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


def decision(tool: str, tool_input: dict) -> str | None:
    stdin, stdout = sys.stdin, sys.stdout
    sys.stdin = io.StringIO(json.dumps({"tool_name": tool, "tool_input": tool_input}))
    sys.stdout = io.StringIO()
    try:
        guard.main()
        out = sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout = stdin, stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else None


def bash(command: str) -> str | None:
    return decision("Bash", {"command": command})


class ReadOnlyPassesThrough(unittest.TestCase):
    def test_read_only(self):
        for cmd in [
            "git status --porcelain",
            "git log -n 30 --format='%s%n%b%n---'",
            "git diff --stat abc123..HEAD",
            "git show HEAD",
            "git rev-parse --short HEAD",
            "git merge-base --is-ancestor abc123 HEAD",
            "git check-ignore .claude/feature-briefs/x-implementation-plan.md",
            "git branch --show-current",
            "git branch -a",
            "git stash list",
            "git stash show -p stash@{0}",
            "git -C /repo log --oneline",
            "git log --grep='commit message'",
            "echo 'remember to commit' && git status",
            "npm test",
            "./gradlew test",
            "",
        ]:
            with self.subTest(cmd=cmd):
                self.assertIsNone(bash(cmd))


class WritesAsk(unittest.TestCase):
    def test_guarded(self):
        for cmd in [
            "git commit -m 'Add x'",
            "git add -A && git commit -m x",
            "git push",
            "git push origin develop",
            "git -C . push",
            "git -c push.default=current push",
            "git --no-pager commit --amend",
            "git --git-dir=.git commit -m x",
            "GIT_AUTHOR_NAME=x git commit -m x",
            "/usr/bin/git commit -m x",
            "sudo git reset --hard",
            "git reset HEAD~1",
            "git rebase -i main",
            "git merge feature",
            "git cherry-pick abc",
            "git revert HEAD",
            "git am patch.mbox",
            "git stash",
            "git stash push -m wip",
            "git stash pop",
            "git checkout -- file.txt",
            "git switch main",
            "git restore src/a.ts",
            "git clean -fd",
            "git branch -D old",
            "git status; git commit -m x",
            "bash -c 'git commit -m x'",
            "sh -c \"git push\"",
            "git commit -m 'unbalanced",
        ]:
            with self.subTest(cmd=cmd):
                self.assertEqual(bash(cmd), "ask")


class OtherTools(unittest.TestCase):
    def test_non_bash_ignored(self):
        self.assertIsNone(decision("Edit", {"file_path": "/repo/a.ts", "new_string": "git commit"}))
        self.assertIsNone(decision("Write", {"file_path": "/repo/b.md", "content": "git push"}))


if __name__ == "__main__":
    unittest.main()

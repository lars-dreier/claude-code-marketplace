"""Tests for guard-documentation.py. Run: python3 -m unittest discover plugins/documentation/hooks"""
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "guard_documentation", Path(__file__).with_name("guard-documentation.py")
)
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)

DOCS = "/repo/.claude/documentation"


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


class ReadsPassThrough(unittest.TestCase):
    def test_reads(self):
        for cmd in [
            f"cat {DOCS}/index.md 2>&1 | head -50",
            f"ls {DOCS}/ /other/.claude/documentation/ 2>&1; cat /x/SKILL.md",
            f"grep -rn foo {DOCS} > /tmp/out.txt",
            f"cat {DOCS}/a.md >/dev/null 2>&1",
            f"cp {DOCS}/a.md /tmp/a.md",
            f"rsync -a {DOCS}/ /tmp/backup/",
            f"sed -n '1,20p' {DOCS}/a.md",
            f"git diff -- {DOCS}",
            f"find {DOCS} -name '*.md' | wc -l",
            "echo hi > /tmp/x",
        ]:
            with self.subTest(cmd=cmd):
                self.assertIsNone(bash(cmd))


class WritesAsk(unittest.TestCase):
    def test_writes(self):
        for cmd in [
            f"echo x > {DOCS}/a.md",
            f"echo x >> {DOCS}/a.md",
            f"echo x>{DOCS}/a.md",
            f"echo x &> {DOCS}/a.md",
            f"cat /tmp/a | tee {DOCS}/a.md",
            f"tee -a {DOCS}/a.md < /tmp/a",
            f"sed -i '' 's/a/b/' {DOCS}/a.md",
            f"sed -i.bak 's/a/b/' {DOCS}/a.md",
            f"perl -pi -e 's/a/b/' {DOCS}/a.md",
            f"cp /tmp/a.md {DOCS}/a.md",
            f"mv {DOCS}/a.md /tmp/a.md",
            f"rm -rf {DOCS}",
            f"touch {DOCS}/new.md",
            f"truncate -s 0 {DOCS}/a.md",
            f"git checkout -- {DOCS}/a.md",
            f"git restore {DOCS}",
            f"python3 -c \"open('{DOCS}/a.md','w')\"",
            f"ls && echo x > {DOCS}/a.md",
            f"cat <<'EOF' > {DOCS}/a.md\nhello\nEOF",
            "echo x > .claude/documentation/a.md",
            'echo "unterminated > .claude/documentation/a.md',
        ]:
            with self.subTest(cmd=cmd):
                self.assertEqual(bash(cmd), "ask")


class FileTools(unittest.TestCase):
    def test_doc_paths_ask(self):
        self.assertEqual(decision("Edit", {"file_path": f"{DOCS}/a.md"}), "ask")
        self.assertEqual(decision("Write", {"file_path": ".claude/documentation/a.md"}), "ask")

    def test_other_paths_pass(self):
        self.assertIsNone(decision("Edit", {"file_path": "/repo/src/a.py"}))


if __name__ == "__main__":
    unittest.main()

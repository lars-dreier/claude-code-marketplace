---
name: check-documentation-index
description: >
  Reads `.claude/documentation/index.md` and loads the project documentation relevant to the
  current task, using each entry's description and "Use when" guidance to decide what to read.
  Use at the start of an implementation, debugging, or exploration task to prime context, or
  when the user says "check the documentation", "load the docs", "initialize documentation",
  "what docs are relevant", "read the project docs", or any variation.
allowed-tools:
  - Read
---

# Check Documentation Index

Initialize the project documentation for the current task.

Read `.claude/documentation/index.md` and then read the documentation files relevant to the
task at hand. The index lists all available documentation with descriptions and "Use when"
guidance to help you decide what to read.

If `.claude/documentation/index.md` does not exist, tell the user no documentation index is
present and suggest running the **create-documentation** skill (or **update-documentation-index**
if documentation files already exist without an index). Then stop.

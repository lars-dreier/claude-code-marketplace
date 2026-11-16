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

1. Read `<working directory>/.claude/documentation/index.md` with the **Read** tool, using the
   absolute path built from the directory Claude Code was launched in. Read the whole file;
   don't pass `limit`.
2. From each entry's description and "Use when" list, pick the files relevant to the task at
   hand and read them with the **Read** tool. Independent reads go in one parallel batch.

Use only the Read tool for these files: no Bash (`cat`, `head`, `ls`, `find`), no Glob or Grep,
and no searching for other `.claude/documentation/` directories in subfolders or sibling
projects. The index is the only entry point; the files it doesn't list are not part of the
documentation.

If the Read tool reports that `index.md` does not exist, tell the user no documentation index is
present and suggest running the **create-documentation** skill (or **update-documentation-index**
if documentation files already exist without an index). Then stop.

## Documentation is read-only for this task

Don't edit, create, or delete files in `.claude/documentation/`, by any means (Edit, Write, or
Bash), even if an approved plan lists them. They are maintained only by the documentation
skills (**refresh-documentation**, **create-documentation**, **update-documentation-index**),
which rewrite them from the code in a consistent style; hand edits drift from that style and get
overwritten on the next refresh.

When your changes make a documentation file inaccurate, leave it as is and keep working. In
your final summary, list each affected file and section and what is now wrong, and recommend
running **refresh-documentation**. Don't propose doc edits in your plan.
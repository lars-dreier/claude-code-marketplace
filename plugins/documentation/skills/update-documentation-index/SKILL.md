---
name: update-documentation-index
description: >
  Regenerates `.claude/documentation/index.md` from the documentation files on disk, producing
  a concise, scannable index where each entry has a 1–2 sentence description and a "Use when"
  bullet list. Use when documentation files have been added, removed, or significantly changed,
  or when the user says "update the documentation index", "regenerate the docs index",
  "rebuild index.md", "refresh the docs index", or any variation.
allowed-tools:
  - Glob
  - Read
  - Write
---

# Update Documentation Index

Regenerate the documentation index when documentation files are added, removed, or
significantly changed.

## Your Task

Regenerate `.claude/documentation/index.md` by following the steps below.

### Step 1: Scan Documentation Directory

1. Use the Glob tool to find all `.md` files in `.claude/documentation/` directory
2. Exclude `index.md` itself from the scan
3. Sort files alphabetically for consistent ordering

### Step 2: Read File Purposes

For each documentation file found:

1. Read the first 15-20 lines to understand the file's purpose
2. Extract the main heading and key topics covered
3. Identify when this documentation should be used

### Step 3: Regenerate Index

Create a new `index.md` file following the established format:

**Format requirements:**

- Total file length: under 60 lines
- Information-dense but concise
- Each file entry includes:
    - File name as markdown link
    - 1-2 sentence description
    - "Use when:" bullet list (2-4 specific scenarios)
- No lengthy explanations or multiple examples
- Quick reference style - scannable in 2-3 seconds

**Entry template:**

```markdown
## [filename.md](filename.md)

Brief description of content (1-2 sentences).

**Use when:**

- Specific scenario 1
- Specific scenario 2
- Specific scenario 3
```

### Step 4: Verify Index Quality

After regenerating, verify:

- File is under 60 lines (read `index.md` and check the line numbers shown by the Read tool)
- All documentation files are listed (except index.md itself)
- Each entry has description and "Use when" bullets
- Format is consistent across all entries
- Information is actionable and specific

## Important Notes

- This is a maintenance task - use direct file operations (Glob, Read, Write)
- Do NOT launch exploration agents or research agents
- Preserve the concise, information-dense style of the original index
- Each entry should help Claude quickly decide which documentation to read
- The index should be a quick reference guide, not a comprehensive manual
- If the line count exceeds 60 lines, condense descriptions while keeping them actionable

After completing the update, inform the user:

- The path to the updated index file
- The line count of the new index
- The number of documentation files indexed

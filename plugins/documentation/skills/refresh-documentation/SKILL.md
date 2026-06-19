---
name: refresh-documentation
description: >
  Re-analyzes the codebase and rewrites any `.claude/documentation/` file whose content has
  drifted from the source code, then refreshes the index and validates each file's frontmatter
  and table of contents. Use when the user says "refresh documentation", "update the docs",
  "the docs are stale", "sync documentation with the code", "bring the docs up to date", or any
  variation asking to reconcile existing project documentation with the current codebase.
allowed-tools:
  - Glob
  - Grep
  - Read
  - Write
  - Bash
  - Agent
---

# Refresh Documentation

The primary job of this skill is to **re-analyze the codebase and rewrite any documentation whose
content no longer accurately reflects the source code**. Frontmatter and index hygiene are
secondary concerns handled at the end.

## Your Task

Follow these steps in order. Carry data forward — do not repeat tool calls you have already made.

### Step 1: Collect Documentation Files and Recent Git Changes

In a **single message**, issue these tool calls in parallel:

- `Glob: .claude/documentation/*.md` — collect all `.md` files (save this list, reuse throughout)
- `Read: .claude/documentation/index.md` — read the current index
- `Read: .claude/documentation/last_refresh` — read the timestamp of the last documentation refresh

If the Glob returns **no files at all**: inform the user that no documentation exists yet and suggest running
the **create-documentation** skill first. Stop here.

If `index.md` does not exist (Read fails): treat the index as missing.

If `last_refresh` exists, use its timestamp in the git log command. If it does not exist, fall back to `90 days ago`.
In a follow-up tool call:

- `Bash: git log --name-only --pretty=format: --since="<timestamp or '90 days ago'>" | sort -u | grep -v '^$'` —
  collect all source files changed since the last refresh (used to focus sub-agent analysis)

### Step 2: Read All Documentation Files

**Read all doc files (excluding `index.md`) in a single parallel message.**

For each file, extract:
- The `last_updated` value from frontmatter (used to scope git history per file in Step 3)
- All section headings and body content (passed directly to sub-agents so they do not re-read)

### Step 3: Re-Analyze the Codebase and Update Stale Docs

This is the core step. Launch one **Explore sub-agent per documentation file**, all in parallel in a single message.

**For each sub-agent, include in its prompt:**
- The full current content of the doc file (already read in Step 2 — do not make the sub-agent re-read it)
- The `last_updated` date from its frontmatter — **for git scoping only**, not to be reused as the new timestamp
- The list of source files changed since `last_updated` (filter the git log from Step 1 by date if needed, or pass
  the full list for the sub-agent to cross-reference against the doc's scope)
- The current UTC date and time in ISO 8601 format (e.g. `2026-03-25T10:42:00Z`) — to be used as the new
  `last_updated` value if a rewrite is needed. Do NOT reuse the old `last_updated` value for this purpose.
  If the exact UTC time is not available from context, run `date -u +%Y-%m-%dT%H:%M:%SZ` to obtain it before
  passing it to sub-agents.

**Each sub-agent must:**

1. **Understand the doc's scope** from the content passed in — title, description, section headings.

2. **Focus on changed source files first** — cross-reference the changed-files list against the areas the doc covers.
   Then use Glob and Grep to read the current state of relevant source files.

3. **Compare doc content against current code:**
   - Are described APIs, functions, or classes still present and named correctly?
   - Do described behaviors, parameters, or return values still match?
   - Are there new significant additions (endpoints, config options, renamed modules) not mentioned?
   - Are there sections documenting things that no longer exist?

4. **Return a verdict:**
   - `UP_TO_DATE` — content accurately reflects the current code.
   - `STALE: <one-line summary of what changed>` — followed by the **complete rewritten file content** including:
     - Valid YAML frontmatter (`title`, `description`, `category`, `tags`, `last_updated` set to the current UTC
       timestamp passed in — not the old value from the existing file, `related_docs`)
     - A `## Table of Contents` section immediately after the `#` title, separated from the first body section by `---`
     - Full updated body content

Once all sub-agents complete, write all rewritten files in a **single parallel message**.

> **Important:** Sub-agents must re-analyze actual source code — not just rephrase what was already in the doc.
> The goal is to catch drift between documentation and code, not to reformat existing text.

### Step 4: Update the Index

Always regenerate `index.md` if **any** doc was rewritten in Step 3 (descriptions may have changed), or if files were
added/removed from disk vs. what the index references. Skip only if all docs were `UP_TO_DATE` AND the file set
matches the index exactly.

To regenerate, use the (updated) content already in hand — no new reads needed. Write a new `index.md` following this
format (keep total length under 60 lines):

```markdown
## [filename.md](filename.md)

Brief description of content (1-2 sentences).

**Use when:**

- Specific scenario 1
- Specific scenario 2
- Specific scenario 3
```

Verify the line count is under 60 using the line numbers shown by the Read tool.

### Step 5: Validate Frontmatter and Table of Contents (Safety Net)

For each documentation file that was **not** rewritten in Step 3, check that:

1. The file starts with a valid YAML frontmatter block: `title`, `description`, `category`, `tags`, `last_updated`,
   `related_docs`.
2. The file contains a `## Table of Contents` section immediately after the `#` title (with a `---` separator before
   the first `##` body section).

For any file with missing or incomplete frontmatter/TOC: generate the corrected version from existing content and
write it. Preserve all body content unchanged.

If all untouched files are already valid, skip this step.

### Step 6: Update Last Refresh Timestamp

Write `.claude/documentation/last_refresh` — a plain-text file containing only the current UTC date and time in ISO
8601 format (e.g. `2026-03-25T10:42:00Z`). If the exact UTC time is not available from context, run
`date -u +%Y-%m-%dT%H:%M:%SZ` to obtain it first. Overwrite any existing value. This scopes the git log on the next run to
only changes made after this refresh.

## Output

After completing all steps, briefly report to the user:

- Which documentation files were **rewritten** due to stale content (file names + one-line summary of what changed).
- Whether the index was regenerated or was already up to date (and why).
- Which files had only frontmatter/TOC fixes, or that all were already valid.
- Which files were fully up to date and required no changes.

## Important Notes

- **Pass doc content to sub-agents directly** — do not have sub-agents re-read files the main agent already read.
- **Re-analyze source code for every doc file** — this is not optional. The whole point is to catch content drift.
- Do NOT modify any source code files.
- Keep the index under 60 lines.
- Maximize parallel tool calls at every step.

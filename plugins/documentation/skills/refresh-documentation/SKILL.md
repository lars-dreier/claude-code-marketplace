---
name: refresh-documentation
description: >
  Re-analyzes the codebase and rewrites any `.claude/documentation/` file whose content has
  drifted from the source code or has accumulated content that no longer earns its place, then
  refreshes the index and validates every file's frontmatter and table of contents. Use when the
  user says "refresh documentation", "update the docs", "the docs are stale", "sync documentation
  with the code", "bring the docs up to date", "trim the docs", or any variation asking to
  reconcile existing project documentation with the current codebase.
allowed-tools:
  - Glob
  - Grep
  - Read
  - Edit
  - Write
  - Bash
  - Agent
---

# Refresh Documentation

This skill keeps `.claude/documentation/` true to the source **and** worth its context budget.
Two kinds of drift matter equally:

- **Accuracy drift** — the code changed and the document did not.
- **Relevance drift** — the document is still accurate but has accumulated history, absence
  notes, duplication, or filler that costs context and earns nothing.

Removing content is as valid an outcome as adding it. Frontmatter and index hygiene are
secondary concerns handled at the end.

**Before anything else, read `${CLAUDE_PLUGIN_ROOT}/references/documentation-style.md`.** It is
the editorial contract for every file you write here, and it is what defines relevance drift.
Pass its rules to every sub-agent you launch.

## Your Task

Follow these steps in order. Carry data forward — do not repeat tool calls you have already made.

### Step 1: Collect Documentation Files and Recent Git Changes

In a **single message**, issue these tool calls in parallel:

- `Glob: .claude/documentation/*.md` — collect all `.md` files (save this list, reuse throughout)
- `Read: .claude/documentation/index.md` — read the current index
- `Read: .claude/documentation/last_refresh` — the previous refresh marker
- `Read: ${CLAUDE_PLUGIN_ROOT}/references/documentation-style.md` — the shared editorial rules

If the Glob returns **no files at all**: inform the user that no documentation exists yet and
suggest running the **create-documentation** skill first. Stop here.

If `index.md` does not exist (Read fails): treat the index as missing.

`last_refresh` holds a single ISO 8601 UTC timestamp. Scope the git log with it:

- Timestamp present: `git log --name-only --pretty=format: --since="<timestamp>" | sort -u | grep -v '^$'`
- Missing or unreadable: fall back to `--since="90 days ago"`

**Cross-repo documentation:** this log only covers the current repository. If a document
describes sibling repos, external tooling, or CI configuration, the log gives no signal about it
and an empty changed-file list is not evidence that the document is current. Note which
documents those are and tell their sub-agents to verify against those external paths directly.

### Step 2: Read All Documentation Files

**Read all doc files (excluding `index.md`) in a single parallel message.**

For each file, extract:
- The `last_updated` value from frontmatter (used to scope git history per file in Step 3)
- All section headings and body content (passed directly to sub-agents so they do not re-read)

### Step 3: Re-Analyze the Codebase and Update Stale Docs

This is the core step. Launch one **Explore sub-agent per documentation file**, all in parallel
in a single message.

**For each sub-agent, include in its prompt:**
- The full current content of the doc file (already read in Step 2 — do not make the sub-agent
  re-read it)
- The full text of `documentation-style.md`, or its rules inline. The sub-agent writes the file,
  so it needs the editorial contract.
- The `last_updated` date from its frontmatter — **for git scoping only**, not to be reused as
  the new timestamp
- The list of source files changed since the last refresh (filter by the doc's scope if helpful,
  or pass the full list for the sub-agent to cross-reference)
- Any external repos or paths this document depends on, when the current repo's git log cannot
  reveal its drift
- The current UTC date and time in ISO 8601 format (e.g. `2026-03-25T10:42:00Z`) — to be used as
  the new `last_updated` value if a rewrite is needed. Do NOT reuse the old `last_updated` value
  for this purpose. If the exact UTC time is not available from context, run
  `date -u +%Y-%m-%dT%H:%M:%SZ` to obtain it before passing it to sub-agents.

**Each sub-agent must:**

1. **Understand the doc's scope** from the content passed in — title, description, section
   headings.

2. **Focus on changed source files first** — cross-reference the changed-files list against the
   areas the doc covers. Then use Glob and Grep to read the current state of relevant source
   files.

3. **Check accuracy against current code:**
   - Are described APIs, functions, or classes still present and named correctly?
   - Do described behaviors, parameters, or return values still match?
   - Are there new significant additions (endpoints, config options, renamed modules) not
     mentioned?
   - Are there sections documenting things that no longer exist?

4. **Check relevance against `documentation-style.md`:**
   - Does the file contain history, migration notes, version churn, or commit hashes?
   - Does it cite line numbers?
   - Does it document absence — things not used, not applicable, not present — without that
     absence correcting a wrong inference?
   - Does it state anything obvious from context or from the technology?
   - Does it repeat content that belongs to another file in the set?
   - Is there filler that can be cut without losing a fact?
   - **Should this file exist at all?** A document whose subject is out of scope for the project
     is a deletion candidate — report it, do not delete it yourself.

5. **Return a verdict:**
   - `UP_TO_DATE` — accurate against the code *and* clean against the style rules.
   - `STALE: <one-line summary>` — content no longer matches the code.
   - `NEEDS_TRIMMING: <one-line summary>` — accurate, but carrying content that violates the
     style rules.
   - `OUT_OF_SCOPE: <one-line rationale>` — the document does not belong in this knowledge base.
     Return no rewrite; the orchestrator raises it with the user.

   `STALE` and `NEEDS_TRIMMING` are each followed by the **complete rewritten file content**:
   valid YAML frontmatter (`title`, `description`, `category`, `tags`, `last_updated` set to the
   current UTC timestamp passed in, `related_docs`), a `## Table of Contents` immediately after
   the `#` title, a `---` separator, then the body.

   Emitting the whole file is a mechanical requirement, not licence to expand it. **Change only
   what accuracy or the style rules require.** Report the resulting line count against the
   original; a rewrite that grows a file needs a reason you can name.

6. **Report findings separately from the file.** Line numbers, commit hashes and other
   provenance belong in the notes to the orchestrator, never in the document body.

> **Important:** Sub-agents must re-analyze actual source code — not just rephrase what was
> already in the doc. Catching drift between documentation and code is the primary job; cutting
> content that no longer earns its context is part of the same job, not a separate
> "reformatting" concern.

### Step 4: Reconcile Before Writing

Sub-agents run in parallel and cannot see each other's output. Before writing anything:

1. **Resolve contradictions.** Where two sub-agents assert incompatible facts, verify against the
   source yourself and use the verified answer. Never write a claim you could not confirm.
2. **De-duplicate.** Where two files now document the same thing, keep it in the one it most
   belongs to and replace the other with a cross-reference.
3. **Check the set reads as one.** Terminology and depth should be consistent across files.

Then write all rewritten files in a **single parallel message**.

Report any `OUT_OF_SCOPE` verdict to the user with the sub-agent's rationale, and leave the file
in place unless the user says otherwise.

### Step 5: Update the Index

Always regenerate `index.md` if **any** doc was rewritten in Step 3 (descriptions may have
changed), or if files were added/removed from disk vs. what the index references. Skip only if
every doc was `UP_TO_DATE` AND the file set matches the index exactly.

To regenerate, use the (updated) content already in hand — no new reads needed. Write a new
`index.md` following this format (keep total length under 60 lines):

```markdown
## [filename.md](filename.md)

Brief description of content (1-2 sentences).

**Use when:**

- Specific scenario 1
- Specific scenario 2
- Specific scenario 3
```

### Step 6: Validate Every File

Run these checks against **all** documentation files, including the ones just rewritten — a
freshly generated file is the most likely place for a malformed TOC.

1. **Frontmatter**: starts with a valid YAML block carrying `title`, `description`, `category`,
   `tags`, `last_updated`, `related_docs`.
2. **Table of contents**: a `## Table of Contents` section immediately after the `#` title, a
   `---` separator before the first body section, and one TOC entry per `##` heading.
3. **No line-number citations**: grep the set for `file.ext:NN` and "lines N-M" patterns and
   remove any hit.
4. **Index length**: under 60 lines.

Mechanical checks are cheaper than a re-read — for example:

```bash
grep -nE '\.(js|ts|py|cs|go|rb|java|php|rs)[a-z]*:[0-9]+|[Ll]ines? [0-9]+-[0-9]+' *.md
```

Fix anything that fails. When repairing frontmatter or a TOC, preserve the body unchanged.

### Step 7: Update the Refresh Marker

Write `.claude/documentation/last_refresh` containing only the current UTC date and time in
ISO 8601 format, nothing else:

```
2026-03-25T10:42:00Z
```

Obtain the timestamp with `date -u +%Y-%m-%dT%H:%M:%SZ` if it is not already in context.
Overwrite any existing value.

## Output

After completing all steps, briefly report to the user:

- Which files were **rewritten for accuracy**, with a one-line summary of what changed in the
  code.
- Which files were **trimmed**, with what class of content came out and the line delta.
- Any file flagged **out of scope**, with the rationale, and that it was left in place.
- Any **contradiction between sub-agents** you resolved, and how you verified it.
- Whether the index was regenerated, and why.
- Which files were already up to date.

## Important Notes

- **Follow `documentation-style.md`.** It governs everything written here and is the definition
  of relevance drift.
- **Pass doc content to sub-agents directly** — do not have sub-agents re-read files the main
  agent already read.
- **Re-analyze source code for every doc file** — this is not optional.
- **Verify any claim two sub-agents disagree on** before writing it.
- A shorter document that says the same thing is a better document.
- Do NOT modify any source code files.
- Maximize parallel tool calls at every step.

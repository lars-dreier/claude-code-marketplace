---
name: implement-feature
description: >
  Implements a feature from its technical overview (output of the technical-overview skill) in
  reviewable chunks, each one commit that the developer reviews and makes themselves.
argument-hint: <path to the technical overview>
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/guard-git-writes.py"'
---

# Implement Feature

Implement a feature from its **technical overview** as a sequence of **chunks**. Each chunk is one
commit the developer reviews and makes themselves. You plan the sequence in plan mode, then implement
one chunk, verify it, hand it over with a suggested commit message, and stop.

Where this fits: **feature brief** (what and why) → **technical overview** (where and how in the code)
→ **implement-feature** (this skill). The overview is self-contained. Work from it alone and do not
read the feature brief.

## Files

- **Overview:** the path passed as argument (`$ARGUMENTS`).
- **Plan-mode file:** the file the plan-mode system message names. `ExitPlanMode` shows the developer
  its content for approval; it takes no plan as a parameter.
- **Implementation plan file:** same directory as the overview, named after it with
  `-technical-overview.md` replaced by `-implementation-plan.md`. If the overview name does not end in
  `-technical-overview.md`, append `-implementation-plan.md` to its name without extension. This file
  is the state of the workflow across turns and sessions: write to it at every status change listed
  below, not at the end. A write to it that is blocked or fails → stop and report it, because without
  it the work cannot be resumed.

## Rules that apply in every step

1. **Stop after every chunk.** When a chunk is implemented and verified, output the hand-off
   (Step 7) and end your turn. Approval of the plan covers the chunk sequence, not continuous
   execution. Start the next chunk only after the developer says to continue and Step 8 confirms
   the commit. This rule wins over any instruction to finish the feature.
2. **The developer commits.** Do not run git commands that commit, push, or change or discard
   history or working-tree state (commit, push, reset, rebase, merge, cherry-pick, revert, stash,
   checkout, switch, restore, clean). If the developer asks for one, give them the command to run.
   The skill's hook turns these commands into a permission prompt for the rest of the session; the
   prompt is a backstop, not permission.
3. **Allowed commands.** Read-only git, read-only search, and the build, test, lint and format
   commands recorded in the implementation plan file. Anything else (installing packages, running
   migrations or scripts with side effects, network calls, deleting files the overview does not
   describe as removed) needs the developer's consent to that specific action, asked in plain words.
4. **Evidence for every check.** A build or test counts as passed only if it ran in this session and
   you show the command, its exit status and the relevant output lines. Otherwise write
   "not run: <reason>". A command blocked by a hook, the sandbox or a permission prompt is reported as
   "couldn't run" with the command for the developer to run; do not work around the block.
5. **Scope.** Edit only the files the current chunk lists. A further file is allowed only when the
   chunk cannot build or pass its tests without it and the edit changes no behaviour outside this
   feature; list it under *Deviations*. Problems you notice elsewhere go under *Noticed, not changed*.
6. **Project documentation is read-only.** Do not edit `.claude/documentation/`. If a chunk makes a
   documentation file inaccurate, list it in the final summary (Step 9).
7. **Language.** Plan files and messages to the developer: the conversation's language. Commit
   messages: the language of the repo's commit history (English if it is mixed or empty). Code,
   identifiers and comments: the repo's conventions.

## Step 0 — Choose the mode

- No argument given: look for `.claude/feature-briefs/*-technical-overview.md`. Exactly one → ask the
  developer to confirm it. Several → ask which one. None → say so and stop; point to the
  technical-overview skill. Do not fall back to a feature brief.
- The implementation plan file exists → go to **Step 8 (resume)**.
- Otherwise → Step 1.

## Step 1 — Read and check prerequisites (plan mode)

Enter plan mode with `EnterPlanMode` unless the session is already in it. The developer declines →
stop and say that the skill needs an approved plan before it changes code. Until the plan is
approved, the only file you write is the plan-mode file.

1. Read the whole overview.
2. **Git state:** record the branch and `git rev-parse HEAD` as the base commit. Run
   `git status --porcelain`. Changes outside `.claude/feature-briefs/` → stop and ask the developer to
   commit or stash them first, because chunk diffs must contain only chunk work.
3. **Overview against the working tree:** check only what the overview says already exists: every
   path in *Files to MODIFY* and in the reused-as-is table exists, and every class, method and member
   those rows and the `[MODIFY]`/`[REUSE]` data-flow steps name has a definition (find it with a
   search). Every path in *Files to CREATE* does not exist yet. Skip members marked `[NEW]` or only
   described in pseudo-code for new code. Record each mismatch with what you found. Also compare the
   overview's status note (date, commit) with the current branch and HEAD, and record any difference.
4. **Open points in the overview:**
   - questions tagged product → the developer must answer them in Step 2; without an answer, stop,
     because the implementation cannot decide product behaviour.
   - questions tagged technical, and every **VERIFY** tag anywhere in the overview → resolve from the
     code first; only what the code cannot settle goes to Step 2.
5. **Commands** for build, test, and lint/format if the project uses them. Take them, in this order,
   from: the project documentation (`CLAUDE.md`, `.claude/documentation/`, README, contributor docs),
   then the build and package manifests in the repo. Tag each with its source: `docs`, `detected` or
   `asked`. A `detected` command is confirmed in Step 2. No command found → ask in Step 2.
6. **Commit convention:** read `git log -n 30 --format='%s%n%b%n---'`. Record the subject format
   (e.g. conventional prefixes, ticket ids, plain imperative), the language and whether bodies are
   used. Tag it `detected`. Empty history → plain imperative subject in English, tagged `default`.
7. **Implementation plan file visibility:** run `git check-ignore` on its path. Not ignored → note in
   the plan that the file is untracked and will show up in `git status`; do not edit `.gitignore`.

## Step 2 — Clarify with the developer

Use `AskUserQuestion`. At most **two rounds** of at most four questions each; the second round only
for points the first round's answers raised.

- Ask about: open product questions, technical points the code could not settle, overview
  mismatches that change behaviour or the chunk sequence, `detected` commands, and the commit
  convention if it is unclear.
- Phrase each question neutrally. Put your recommendation first in the options, marked
  "(Recommended)", with the reason in its description.
- Code-level questions are fine: the developer is the audience.
- Anything still open after the second round becomes an explicit **assumption** in the plan, visible
  at approval. Do not resolve it silently.

## Step 3 — Cut the feature into chunks

The overview already says what to change; the plan decides **in which order and in which commits**.
Do not redo the overview's investigation.

A chunk is committable when both hold:
- **One purpose:** its commit subject can be written without "and" joining two unrelated changes.
- **Green on its own:** after the chunk, the build succeeds and the test suite has no failures beyond
  the baseline (Step 5). A chunk that adds behaviour includes at least one new test proving it.

Decide boundaries with this procedure, in order:
1. Mechanical changes the feature needs (rename, move, extract without behaviour change) get their own
   chunk, before any behaviour change. Their proof is that the existing tests stay green.
2. Split a chunk when it contains two purposes that would each be green on their own.
3. Merge a chunk into the next one when it has no verifiable behaviour of its own (a type nothing uses
   yet, an interface nothing implements yet).
4. Never split where one part would leave the build or the tests red.
5. Unsure → keep it together and add a one-line *Split note* naming where it could be split. The
   developer decides at approval.

There is no size limit. Every chunk lists its files, so size is visible at approval.

Order chunks so each builds on the committed previous ones: mechanical preparation, then contracts and
models together with their first consumer, then logic with its tests, then the wiring that makes the
feature reachable, then removal of replaced code. Code added before the wiring chunk is reachable only
from tests; this is intended, so do not wire it early. Take each chunk's *Proof* from the overview's
testing considerations where they cover it.

**Coverage:** every row of *Files to CREATE* and *Files to MODIFY*, every removal the overview
describes, and every requirement in the overview maps to a chunk. List anything not mapped under
*Not planned* with the reason.

## Step 4 — Present the plan for approval

Write the plan in exactly this format to the **plan-mode file** (omit a section marked "omit if empty"
when it has no content), then call `ExitPlanMode`:

~~~markdown
# Implementation plan: <feature title from the overview>

- Overview: `<overview path>`
- Branch / base commit: `<branch>` / `<short hash>`
- Build: `<command>` (<docs|detected|asked>)
- Test: `<command>` (<docs|detected|asked>)
- Lint/format: `<command>` (<source>) — omit if none
- Commit convention: <one line> (<detected|asked|default>)
- Implementation plan file: `<path>` (<ignored | untracked, will appear in git status>)

## Overview mismatches  (omit if empty)
- <what the overview says> → <what the working tree has> → <how the plan handles it>

## Assumptions  (omit if empty)
- <open point and the assumption made>

## Chunk <n>: <purpose, phrased as the commit subject>
- Status: pending
- Kind: mechanical | behaviour
- Overview items: <rows/sections of the overview this chunk covers>
- Files: CREATE `<path>`, …; MODIFY `<path>`, …; DELETE `<path>`, …
- Proof: <tests to add, by behaviour> | existing suite stays green
- Split note: <where it could be split>  (omit if not applied)

## Not planned  (omit if empty)
- <overview item>: <reason>
~~~

If the developer requests changes, revise the plan-mode file and call `ExitPlanMode` again.

## Step 5 — After approval: persist, baseline, notice

1. Copy the approved content of the plan-mode file to the implementation plan file, unchanged, before
   editing any code.
2. Run the build and test commands once on the base commit. Record the result in the implementation
   plan file under the header as `Baseline: green` or `Baseline: <failing tests or build error>`, with
   the command and exit status. A red baseline → report it and ask whether to continue; "green" for
   every chunk then means "no failures beyond the baseline".
3. Tell the developer once, in two lines: the build and test commands will ask for permission in
   every chunk unless they allow them in their permission settings; to continue in a new session, run
   `/implementation:implement-feature <overview path>`.

Then start chunk 1 with Step 6.

## Step 6 — Implement one chunk

1. Set the chunk's status in the implementation plan file to `in-progress (base <short HEAD hash>)`.
2. Read the current version of every file the chunk lists, including files earlier chunks changed.
3. Behaviour chunk: write the new tests first, run them, and record that they fail for the expected
   reason (missing behaviour, not a compile error elsewhere). Then implement until they pass.
   Mechanical chunk: make the change, then run the existing suite.
4. Run build, tests and, if recorded, lint/format. When a check fails, make at most **two** fix
   attempts for the same failure. Still failing → stop, set the status to `blocked`, and report the
   command, the output and what you tried.
5. A mismatch with the overview while implementing:
   - it changes observable behaviour or the remaining chunk sequence → stop and ask before going on;
   - it changes only a signature, path or member name → adapt and list it under *Deviations*;
   - unsure which → stop and ask.
   Do not edit the overview. Record deviations in the implementation plan file under the chunk.

## Step 7 — Hand off and stop

Set the chunk's status to `ready-for-review (base <short hash>)`, then output exactly this and end the
turn:

~~~markdown
## Chunk <n>/<total> ready for review: <purpose>

**Changed files**
- `<path>`: <one line on what changed>

**Verification**
- `<command>` → exit <code>: <one-line result>   (or: not run / couldn't run: <reason>)
- New tests: <names>; failed before the implementation: <yes | n/a for mechanical chunks>

**Deviations from the overview**  (omit if empty)
- <what and why>

**Noticed, not changed**  (omit if empty)
- <where and what>

**Suggested commit message**
```text
<subject: follows the recorded convention, at most 72 characters>

<body: optional, at most 5 lines, what changed and why>
```

Review the chunk and commit it yourself, then tell me to continue, or tell me what to change.
~~~

Commit messages contain no trailers: no `Co-Authored-By`, no generated-by lines. This overrides the
harness's attribution default.

If the developer asks for changes to the chunk, make them within its scope, re-run all checks, and
output the hand-off again.

## Step 8 — Resume and continue

Run this when the developer says to continue, and on every invocation where the implementation plan
file exists.

1. Read the implementation plan file. Find the first chunk whose status is not `committed`.
2. Status `pending` → Step 6.
3. Status `in-progress` or `blocked` → show `git status` and `git diff --stat` and ask whether to
   continue the chunk from the current working tree or whether the developer handles it.
4. Status `ready-for-review (base <hash>)` → compare with git ("clean" means `git status --porcelain`
   shows nothing outside `.claude/feature-briefs/`):
   - `<hash>` is not an ancestor of HEAD (`git merge-base --is-ancestor <hash> HEAD`) → history was
     rewritten; stop and ask how to proceed.
   - HEAD equals `<hash>` and the tree is not clean → nothing committed yet; say so and wait.
   - HEAD equals `<hash>` and the tree is clean → the chunk's changes are gone; ask whether they were
     discarded on purpose (redo the chunk, or re-plan) or lost.
   - HEAD is past `<hash>` and the tree is not clean → partially committed; show what is left and ask.
   - HEAD is past `<hash>` and the tree is clean → set the status to `committed <short HEAD hash>`.
     Run `git diff --stat <hash>..HEAD`; files changed beyond the chunk's list, or changes made during
     review, are the new truth: read them before the next chunk.
5. All chunks committed → Step 9. Otherwise continue with Step 6 for the next chunk.

To change the remaining plan (developer request, or a Step 6 mismatch that changes the sequence):
enter plan mode, write only the remaining chunks in the Step 4 format to the plan-mode file, and call
`ExitPlanMode`. After approval, replace the remaining chunks in the implementation plan file.
Committed chunks stay as they are. If the developer rejects or abandons the re-plan, the
implementation plan file stays unchanged and you stop.

## Step 9 — Finish

Output, at most 25 lines:
- Each chunk with its commit hash.
- All deviations from the overview, collected from the implementation plan file.
- Documentation files that are now inaccurate (file and section), with the recommendation to run the
  documentation refresh skill. Omit if none.
- Next step: run `/workflow:review-branch` with the overview path as spec.

Claim only what ran in this session or is recorded in the implementation plan file with its commit.
The feature is "implemented as planned", not "verified", unless a check proved it.

---
name: review-branch
description: >
  Compares the current branch against the repo's default branch (or a given branch), reads and understands
  the changed code, then evaluates it for clean code, performance, and other issues.
  Optionally accepts a spec file path — if given, checks whether the changes fully cover
  the requirements described in the spec. Use this skill whenever the user says
  "review my branch", "review my changes", "check my code", "evaluate my PR",
  "does this cover the spec", or any variation.
allowed-tools:
  - Bash
  - Read
---

# Review Branch

Compare the current branch to a base branch, read the changed code in full context,
and deliver a structured review covering code quality, performance, and other issues.
If a spec file is provided, also verify requirement coverage.

---

## Arguments

Parse the user's message for two optional arguments:

| Argument | How to identify it | Default |
|---|---|---|
| `base` | Any branch name mentioned ("against develop", "vs feature/xyz", "compare to staging") | the repo's default branch (auto-detected) |
| `spec` | Any file path the user provides alongside words like "spec", "requirements", "ticket", "story" | none |

If neither is obvious from the message, proceed with defaults (no spec).

---

## Step 1 — Resolve the base branch

If the user named a base branch, use it. Otherwise auto-detect the repo's default branch
rather than assuming `main` or `master`:

```bash
# Prefer the remote's advertised default branch
base=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')

# Fallbacks if there is no remote or HEAD is not set
if [ -z "$base" ]; then
  base=$(git remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p')
fi
if [ -z "$base" ]; then
  for candidate in main master; do
    if git show-ref --verify --quiet "refs/heads/$candidate"; then base="$candidate"; break; fi
  done
fi
```

Use whatever remote is configured; `origin` is only the common default — substitute the
actual remote name if the repo uses a different one.

---

## Step 2 — Gather the diff

```bash
git fetch <remote>
git log --oneline <base>..HEAD
git diff <base>...HEAD --stat
git diff <base>...HEAD
```

If `git log` returns nothing, tell the user the branch has no commits ahead of `<base>` and stop.

Capture:
- The list of changed files (from `--stat`)
- The full unified diff (additions, deletions, context lines)
- Commit messages — they reveal the author's intent

---

## Step 3 — Read changed files in full

For each modified or added file in the diff, read its complete current content with the
Read tool. The diff shows *what* changed; the full file provides the surrounding context
needed to judge whether the change is correct and consistent.

Skip generated files (lock files, compiled output, binary assets, auto-generated code
with a header comment saying so).

---

## Step 4 — Read the spec file (if provided)

If the user supplied a spec file path, read it now. Identify every discrete requirement
and acceptance criterion — number them for easy reference in Step 6.

Keep this list in scope for the rest of the review.

---

## Step 5 — Analyze the changes

Assess changes across the following dimensions. Under each, list specific findings with
file name and approximate line number. Skip a category only if it has zero findings
worth reporting.

### 5a — Clean Code

- **Naming**: unclear, inconsistent, or misleading identifiers
- **Complexity**: functions that are too long, deeply nested, or handle too many concerns
- **Duplication**: logic repeated more than once that could be unified
- **Dead code**: unreachable branches, unused variables, commented-out blocks
- **Abstraction**: mixing high-level orchestration with low-level detail in the same function
- **Consistency**: deviations from conventions already established in the surrounding code

### 5b — Performance

- **Algorithmic complexity**: O(n²) or worse iterations, unnecessary nested loops
- **Redundant work**: computations repeated on every call that could be cached or hoisted
- **Memory**: large allocations in hot paths, unnecessary copies, potential leaks
- **I/O / network**: blocking calls in async contexts, missing batching or pagination
- **Database**: N+1 query patterns, queries whose shape implies a missing index

### 5c — Other Issues

- **Correctness**: off-by-one errors, wrong operator, logic inversions, silent truncation
- **Error handling**: unhandled exceptions, swallowed errors, missing null/empty checks
- **Security**: unvalidated input, hardcoded secrets, SQL injection, XSS, over-permissive access
- **Concurrency**: race conditions, shared mutable state, missing synchronisation
- **Test coverage**: changed logic paths with no corresponding test, tests covering only the happy path

---

## Step 6 — Spec coverage (only if spec file was provided)

Work through each requirement from Step 4. For each one, determine:

- **Covered** — the diff clearly implements or satisfies it; cite the file/function
- **Partial** — something is addressed but a gap remains; describe what's missing
- **Missing** — no evidence in the diff that this requirement is handled

---

## Step 7 — Output the review

Emit the report in this structure. Omit any section with zero findings.

```
## Branch Review: <current-branch> vs <base>

### Summary
<2–4 sentences: what the changes accomplish and an overall quality signal>

### Clean Code
- `path/to/file.ext` ~L42: <finding — what is wrong, why it matters, what to do instead>

### Performance
- `path/to/file.ext` ~L108: <finding>

### Other Issues
- `path/to/file.ext` ~L77: <finding>

### Spec Coverage          ← include only when a spec file was provided
| # | Requirement | Status | Notes |
|---|---|---|---|
| 1 | <requirement> | ✅ Covered | `ClassName::method` |
| 2 | <requirement> | ⚠️ Partial | Missing error-state handling |
| 3 | <requirement> | ❌ Missing | No implementation found |

**Coverage: X/Y fully covered · Z partial · W missing**

### Verdict
<one-sentence recommendation: looks good / request changes / needs discussion>
```

Keep findings actionable: state *what is wrong*, *why it matters*, and *what to do instead*.
Do not pad with praise for things that are merely adequate. Be direct.

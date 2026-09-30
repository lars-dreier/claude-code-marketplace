---
name: verify-document
description: >
  Audits a technical document (analysis, assessment, architecture write-up, bug report, design doc,
  feature brief, technical overview, ADR) against the codebase it describes. Treats the document as
  unverified, extracts every claim, and checks each by tracing it through the actual code, labelling
  how it was verified. Then reads the code the document covers on its own to find what the document
  missed. Read-only: reports and stops. Takes a path to the document. Use when the user says "verify
  this document", "check this analysis against the code", "is this assessment correct", "fact-check
  this doc", "review this write-up", or passes a document path and asks whether it holds up.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Verify Document

Audit a technical document against the code it describes. Report which claims hold up, which are
wrong or overstated, and what the document misses. **Do not edit the document or the code.** Report
and stop; the user decides what to change.

The main failure mode is **confirming the document on its own terms**: checking that line 249 says
what the document quotes, then calling a scenario built on it "verified". A claim is only verified
at the level it was checked. A matching declaration does not prove the runtime behavior.

---

## Arguments

| Argument | How to identify it | Default |
|---|---|---|
| `doc` | The file path in the user's message | required; ask if missing |
| `ref` | A commit, branch or tag the user names ("against master", "at abc123") | the commit pinned in the document if any, otherwise the working tree |
| `focus` | Sections or topics the user wants checked ("only section 4", "just the performance claims") | the whole document |

---

## Step 1 — Read the document and establish the baseline

1. Read the whole document. Note its subject, its scope, and any commit or date it is pinned to.
2. If a commit is pinned and differs from `HEAD`, check for drift in the files it references:
   ```bash
   git log --oneline <pinned>..HEAD -- <referenced paths>
   ```
   If those files changed, verify against `HEAD` and record every claim the drift affects.
3. If the repo has project documentation or an index (e.g. `.claude/documentation/index.md`,
   `CLAUDE.md`), load what is relevant to the document's subject.

---

## Step 2 — Build the claim ledger

Split the document into **atomic, checkable claims** and number them (`C1`, `C2`, …). One sentence
can hold several claims, and a scenario is a chain of claims. Classify each:

| Type | Example | Verified by |
|---|---|---|
| **Reference** | "`Foo.cs:42` does X", "class Y exists" | Reading the cited location |
| **Structural** | "A calls B", "all X implement Y", "pattern P is used in …" | Reading and searching (callers, implementers, usages) |
| **Behavioral / scenario** | "when A happens, B follows, so C breaks" | **Tracing the runtime path end to end** |
| **Completeness** | "all", "only", "exactly N", "never", "no callers" | Exhaustive search, not sampling |
| **Mitigation / impact** | "harmless because …", "hidden by …", "low risk" | Following the cited mechanism into its implementation |
| **Causal** | "root cause is X", "this exists because Y" | Checking that the cause produces the effect and nothing else explains it better |
| **Quantitative** | "O(n²)", "allocates per call", "thousands per switch" | Reading the loop and allocation structure; label estimates as estimates |
| **Recommendation** | "we should do X" | Checking its premises; judge soundness only if the premises hold |
| **Self-declared unverified** | "not verified", "probably", "TODO" | Trying to resolve it |

Also record the document's **internal cross-references** (counts, "see 4.5", summary bullets). They
are checked in Step 5.

---

## Step 3 — Verify every claim

Check each claim with the method its type requires, and record the evidence as `path:line`.

Rules that make the difference between checking and confirming:

- **Trace scenarios from trigger to effect.** Start at the entry point (signal, user action, call
  site) and follow every call to the claimed result. At each step look for the branch that stops the
  scenario: early returns, guards, null checks, redraws or rebuilds, caching, state resets. Most
  wrong scenarios die at one such branch.
- **Read whole functions, not line windows.** Condition and early-return logic often sits a few
  lines above the quoted line.
- **Follow mitigations one level deeper.** If the document says a mechanism hides or limits a
  problem, open the guard, provider or filter that mechanism relies on and check which inputs it
  actually covers.
- **Search exhaustively for completeness claims.** Find every implementer, caller or usage (e.g.
  `grep -rn`) instead of stopping at the examples the document gives.
- **Try to disprove, not to confirm.** For each behavioral claim, ask what would have to be true for
  it to be false, and look for that.
- **Keep each claim's verification level honest.** A claim checked only at its declaration is
  "declaration only", even if the rest of the document relies on it.

Assign one verdict per claim:

| Verdict | Meaning |
|---|---|
| ✅ **Confirmed (traced)** | The runtime path was followed end to end and supports the claim |
| ☑️ **Confirmed (declaration only)** | The cited code says what the document states; runtime behavior not traced |
| ⚠️ **Partially correct** | True, but overstated, understated or narrower than written; state the correct scope |
| ❌ **Contradicted** | The code shows otherwise; cite where |
| ❔ **Unverifiable** | Depends on runtime data, configuration or external systems; state how to check it |

---

## Step 4 — Independent coverage pass

The document's structure decides what gets checked in Step 3. This pass removes that bias.

1. List the core files of the subject: the files the document cites, plus the files they depend on
   for the behavior under discussion.
2. Read every one of them that Step 3 didn't read in full, **including files the document lists but
   never discusses**.
3. Using the document's own goal (correctness, performance, design quality, feasibility), note
   issues, risks or facts that are relevant to that goal and missing from the document. Stay within
   the document's subject; don't review the whole codebase.
4. Check dead or unused parts the document relies on or builds on (e.g. interface methods with no
   callers).

---

## Step 5 — Consistency pass

- Counts and lists match the body ("three paths" when the tree shows three).
- Summary bullets and root-cause tables agree with the detailed sections.
- Cross-references point to sections that say what is claimed.
- Claims marked unverified in one place aren't treated as fact elsewhere.

---

## Step 6 — Report

Report in the conversation using this structure. Omit empty sections. Write the report to a file
only if the user asks.

```
## Verification: <document title or path>

Baseline: <ref verified against> · Drift: <none / files changed since pinned commit>
Claims checked: N · ✅ a · ☑️ b · ⚠️ c · ❌ d · ❔ e

### Contradicted
- **C12** (<doc section>): <claim, short>. <What the code shows instead>, `path:line`.
  Impact on the document: <which conclusions depend on it>.

### Partially correct
- **C7** (<section>): <claim>. <Correct scope>, `path:line`.

### Missing from the document
- <Finding>, `path:line`. <Why it matters for the document's goal>.

### Internal inconsistencies
- <Section X says A, section Y says B>.

### Unverifiable
- **C20**: <claim>. <How to check: runtime test, data query, log>.

### Claim ledger
| # | Section | Claim | Type | Verdict | Evidence |
|---|---|---|---|---|---|

### Not covered by this verification
<Files, sections or claims not checked, and why>

### Verdict
<One or two sentences: can the document be relied on as is, which sections need revision first>
```

Order findings by how much of the document depends on them. A contradicted premise under three
conclusions comes before an off-by-two line number.

---

## Principles

- **Read-only.** Never edit the document or the code. If the user wants the document corrected,
  that is a separate step after they have reviewed the findings.
- **Evidence or it didn't happen.** Every verdict other than ❔ cites `path:line`.
- **Don't inherit confidence.** Claims the document calls "confirmed" or "verified" get the same
  scrutiny as the rest.
- **Say what you didn't check.** A verification that hides its gaps is worse than a partial one that
  lists them.
- **Plain, direct prose.** State the defect and the evidence; no hedging where the code is clear, no
  confidence where it isn't.

---
name: technical-overview
description: >
  Turns a feature brief into a code-grounded technical overview — the layer between the brief
  (what must be built) and a plan-mode implementation. Maps every requirement to the concrete
  file(s)/line(s) that satisfy or must change it, expressed as "mirror this existing pattern",
  with every claim verified against the working tree. Use when the user says "create a technical
  overview", "map the brief to the code", "find the places in the code we need to adjust",
  "turn this brief into technical requirements", or feeds you a feature brief and wants the
  technical surface pinned down before implementing.
---

# Technical Overview

Turn a **feature brief** into a **single-file, code-grounded technical overview**: a map from each
requirement to the concrete code that satisfies it or must change. The output is fed into a **fresh
Claude Code session in plan mode** to implement the feature — so it must be precise, verified, and
self-contained enough that the implementer redoes none of the investigation.

This skill is the **lower-altitude companion** to [`feature-brief`](../feature-brief/SKILL.md):

| | Feature brief | Technical overview (this skill) |
|---|---|---|
| Altitude | *What* must be built & why | *Where* in the code, and *how* (mirror which existing pattern) |
| Contains | requirements, answered technical questions | file paths, line refs, pseudo-code, wiring, exact signatures |
| Forbids | code, line-numbers, "edit file X" | nothing — this is the place for all of it |
| Audience | any developer/PO | the implementer (plan mode) |

The litmus test for every line here is the inverse of the brief's: *"Could the implementer act on
this without opening the code to figure out where/how?"* If not, it is not specific enough yet.

---

## When to use
- A feature brief exists (or the user provides one) and the technical surface must be pinned down
  before implementation.
- The user wants the "second document" that finds the exact code to adjust.

## When NOT to use
- No brief / unclear acceptance criteria yet → run `feature-brief` first.
- The user wants the actual code written → that is the plan-mode implementation step that *consumes*
  this document.

---

## Output

**One Markdown file.** Save next to the brief as
`.claude/feature-briefs/<brief-name>-technical-overview.md`. Name it after the brief it companions.
Keep everything in this one file. Use the template in **Overview template** below.

---

## Core principle: VERIFY, don't trust

The brief, any earlier draft of this overview, prior-art docs, your own memory, and the
codebase index are all **leads, not facts**. Every load-bearing claim — file path, line number,
method/function signature, overload, "this already exists", "this dependency is already available",
"the call has no parameters", "something else already handles this" — **must be confirmed by reading
the current working tree** before it goes in the document. Plausible-sounding claims about paths,
signatures, and existing wiring are exactly the ones that turn out wrong and break a downstream
implementation.

When you cannot verify a claim, mark it **VERIFY** in the doc rather than asserting it. Re-verify on
each pass — prior-art code merges, branches move.

---

## Process

### Step 1 — Read the brief and establish repo/git state
Read the feature brief end-to-end. Then establish the ground truth the brief cannot capture:
- **Git/branch state:** what branch are we on, what is already committed vs. empty
  (`git log origin/<default-branch>..HEAD`), what dependency work/PRs are already **merged to the
  default branch**.
- **Dependency state:** if this work builds on foundational work (e.g. shared infrastructure), is
  that code merged, in review, or unwritten? **Merged → it is the template; reuse it. Unmerged →
  flag the sequencing risk.** Record this; it dictates whether you reuse or rebuild.

Record this as a dated re-assessment note at the top of the doc, because it goes stale.

### Step 2 — Trace the contracts the feature depends on against this codebase
Identify the contracts the feature must conform to — API endpoints, message/event schemas, data
models, library or module interfaces — and read their authoritative definition (another service, a
shared repo, a schema, or this codebase). Confirm the corresponding types/interfaces this code will
use exist and match. Capture the **exact** shape: is the call parameterless? what does the result
contain — and what does it **not** (data that arrives through a separate channel)? what is done
elsewhere, outside this code (compute, clamp, skip, persist)? Work done outside this code often
eliminates work here — e.g. a parameterless call whose other side iterates the whole set means this
code sends no list.

### Step 3 — Map the current code: reuse vs. new
Split the surface in two, both verified by reading the code:
- **Reuse (do not rebuild):** the existing modules/components/handlers/models/functions the feature
  should mirror. For each, record *where it is* and *what it does*, and — critically — **find the
  closest existing analog** for each new piece. The strongest overview expresses nearly every change
  as **"mirror `ExistingThing` at `path:line`"**. Reuse beats invention.
- **Genuinely new:** the short list of things no existing code covers. Be honest about which is which.

### Step 4 — Trace each flow end-to-end, including blast radius
For every runtime path the feature touches, follow the data to its conclusion — do not stop at the
first plausible hop:
- **Who sends / who handles / what updates state / is there an unsolicited update?** A flow that
  *seems* to refresh itself may not; whether the code must explicitly refetch vs. relies on an
  incoming update is a fact to confirm by tracing, not to assume.
- **Before reusing any signal/event/command, trace its full blast radius** — every subscriber. A
  mechanism that looks reusable by its name can be a trap: a subscriber may fire unwanted side
  effects, log noise, or re-enter a deprecated code path. List the subscribers and their per-item
  effect; decide reuse from that, not from the name.

### Step 5 — Resolve every open technical question on the escalation ladder
List the questions whose answer **changes the implementation**, then resolve each in this order:
1. **Working-tree code** (the contract, the existing pattern).
2. **The contract** (authoritative external truth).
3. **Any existing analogous implementation** as the authoritative *behavioral* reference (Step 6).
4. **The user** — only when 1–3 cannot settle it.

Mark each **RESOLVED** (with the evidence) or **OPEN**, and tag open ones **product** (needs PO) vs
**technical** (verify at implementation). Work through them **one at a time, conversationally** —
surface the question, resolve it, confirm, move on. Be willing to **reverse your own earlier
conclusion** when the evidence contradicts it; a decision reached from the brief or intuition is
provisional until verified code or the prior-art implementation confirms it.

### Step 6 — Use any existing analogous implementation as the authoritative behavioral tie-breaker
When a behavioral question is genuinely open, read the **real, merged implementation of the same
feature elsewhere** — another platform, module, or prior feature. Pull the PR (your code host's MCP
tools) to find the changed files, then **read the actual code in its repo**, not the PR description.
Extract behavior/flow/calc/edge-cases; **never** copy structure (the target may have a different
architecture). Reference it by **ticket/PR + stable file paths**, never an ephemeral branch. If it
contradicts the brief, the verified implementation wins and you record a deviation (Step 7).

### Step 7 — Write the overview, recording deviations from the brief
Write at implementation altitude: real file paths, line refs, pseudo-code, wiring, exact
signatures. Where deeper investigation **contradicts the brief**, the overview supersedes it — record
these in an explicit **Deviations from the feature brief** section, each with the reason and the
evidence. The brief is not edited; the overview is the now-authoritative technical document.

### Step 8 — Keep the document internally consistent (propagate, don't append)
This is a living document during investigation. When one decision changes, **propagate it through
every section that depends on it** — the deviations list, the data-flow diagram, the CREATE/MODIFY
tables, the detailed specs, the decisions, the open-questions list, and the prior-art section —
rather than appending a contradicting note. A reader must be able to trust any single section in
isolation. One changed conclusion routinely touches several sections; chase all of them.

### Step 9 — Pin exact signatures and wiring
Before finalizing, confirm by reading the real code: method/function signatures and overloads,
argument/type-parameter order, which dependencies/imports are *already* available, exact
constant/enum/identifier names, capacities/limits, feature-flag names. These are the details that
break a plan-mode implementation if guessed. Anything unverified stays tagged **VERIFY**.

---

## Overview template

```markdown
# <TICKET-ID or feature name> — Technical Overview: <short title>

Companion to `<brief-name>.md` (the feature brief). Code-grounded requirements map: every
requirement → the concrete file/line that satisfies or must change it.

> **Re-assessed <date>.** <git/branch/dependency state: what's merged, what's written, what this
> branch points at>. Every path/line below verified against the current working tree.

> Scope reminder: <one line — what this work is / isn't>.

> ⚠️ **Deviations from the feature brief** (these supersede it):
> 1. <what the brief said> → <reality, with the file/evidence that proves it>.

## 0. Dependencies — <status>
What prior/foundation work this builds on; whether merged (→ reuse as template) or not
(→ sequencing risk). Table of **reusable assets** (where + what it does + how this feature reuses
it) and a short list of **what is genuinely new**.

## 1. Data flow (target implementation)
Annotated step-by-step of the runtime path, each step tagged [MODIFY]/[NEW]/[REUSE] with file refs.

## 2. Files to CREATE
| # | File | Content (mirror which existing thing) |

## 3. Files to MODIFY
| # | File | Change (mirror which existing thing, at which line) |

## 4. Detailed change specs
Per non-trivial change: pseudo-code + the existing pattern it mirrors + why.

## 5. Key technical decisions & risks
Each decision: the choice, the reason, and the verified evidence (code ref / prior-art ref).
Include error/failure handling and any residual risks (with why they're acceptable).

## 6. Reused as-is (no change)
| Concern | Reuse point (path:line) | Verified |

## 7. Open questions / VERIFY before coding
Resolved (with evidence) vs Open (product vs technical).

## 8. Testing considerations
Unit / integration / manual, keyed to the new and changed units.

## 9. Prior-art reference — verified analogous flow
The existing analogous implementation's real flow by ticket/PR + stable paths. What to take; what NOT
to copy.
```

---

## Rules / calibration
- **Verify before asserting.** Every path, line, signature, binding, and "already exists" claim is
  read from the working tree first. Unverifiable → tag **VERIFY**, don't assert. Re-verify each pass.
- **Mirror, don't invent.** Express changes as "mirror `ExistingThing` at `path:line`" wherever an
  analog exists. The fewer net-new patterns, the better the overview.
- **Trace to the conclusion, including blast radius.** Follow data/signals all the way; enumerate a
  mechanism's subscribers before reusing it.
- **Existing implementations = behavioral reference, never a structural template.** Read the real
  merged code; reference by ticket/PR + stable paths. If it contradicts the brief, it wins — record
  the deviation.
- **Resolve on the ladder:** code → contract → prior art → user. One question at a time. Reverse
  yourself when evidence demands it.
- **Supersede, don't silently diverge.** Contradictions with the brief go in **Deviations**, with the
  reason.
- **One file, internally consistent.** Propagate every changed decision through all dependent
  sections; never leave two sections disagreeing.
- **Built to be implemented from.** The acceptance test: a fresh plan-mode session could execute this
  without re-opening the code to find where/how.
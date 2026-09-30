---
name: technical-overview
description: >
  Turns a feature brief into a self-contained, code-grounded technical overview — the layer between
  the brief (what must be built) and a plan-mode implementation. Restates the requirements and maps each
  to the concrete file(s), classes and methods that satisfy or must change it, expressed as "mirror this
  existing pattern", with every claim verified against the working tree. The implementer needs only this
  document, not the brief. Use when the user says "create a technical
  overview", "map the brief to the code", "find the places in the code we need to adjust",
  "turn this brief into technical requirements", or feeds you a feature brief and wants the
  technical surface pinned down before implementing.
---

# Technical Overview

Turn a **feature brief** into a **single-file, self-contained, code-grounded technical overview**: the
requirements, restated, plus a map from each requirement to the concrete code that satisfies it or must
change. The output is fed into a **fresh Claude Code session in plan mode** to implement the feature —
**on its own, without the brief**. So it must be precise, verified, and complete enough that the
implementer neither redoes the investigation nor needs the brief to know what to build.

The brief is the **starting point**, not a companion document. Once the overview exists, it replaces the
brief for the implementer. The overview is written as if the brief did not exist: it never quotes,
references or corrects the brief.

**Where the overview fits.** Features are prepared in a two-document workflow before implementation:
**feature brief** (a separate skill: what and why) → **technical overview** (this skill: where and how in
the code) → implementation in plan mode. The table shows how the two documents differ:

| | Feature brief | Technical overview (this skill) |
|---|---|---|
| Altitude | *What* must be built & why | *What* (restated, final), plus *where* in the code and *how* (mirror which existing pattern) |
| Contains | requirements, answered technical questions | restated requirements, contracts, file paths, class/method refs, pseudo-code, wiring, exact signatures |
| Forbids | code, line-numbers, "edit file X" | line numbers (reference `Class.Method` instead); references to the brief; deviations; rejected alternatives |
| Audience | any developer/PO | the implementer (plan mode), reading nothing else |

The litmus test for every line here: *"Could the implementer act on this without opening the code to
figure out where/how, and without reading the brief or this conversation to know what/why?"* If not, it
is not specific or complete enough yet.

**Write only the overview.** The feature brief skill has its own instructions. Do not look them up,
load them or follow them while writing the overview: its restrictions (no code, no line-level
references, design questions left unanswered) do not apply here. Read the brief *document* as input;
this file alone defines the overview, and where the two skills' rules differ, this file applies.

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
`.claude/feature-briefs/<brief-name>-technical-overview.md` (the name only records where it came from; the
content does not refer to the brief). Keep everything in this one file. Use the template in **Overview
template** below.

**Traceability for humans lives outside the document.** When you finish (Step 10), tell the user in the
chat which points of the brief the overview changed and why. If the user wants that record kept, write it
to a separate file the implementer is not given — never into the overview.

---

## Core principles: ask, don't guess; VERIFY, don't trust

**Ask, don't guess.** Whenever you are unsure about a requirement or about what the user expects, stop
and ask the user — one question at a time — instead of assuming an answer and building on it.

**Verify, don't trust.** The brief, statements made in the conversation (including the user's), any
earlier draft of this overview, reference implementations, your own memory, and the codebase index are all
**leads, not facts**. Every load-bearing claim — file path, class/method/member
name, method/function signature, overload, "this already exists", "this dependency is already available",
"the call has no parameters", "something else already handles this" — **must be confirmed by reading
the current working tree** before it goes in the document. Plausible-sounding claims about paths,
signatures, and existing wiring are exactly the ones that turn out wrong and break a downstream
implementation.

When you cannot verify a claim, mark it **VERIFY** in the doc rather than asserting it. Re-verify on
each pass — reference-implementation code merges, branches move.

**Reference code by file path and class/method/member name, never by line number.** Line numbers go
stale within days and make a correct document look wrong. Write `ItemConfigFactory.ConvertInstantItem`
(with the file path where it isn't obvious), not `ItemConfigFactory.cs:38-89`. When a method is long
and the spot matters, name the branch or statement ("the `INS_REV` branch of `ConvertInstantItem`").

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

Record this as a dated status note at the top of the doc, because it goes stale.

Also extract from the brief everything the implementer needs to know *what* to build: goal and context,
acceptance criteria, required behaviour, failure handling, what must stay unchanged, out of scope,
constraints. These go into the overview's **Goal & context** and **Requirements** sections, restated in
your own words as settled facts — not as references to the brief, and without its section names or
requirement ids (`R1`, "Open question 2").

### Step 2 — Trace the contracts the feature depends on against this codebase
Identify the contracts the feature must conform to — API endpoints, message/event schemas, data
models, library or module interfaces — and read their authoritative definition (another service, a
shared repo, a schema, or this codebase). Confirm the corresponding types/interfaces this code will
use exist and match. Capture the **exact** shape: is the call parameterless? what does the result
contain — and what does it **not** (data that arrives through a separate channel)? what is done
elsewhere, outside this code (compute, clamp, skip, persist)? Work done outside this code often
eliminates work here — e.g. a parameterless call whose other side iterates the whole set means this
code sends no list. Write the contract shape into the overview's **Goal & context** section, so the
implementer does not have to look it up.

### Step 3 — Map the current code: reuse vs. new
Split the surface in two, both verified by reading the code:
- **Reuse (do not rebuild):** the existing modules/components/handlers/models/functions the feature
  should mirror. For each, record *where it is* and *what it does*, and — critically — **find the
  closest existing analog** for each new piece. The strongest overview expresses nearly every change
  as **"mirror `ExistingThing.Method` in `path`"**. Reuse beats invention.
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
List the questions whose answer **changes the implementation** — start with the brief's
*Deferred to technical overview* list, which holds the design questions the brief intentionally left
unanswered — then resolve each in this order:
1. **Working-tree code** (the contract, the existing pattern).
2. **The contract** (authoritative external truth).
3. **Any existing analogous implementation** as the authoritative *behavioral* reference (Step 6).
4. **The user** — only when 1–3 cannot settle it.

Work through them **one at a time, conversationally** — surface the question, resolve it, confirm, move
on. Be willing to **reverse your own earlier conclusion** when the evidence contradicts it; a decision
reached from the brief or intuition is provisional until verified code or the reference implementation
confirms it.

The conversation is the process; **only its result goes into the document.** A resolved question becomes
a plain statement in the section it belongs to (a requirement, a design fact, a decision), with its
evidence. It is not kept as a question, and it carries no status marker ("RESOLVED", "decided",
"settled", "confirmed with the user"). The open-questions section lists only questions that are still
open, tagged **product** (needs PO) or **technical** (verify at implementation).

### Step 6 — Use any existing analogous implementation as the authoritative behavioral tie-breaker
When a behavioral question is genuinely open, read the **real, merged implementation of the same
feature elsewhere** — another platform, module, or prior feature. Pull the PR (your code host's MCP
tools) to find the changed files, then **read the actual code in its repo**, not the PR description.
Extract behavior/flow/calc/edge-cases; **never** copy structure (the target may have a different
architecture). Reference it by **ticket/PR + stable file paths**, never an ephemeral branch. If it
contradicts the brief, the verified implementation wins: its behaviour becomes the requirement (Step 7).

### Step 7 — Write the overview as the only source of truth
Write at implementation altitude: real file paths, class/method refs, pseudo-code, wiring, exact
signatures. Start with the restated **Goal & context** and **Requirements** (Step 1).

Where deeper investigation **contradicts the brief**, write the verified fact as the requirement or
design fact, with its evidence. **Never quote or correct the brief's claim** ("the brief says X, in fact
Y"): an implementer reading the wrong claim may act on it. The brief is not edited; the overview simply
states what is true. Report the differences to the user in the chat (Step 10).

**Document only the chosen solution.** Leave out alternatives that were considered and rejected. Mention
a rejected approach only as a short prohibition ("don't use X", "do not reorder Y"), and only when an
implementer would plausibly reach for it; no argument history.

### Step 8 — Keep the document internally consistent (propagate, don't append)
This is a living document during investigation. When one decision changes, **propagate it through
every section that depends on it** — the requirements, the key facts, the data-flow diagram, the
CREATE/MODIFY tables, the detailed specs, the decisions, the open-questions list, and the reference
implementation section — rather than appending a contradicting note. A reader must be able to trust any single section
in isolation. One changed conclusion routinely touches several sections; chase all of them.

**The document states only the current conclusion.** Never describe what an earlier draft, the brief or
the conversation said: no "no longer", "instead of", "renamed from", "previously", "as discussed".

### Step 9 — Pin exact signatures and wiring
Before finalizing, confirm by reading the real code: method/function signatures and overloads,
argument/type-parameter order, which dependencies/imports are *already* available, exact
constant/enum/identifier names, capacities/limits, feature-flag names. These are the details that
break a plan-mode implementation if guessed. Anything unverified stays tagged **VERIFY**.

### Step 10 — Finalise for a cold reader
Read the finished document as if you had never seen the brief or this conversation, and check:
- **Self-contained:** goal, acceptance criteria, required behaviour, failure handling, unchanged areas,
  out of scope and constraints are all in the document. Every term the document introduces is defined
  where first used.
- **No outside references:** no mention of the brief, its sections or requirement ids, the conversation,
  or earlier drafts.
- **No history:** no deviations, no quoted wrong claims, no resolved-question log, no status markers, no
  rejected alternatives beyond short prohibitions.
- **Open means open:** the open-questions section holds only genuinely open items.
- **No line numbers** anywhere.

Fix what fails, then tell the user in the chat which points of the brief the overview changed and why
(the human-facing traceability; see **Output**).

---

## Overview template

```markdown
# <TICKET-ID or feature name> — Technical Overview: <short title>

Implementation document for <component>. It states the requirements and maps each of them to the
concrete file/class/method that satisfies or must change it. Everything needed to implement is in
this file.

> **Status, re-assessed <date>.** <git/branch/dependency state: what's merged, what's written, what this
> branch points at>. Every path and member below verified against the current working tree.

## 1. Goal & context
What the feature is, why it exists, and the contracts it depends on (exact shape: fields, calls,
what the other side does and does not do).

## 2. Requirements
Settled facts, in your own words: acceptance criteria; required behaviour (table of behaviours with the
code that implements each today, if the feature changes existing behaviour); failure handling; what must
stay unchanged; out of scope; constraints.

## 3. Key facts the design rests on
Definitions of every term this document introduces, and the verified facts the design depends on,
stated as facts (not as corrections of anything).

## 4. Data flow (target implementation)
Annotated step-by-step of the runtime path, each step tagged [MODIFY]/[NEW]/[REUSE] with file refs.
Then the dependencies (merged → reused; unmerged → sequencing risk), a table of **reusable assets**
(where + what it does + how this feature reuses it) and a short list of **what is genuinely new**.

## 5. Files to CREATE
| # | File | Content (mirror which existing thing) |

## 6. Files to MODIFY
| # | File | Change (mirror which existing thing, in which class/method) |

## 7. Detailed change specs
Per non-trivial change: pseudo-code + the existing pattern it mirrors + why.

## 8. Key technical decisions & risks
Each decision: the chosen solution, the reason, and the verified evidence (code ref / reference-implementation ref).
No rejected alternatives; a short prohibition only where an implementer would plausibly take the wrong
path. Include error/failure handling and any residual risks (with why they're acceptable).

## 9. Reused as-is (no change)
| Concern | Reuse point (path + class/method) | Verified |

## 10. Open questions / VERIFY before coding
Only what is still open, tagged product vs technical. Resolved questions live in the sections above as
statements.

## 11. Testing considerations
Unit / integration / manual, keyed to the new and changed units.

## 12. Reference implementation — verified analogous flow
The existing analogous implementation's real flow by ticket/PR + stable paths. What to take; what NOT
to copy.
```

---

## Rules / calibration
- **Ask, don't guess.** Unsure about a requirement or expectation → ask the user, one question at a time.
- **Write only the overview.** Don't consult or follow the feature brief skill's instructions; the
  brief document is input, this file alone defines the overview.
- **Verify before asserting.** Every path, member name, signature, binding, and "already exists" claim is
  read from the working tree first. Unverifiable → tag **VERIFY**, don't assert. Re-verify each pass.
- **Mirror, don't invent.** Express changes as "mirror `ExistingThing.Method` in `path`" wherever an
  analog exists. The fewer net-new patterns, the better the overview.
- **No line numbers.** Reference code by path and class/method/member name; line numbers go stale.
- **Trace to the conclusion, including blast radius.** Follow data/signals all the way; enumerate a
  mechanism's subscribers before reusing it.
- **Existing implementations = behavioral reference, never a structural template.** Read the real
  merged code; reference by ticket/PR + stable paths. If it contradicts the brief, it wins — its
  behaviour becomes the requirement.
- **Resolve on the ladder:** code → contract → reference implementation → user. One question at a time. Reverse
  yourself when evidence demands it.
- **Self-contained.** Requirements are restated in the document. Never reference the brief, its
  sections or requirement ids, or the conversation. Define every term you introduce.
- **State facts, not corrections.** Where the brief is wrong, write what is true. No deviations
  section, no quoted wrong claims, no "no longer / instead of / previously". Report the differences to
  the user in the chat.
- **Only the chosen solution.** No rejected alternatives, no resolved-question log, no status markers.
  A short prohibition is fine where an implementer would plausibly take the wrong path.
- **One file, internally consistent.** Propagate every changed decision through all dependent
  sections; never leave two sections disagreeing.
- **Built to be implemented from.** The acceptance test: a fresh plan-mode session, given only this
  document, could execute it without re-opening the code to find where/how and without the brief or
  this conversation to know what/why.
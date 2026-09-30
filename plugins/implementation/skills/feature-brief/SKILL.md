---
name: feature-brief
description: >
  Produces a single-file feature technical brief for a ticket or feature request — the layer between
  product acceptance criteria and an implementation plan. Combines the authoritative spec (AC + flow)
  with the technical requirements and the answered technical questions a developer needs before
  implementing. Works from a tracker ticket or a plain description. Use when the user says "create a
  feature brief", "brief me on <TICKET-ID>", "analyze this ticket/feature", or otherwise wants a
  feature understood end-to-end before coding.
---

# Feature Brief

Produce a **single-file feature technical brief** for a unit of work — a tracker ticket or a plain
feature request: a document that lets any developer, PO or LLM understand a feature end-to-end —
what must be built and why — without redoing the investigation.

**Where the brief fits.** Features are prepared in a two-document workflow before implementation:
**feature brief** (this skill: what and why) → **technical overview** (a separate skill: where and how
in the code) → implementation in plan mode. The technical overview turns the brief into the
self-contained, code-level document the implementation session works from. The brief is its input and
a reference for humans; it is not handed to the implementer.

**Write only the brief.** The technical overview has its own instructions. Do not look them up, load
them or follow them while writing the brief, and do not produce any of its content (code references,
design decisions, file-by-file changes). Everything the brief needs is in this file; where the two
skills differ, this file applies.

A feature brief sits **between** two things and is neither of them:
- It is **more** than acceptance criteria: it captures the technical requirements and answers the
  technical questions that determine *how the feature must behave* (e.g. error handling, which data
  source feeds a value, which endpoint is called and what it returns).
- It is **less** than an implementation plan: it does **not** contain code, file line-numbers,
  wiring instructions, or step-by-step "edit this file" tasks.

The litmus test for every line: *"Does this shape what must be built, or is it telling someone how
to build it?"* Keep the former, drop the latter. The one exception — see Rules — is the
**contract** (the calls/endpoints/schemas/types the feature depends on), which is named explicitly
because it IS the requirement.

The same test applies to **questions**, not just to lines of output: a question that only decides
*how* to build (structure, placement, naming, which existing code to extend) is not answered in the
brief — it is handed to the next step (see Step 5).

## Core principles

**Ask, don't guess.** Whenever you are unsure about a requirement or about what the user expects, stop
and ask the user — one question at a time — instead of assuming an answer and building on it. This
applies within the brief's interview scope: requirement and spec questions only; design questions are
deferred, not asked (Step 5).

**Verify, don't accept.** The ticket, related work items, statements made in the conversation
(including the user's), reference-implementation code, the codebase index and your own memory are **leads, not
facts**. Check every claim against its source — the code, the contract's authoritative definition, or
the spec the user provided — before it goes into the brief. What you cannot verify, say so.

---

## When to use
- The user wants a ticket/feature investigated and documented before implementation.
- The feature touches several parts of the system (services, modules, or multiple client platforms)
  and the technical surface needs to be pinned down before coding.

## When NOT to use
- The user wants the actual implementation plan or code → that is a separate, lower-altitude step.
- A trivial change with no open technical questions.

---

## Output

**One Markdown file.** Save to `.claude/feature-briefs/<descriptive-kebab-case-name>.md` (create the
directory if missing). Derive the name from the ticket/feature (e.g. `user-profile-export.md`).
Keep everything in this single file — do not split into companion docs.

---

## Process

### Step 1 — Situate the work
Establish what you're briefing and its surroundings. **If it's a tracker ticket**, pull it and its
context (use your issue tracker's MCP tools, if available): the item itself, its **parent story**,
**sibling sub-tasks**, and any **linked/related items**, plus any linked wiki/docs pages. **If it's a
plain feature request** (no tracker), the user's description is the starting point — capture it, then
ask for the surrounding context: what larger effort it belongs to and any related work. Either way,
establish two scopes explicitly and keep them separate throughout:
- **Whole-feature scope** — what the entire feature/effort is about.
- **This slice's scope** — the part this brief is for.

If the work item has no written description (common for tickets), the spec lives elsewhere — go to
Step 2.

### Step 2 — Get the authoritative spec — DO NOT reconstruct it
The acceptance criteria and flow are **product truth**. Do not invent or infer them from code or
related work. **Ask the user** for the spec — screenshots of the flow diagram / AC, a design doc,
or Figma. Transcribe what they provide faithfully into the brief. Only after you have the real spec
do you start answering *how* it must work.

### Step 3 — Trace the contracts the feature depends on (the source of truth)
Identify the contracts and boundaries the feature must conform to — whatever constrains how it
behaves: API endpoints, message/event schemas, data models, library or module interfaces, config.
Read the authoritative definition (in another service, a shared repo, a schema, or this codebase).
Capture, at requirement altitude:
- which **inputs/calls** are involved and their parameters (or lack thereof),
- the **shape of what comes back** and what it contains (and, crucially, what it does **not** — e.g.
  data that arrives through a separate channel or a later step),
- **effects outside this code's control** the feature must account for (what is
  computed/persisted/clamped elsewhere, what happens asynchronously, what is best-effort vs. fatal).
Confirm the corresponding **types/interfaces** the feature will use exist and match.
If the project documents cross-cutting constraints of its own (e.g. in its project documentation),
check them here — they are requirements even when the ticket does not mention them.

### Step 4 — Trace current behaviour
Find what the system does today that this work changes or must preserve, and state it as
**behaviour** ("the list shows only items of kind X", "this value is rounded up"), not as components
to reuse or extend. Note constraints that behaviour imposes (e.g. "this view displays at most N
items"). Code locations are evidence for your own verification and for the Reference implementation section — they
do not become a plan.

State behaviour **only as it is observable from outside**: what a user, tester or other system sees.
Do not describe the **mechanism** — how the code tells cases apart, where it dispatches, what it
filters or keys on ("today the client distinguishes X by field Y"). Mechanism claims are design facts;
they belong to the technical overview, and a wrong one misleads everything built on it. If a
mechanism statement is unavoidable (e.g. it explains a constraint), verify it in the code first and
mark it as a lead to be confirmed, not as a requirement.

### Step 5 — Surface AND answer the requirement-level questions
A question belongs in the brief only if its answer changes **observable behaviour or a constraint**:
what a user, tester, or other system sees; which data source feeds a value; how failure presents;
what must keep working; what is out of scope. Typical examples: error/failure handling, in-flight UX,
how results/states are presented, how state refreshes.

**Gate every question before you answer it or ask the user:** *"Would two implementations that answer
this differently be indistinguishable from the outside?"* If yes, it is a **design question** —
where logic lives, which class/type/dispatch mechanism, how old and new paths coexist, which helper
to reuse or delete. Do **not** answer it, recommend an option for it, or ask the user about it.
Record it in one line under *Deferred to technical overview* and move on.

Answer each requirement-level question from code/contract where possible, or escalate to the user.
Error handling specifically must be addressed — it is a requirement, not an implementation detail.

**Only the answer goes into the brief.** A resolved question becomes a plain statement in the section
it belongs to (a requirement, contract, constraint or out-of-scope item), with its reason where the
reason matters. It is not kept as a question, and it carries no status marker ("decided", "resolved",
"settled"). The *Open questions* section lists only questions that are still open, tagged
**product** (needs PO/design) or **technical**.

### Step 6 — Use any existing analogous implementation as a reference, not a template
If the feature (or a close variant) is already implemented elsewhere — another platform, another
module, or a prior similar feature — use it as a **behavioural example** for flow, calculation logic,
and edge cases, never as a structural template to copy (the target may have a different architecture).
Reference such code by **ticket/PR** and **stable file paths**, never by an ephemeral branch name.

### Step 7 — Write the brief (single file, using the template below)
Brief altitude: keep the *what/why*, drop code and line-numbers. Distinguish whole-feature from
this-slice scope, and open questions by product vs technical.

### Step 8 — Iterate
A brief is a living document during investigation. When a new fact changes a conclusion (e.g. a
framework capability that flips a design choice), update the affected sections and any decisions that
depended on them — don't just append.

**The brief states only the current conclusion.** Never describe what an earlier draft or the
conversation said: no "no longer", "instead of", "previously", "as discussed", and no status markers.

---

## Brief template

```markdown
# <TICKET-ID or feature name> — <short title>

## Goal & context
- One-paragraph statement of what this work delivers and why.
- Work item (ticket/PR/request), parent story or related items if any, feature name + spec source
  (wiki/design doc/Figma/user description).
- Scope boundary: what belongs to the WHOLE feature vs. THIS slice.

## Spec (authoritative — from <source>)
- The flow (step by step).
- The acceptance criteria.
  (Transcribed from the provided design/screenshots — not reconstructed.)

## Technical requirements
### Contracts & dependencies
- Inputs/calls + params; shape of what comes back + what it contains and what it does NOT.
- Effects outside this code's control the feature must account for (computed/persisted/clamped
  elsewhere, async, best-effort vs fatal).
- Confirmed types/interfaces the feature will use.
### Behaviour requirements
- In-flight + error/failure handling (required — how the user experiences loading and failure).
- Each behaviour the spec implies (data sources for computed values, how results/state are presented,
  state refresh, etc.), at the "what must happen" level.
### Constraints
- Hard limits that force design decisions (capacities, caps, clamping done elsewhere, feature flags).

## Out of scope (for this slice)
- Explicitly excluded items + where they live instead.

## Reference implementation (example, not a template)
- Any existing analogous implementation by ticket/PR + stable file paths. Behaviour to take from it;
  what NOT to copy.

## Open questions
- Open — product (needs PO/design).
- Open — technical (requirement-level; affects behaviour — verify during implementation).
  (Only what is still open. Answered questions live in the sections above as statements.)

## Deferred to technical overview
- Design questions surfaced during investigation — one line each, stated neutrally, **not answered
  and no recommendation**. The technical overview resolves them.
```

---

## Rules / calibration
- **Altitude:** brief = requirements + answered technical questions. **No code snippets, no file
  line-numbers, no wiring steps, no "edit file X" task list.**
- **The one exception:** name the **contracts** explicitly — the calls/endpoints/schemas/types the
  feature depends on. That contract *is* a requirement.
- **Error handling is in scope** — it changes the implementation approach, so it belongs in the brief
  even though it rarely appears in the AC.
- **Interview scope:** questions to the user are limited to spec gaps and requirement-level questions
  (Step 5 gate). Never ask the user to choose between code designs here. Take positions on
  requirements, not on structure — design positions belong to the technical overview.
- **Never reconstruct the spec** — get it from the user/design.
- **Ask, don't guess.** Unsure about a requirement or expectation → ask the user, one question at a time
  (within the interview scope above).
- **Verify, don't infer.** Every claim about current behaviour or a contract is read from the code or the
  contract's authoritative definition, not inferred from names, tickets, related work or unchecked
  statements. Unverified → say so.
- **Behaviour, not mechanism.** Describe what is observable from outside; leave how the code achieves it
  to the technical overview (Step 4).
- **Write only the brief.** Don't consult or follow the technical overview's instructions; this file
  alone defines the brief.
- **Existing implementations are references, not templates.**
- **One file.** Keep it current as facts arrive (Step 8), rather than appending contradictions.
- **Answers, not a question log.** Resolved questions become statements; *Open questions* holds only
  what is open.
- **Separate** whole-feature vs this-slice scope, and open questions by product vs technical.
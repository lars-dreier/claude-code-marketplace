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
feature request: a document that lets any developer (or LLM) understand a feature end-to-end and
start implementing without redoing the investigation.

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

### Step 4 — Trace the current code (current state + reuse points)
Find what already exists vs. what this work adds. Identify the existing components, handlers,
models, and patterns the feature should reuse — **named at the requirement level** (what they are
and what they do), not as line-numbered code. Note relevant constraints they impose (e.g. "this view
displays at most N items").

### Step 5 — Surface AND answer the technical questions
List the questions whose answers **change the implementation** — error/failure handling, in-flight
UX, which data source feeds a computed value, how results/states are presented, how state refreshes.
Then **answer each**: from code/contract where possible, or escalate to the user. Track each as
**resolved** or **open**, and tag open ones as **product** (needs PO/design) vs **technical**.
Error handling specifically must be addressed — it is a requirement, not an implementation detail.

### Step 6 — Use any existing analogous implementation as a reference, not a template
If the feature (or a close variant) is already implemented elsewhere — another platform, another
module, or a prior similar feature — use it as a **behavioural example** for flow, calculation logic,
and edge cases, never as a structural template to copy (the target may have a different architecture).
Reference such code by **ticket/PR** and **stable file paths**, never by an ephemeral branch name.

### Step 7 — Write the brief (single file, using the template below)
Brief altitude: keep the *what/why*, drop code and line-numbers. Distinguish whole-feature from
this-slice scope, resolved from open, product from technical.

### Step 8 — Iterate
A brief is a living document during investigation. When a new fact changes a conclusion (e.g. a
framework capability that flips a design choice), update the affected sections and any decisions that
depended on them — don't just append.

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

## Prior-art reference (example, not a template)
- Any existing analogous implementation by ticket/PR + stable file paths. Behaviour to take from it;
  what NOT to copy.

## Open questions
- Resolved decisions worth recording (with the reason).
- Open — product (needs PO/design).
- Open — technical (verify during implementation).
```

---

## Rules / calibration
- **Altitude:** brief = requirements + answered technical questions. **No code snippets, no file
  line-numbers, no wiring steps, no "edit file X" task list.**
- **The one exception:** name the **contracts** explicitly — the calls/endpoints/schemas/types the
  feature depends on. That contract *is* a requirement.
- **Error handling is in scope** — it changes the implementation approach, so it belongs in the brief
  even though it rarely appears in the AC.
- **Never reconstruct the spec** — get it from the user/design.
- **Existing implementations are references, not templates.**
- **One file.** Keep it current as facts arrive (Step 8), rather than appending contradictions.
- **Separate** whole-feature vs this-slice scope, and resolved vs open (product vs technical).
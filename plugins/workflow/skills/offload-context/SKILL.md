---
name: offload-context
description: >
  Creates a context offload file that captures everything needed to continue the current
  work in a fresh conversation. Use this skill whenever the user says "save context",
  "offload context", "I want to continue this later", "save progress", or any variation.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Offload Context

Review the current conversation and create a context file that lets a future conversation
pick up exactly where this one left off — with zero re-exploration required.

---

## Step 1 — Choose a filename

Derive a short, descriptive kebab-case name from the topic of the current work.

Save the file to:
```
.claude/tasks/<descriptive-kebab-case-name>.md
```

Create the directory if it does not exist:
```bash
mkdir -p .claude/tasks
```

---

## Step 2 — Write the offload file

The file must contain every section below that is relevant to the current work.
Omit a section only if it is genuinely not applicable — do not leave it empty.

### Goal
What is being built, investigated, or understood — and why. Include enough motivation
that the next conversation grasps the intent without asking.

### Progress
What has already been explored, decided, or implemented. What works. What doesn't.
Be explicit about dead ends so the next conversation doesn't retrace them.

### Key Findings
What was discovered: relevant code structure, data flow, architectural decisions, key
files and their roles. Include file paths and line numbers where they matter.

### Next Steps
What remains. The form depends on the task:
- For investigations: threads still to follow, questions still to answer
- For implementation: ordered steps — which file(s), what change, and why
- For explanations: areas not yet covered, follow-up questions to explore

Include open decisions or unresolved questions as a sub-list here.

### Important Context
Non-obvious things the next conversation must know: constraints, gotchas, naming
conventions, framework quirks, prior decisions and their reasons.

---

## Step 3 — Confirm

After saving, tell the user the exact file path. One sentence is enough.

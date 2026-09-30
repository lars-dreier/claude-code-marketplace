# Documentation Style

Shared editorial rules for everything written into `.claude/documentation/`.
Both `create-documentation` and `refresh-documentation` follow this file.

## Audience

The main audience is an LLM (Claude Code), not a human browsing a wiki. Every line gets loaded
into a context window. Content that is true but not useful is a cost: at best it consumes
context, at worst it misleads. Documentation should be as long and detailed as necessary but as
short as possible.

## Rules

1. **Current state only.** Document how the code works now. No changelogs, no migration paths,
   no "this used to be X", no "since version Y", no "no longer", no commit hashes, no editor or
   dependency revisions nobody acts on. History lives in git.

2. **No line numbers.** Reference code as file plus symbol — `ImageHelper.ProgressAnimation`,
   `Assets/Editor/PathHelper.cs` — never `PathHelper.cs:24` or "lines 88-104". Line numbers go
   stale on the next edit and are the fastest way for a document to start lying.

3. **Do not document absence.** Delete content that exists only to say something is unused, not
   applicable, or not present, rather than annotating it as such.
   *Exception:* state an absence when it corrects an assumption the code actively invites — for
   example, a path-building function that returns an output path for an image that is never
   written. Removing a likely wrong inference earns its lines; cataloguing everything that does
   not exist does not.

4. **Do not state the obvious.** Skip whatever a competent reader infers from the surrounding
   sentence or from the technology itself.

5. **No duplication across files.** One fact, one home. Cross-reference by filename instead of
   restating.

6. **No filler.** Drop "note that", "it is worth knowing", "in practice", "simply",
   "essentially", "of course". State the fact.

7. **Verify before writing.** Every claim must come from the current source — not from the
   previous version of the document, and not from inference.

## Structure

Every file carries YAML frontmatter with `title`, `description`, `category`, `tags`,
`last_updated` (ISO 8601 UTC) and `related_docs`; then an `# Title`; then
`## Table of Contents`; then a `---` separator before the first body section. TOC entries must
match the `##` headings exactly.

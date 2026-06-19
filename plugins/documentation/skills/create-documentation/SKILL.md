---
name: create-documentation
description: >
  Analyzes the codebase and generates a comprehensive `.claude/documentation/` knowledge base
  for Claude Code — a multi-phase discovery, design, and generation workflow tailored to the
  project's actual stack, architecture, and conventions. Use when the user says
  "create documentation", "document this project", "generate project docs", "build a knowledge
  base", "set up .claude/documentation", or any variation requesting fresh project
  documentation be written from scratch.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Agent
---

# Create Comprehensive Project Documentation

Analyze the current codebase and generate comprehensive project documentation in
`.claude/documentation/`.

This is a multi-phase analysis that will create a complete knowledge base about the project's
structure, architecture, patterns, and development workflows.

The main audience for these documents is an llm/ai (specifically you, Claude Code). The resulting
documentation should be as long and detailed as necessary but as short as possible.

## Phase 1: Project Discovery

Analyze the project to understand:

1. **Technology Stack Detection**:
    - Identify primary language(s) and version
    - Detect frameworks and major libraries
    - Identify build systems and package managers
    - Detect target platforms (web, mobile, desktop, etc.)
    - Find test frameworks

2. **Project Structure Analysis**:
    - Map the directory structure
    - Identify main source directories
    - Find test directories
    - Locate configuration files
    - Identify resource/asset directories

3. **Architectural Pattern Detection**:
    - Identify architectural patterns (MVC, MVVM, Clean Architecture, etc.)
    - Detect dependency injection frameworks
    - Find design patterns in use
    - Identify communication patterns (events, signals, messages)
    - Detect data access patterns

4. **Domain Analysis**:
    - Identify main feature areas/modules
    - Find core domain models
    - Detect service layer patterns
    - Identify shared utilities

## Phase 2: Design Documentation Structure

Based on your Phase 1 analysis, design an appropriate documentation structure. Consider:

**What documentation categories are actually needed for this specific project?**

Don't force categories that don't apply. Instead, design documentation that fits the project's actual characteristics.

### Documentation Category Guidelines

Consider creating documentation for these areas **if they are relevant to the project**:

#### Project Overview & Setup
- Project name, purpose, and goals
- Technology stack with versions
- Target platforms and runtime requirements
- Project structure and organization
- Build system and commands
- Key dependencies and libraries

**Suggested approach**: Create 1-2 files that cover project basics. Consider names that match the project's domain (e.g., "game-system.md" for a game, "api-reference.md" for an API, etc.)

#### Architecture & Design
- Architectural patterns in use
- System design and component relationships
- Module organization
- Data flow and control flow
- Infrastructure and external integrations

**Suggested approach**: If the project has significant architectural patterns, create dedicated files. For simple projects, this might be merged with overview. Consider domain-specific names (e.g., "game-architecture.md", "event-system.md", "plugin-system.md")

#### Domain-Specific Concepts
- Core domain models and entities
- Business logic organization
- Domain-specific patterns
- Key workflows and processes
- State management

**Suggested approach**: Only create if the project has clear domain concepts. Use names that reflect the actual domain (e.g., "character-system.md", "combat-mechanics.md", "data-models.md")

#### Development Workflow
- How to build and run the project
- Development patterns and best practices
- What Claude Code can and cannot do
- Common pitfalls to avoid
- Testing approach and commands
- Contribution guidelines

**Suggested approach**: Essential for most projects. Consider splitting or combining based on complexity. Might be called "development.md", "getting-started.md", or "contributor-guide.md"

#### Code Style & Conventions
- Naming conventions found in the codebase
- File organization patterns
- Formatting rules (indentation, braces, etc.)
- Documentation standards
- Language-specific idioms

**Suggested approach**: Only create if there are established patterns worth documenting. Consider language-specific names (e.g., "typescript-style.md", "coding-conventions.md")

#### Testing
- Test frameworks in use
- Test organization and structure
- How to run tests
- Test writing guidelines
- Coverage expectations

**Suggested approach**: Create if testing infrastructure exists. Might be standalone or merged with development docs. Consider "testing.md" or "test-guide.md"

#### Related Systems
- Multi-repository information
- External system integrations
- API documentation
- Plugin/extension systems

**Suggested approach**: Only if applicable. Use descriptive names based on what they document.

## Phase 3: Generate Documentation Files

Based on your design from Phase 2:

1. **Decide on file names** that make sense for this specific project
2. **Decide what to include in each file** - avoid duplication, ensure logical grouping
3. **Create comprehensive documentation** in `.claude/documentation/`
4. **Use the project's actual terminology** in filenames and content

Create 3-8 documentation files typically (more for complex projects, fewer for simple ones).

## Analysis Guidelines

### Be Thorough and Accurate

- Read actual code files to understand patterns
- Don't guess - if you can't determine something, say so
- Look at multiple examples to establish patterns
- Verify your findings across different parts of the codebase

### Search Strategy

Use the Agent tool with subagent_type=Explore for:

- Finding architectural patterns across the codebase
- Discovering naming conventions and code styles
- Understanding module organization
- Identifying common development patterns

Use direct Read/Grep/Glob tools only for:

- Reading specific configuration files (package.json, build files, etc.)
- Examining specific example files once you've found them
- Reading README or existing documentation

### Technology Detection

Look for these files to identify technology:

- `package.json`, `package-lock.json` - Node.js/JavaScript projects
- `pom.xml`, `build.gradle` - Java projects
- `requirements.txt`, `pyproject.toml`, `setup.py` - Python projects
- `Cargo.toml` - Rust projects
- `go.mod` - Go projects
- `.csproj`, `.sln` - C#/.NET projects
- `composer.json` - PHP projects
- `Gemfile` - Ruby projects

### Architecture Detection

Look for these patterns:

- **Dependency Injection**: Search for DI container registrations, constructor injection patterns
- **MVC/MVVM**: Look for Model, View, Controller/ViewModel directories or naming patterns
- **Repository Pattern**: Search for repository interfaces and implementations
- **Service Layer**: Look for service classes and interfaces
- **Command Pattern**: Search for command classes
- **Event/Signal Systems**: Look for event emitter patterns or signal implementations

### Code Style Analysis

Analyze actual code files to determine:

- Naming conventions (examine variable, function, class names)
- Indentation (tabs vs spaces, size)
- Brace style (same line vs new line)
- Import/using statement organization
- Documentation comment style
- File organization patterns

## Output Format

Each file must begin with a YAML frontmatter block, followed by the main title and a table of contents:

```markdown
---
title: "Human-readable title"
description: "One-sentence description of what this file covers and when to use it."
category: "reference|guide|overview|architecture"
tags: ["tag1", "tag2", "tag3"]
last_updated: "YYYY-MM-DDTHH:MM:SSZ"
related_docs: ["other-file.md"]
---

# Title

## Table of Contents
1. [Section One](#section-one)
2. [Section Two](#section-two)
   - [Subsection](#subsection)

---

## Section One
...
```

- `category`: one of `reference`, `guide`, `overview`, or `architecture`
- `tags`: lowercase kebab-case keywords relevant to the content
- `last_updated`: current UTC date and time in ISO 8601 format `YYYY-MM-DDTHH:MM:SSZ` — if not available from
  context, run `date -u +%Y-%m-%dT%H:%M:%SZ` to obtain it
- `related_docs`: list of other documentation files that are closely related (empty list if none)
- The table of contents must list all `##` sections and, where helpful, `###` subsections
- Use a horizontal rule (`---`) after the table of contents to separate it from the body

For the body, use clear markdown formatting:

- Use `#` for main title, `##` for sections, `###` for subsections
- Use code blocks with language hints for examples
- Use lists for structured information
- Use tables when comparing multiple items
- Add examples from the actual codebase when relevant
- Include file paths and locations for reference

## Important Notes

1. **Do not modify any existing code** - only create documentation files
2. **Be project-agnostic** - don't assume this is any specific type of project
3. **Base documentation on actual findings** - don't invent patterns that aren't there
4. **Skip sections that don't apply** - not all projects need all documentation
5. **Be comprehensive but concise** - provide enough detail to be useful but avoid redundancy

## Execution

Follow this workflow:

1. **Phase 1 - Discovery**: Thoroughly analyze the codebase to understand its characteristics
2. **Phase 2 - Design**: Based on your findings, design a custom documentation structure:
   - List the documentation files you plan to create with their proposed names
   - Explain why each file is needed and what it will cover
   - Ensure no overlap between files
   - Present this plan to the user and **wait for explicit approval before creating any files**. Do not proceed to Phase 3 until the user confirms.
3. **Phase 3 - Generation**: Create the documentation files you designed

**Important**: In Phase 2, explicitly present your proposed documentation structure (file names and their purposes) and **stop**. Do not create any files until the user has reviewed and approved the plan. Only proceed to Phase 3 after receiving explicit confirmation.

After completion:

1. **Write `.claude/documentation/last_refresh`** — a plain-text file containing only the current UTC date and time
   in ISO 8601 format (e.g. `2026-03-25T10:42:00Z`). If the exact UTC time is not available from context, run
   `date -u +%Y-%m-%dT%H:%M:%SZ` to obtain it first. This timestamp is used by the **refresh-documentation** skill to
   scope its git log to only changes since this run.
2. **Instruct the user to run `/clear` and then invoke the `update-documentation-index` skill** so the index.md file
   is generated with empty context.
3. Inform the user:
    - Which documentation files were created (with their actual names)
    - The rationale behind the chosen structure
    - Any sections that were skipped and why
    - Suggestions for manual review or additions
    - That they should review the generated documentation

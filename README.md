# Claude Code Marketplace

A [Claude Code](https://claude.com/claude-code) plugin marketplace with skills for
documentation, implementation planning, and development workflow.

## Install

Add the marketplace, then install the plugins you want:

```bash
/plugin marketplace add lars-dreier/claude-code-marketplace
/plugin install documentation
/plugin install implementation
/plugin install workflow
```

Forking? Swap in your own `owner/repo` (or a full git URL / local path).

## Plugins

### `documentation`

Create and maintain project documentation.

| Skill | Purpose |
| --- | --- |
| `check-documentation-index` | Read the documentation index and load the docs relevant to the current task. |
| `create-documentation` | Author new project documentation. |
| `refresh-documentation` | Update existing docs as the code changes. |
| `update-documentation-index` | Keep the documentation index in sync. |

### `implementation`

Turn tickets and feature requests into implementation-ready artifacts.

| Skill | Purpose |
| --- | --- |
| `feature-brief` | Produce a single-file feature technical brief from a ticket or description. |
| `technical-overview` | Produce a technical overview of a feature or area. |

### `workflow`

Development workflow helpers.

| Skill | Purpose |
| --- | --- |
| `review-branch` | Review the current branch against the default branch (optionally against a spec). |
| `offload-context` | Offload context to keep a working session focused. |

## Repository layout

```
.claude-plugin/marketplace.json     Marketplace manifest (lists the plugins)
plugins/<name>/.claude-plugin/plugin.json   Per-plugin manifest
plugins/<name>/skills/<skill>/SKILL.md      Auto-discovered skills
```

## License

[MIT](./LICENSE)

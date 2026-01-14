<!--
Sync Impact Report

- Version change: 0.0.0 → 1.0.0
- Modified principles: Template placeholders → Bronze-tier constitution principles
- Added sections: Project Guardrails; Workflow & Quality Gates
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (no changes needed)
  - ✅ .specify/templates/spec-template.md (no changes needed)
  - ✅ .specify/templates/tasks-template.md (no changes needed)
- Deferred TODOs:
  - TODO(RATIFICATION_DATE): Confirm original ratification date
  - TODO(RATIFICATION_DATE): Set ratified date (suggestion: 2026-01-12) without changing version if desired
-->

# My AI Employee (Hackathon Zero) Constitution

## Core Principles

### I. Bronze-First Scope (NON-NEGOTIABLE)
Build strictly to Bronze tier first.

- MUST implement only Bronze deliverables initially: Obsidian vault, one watcher, Claude vault I/O, and skills.
- MUST NOT introduce MCP servers or external actions in Bronze (no email sending, posting, payments).
- SHOULD allow a `Plans/` folder even though only `Inbox/`, `Needs_Action/`, and `Done/` are required.

### II. Local-First Vault as Source of Truth (NON-NEGOTIABLE)
Treat the Obsidian vault as the single source of truth.

- MUST store operational state and artifacts in local markdown inside the vault.
- MUST keep the required vault structure:
  - `Inbox/`
  - `Needs_Action/`
  - `Done/`
  - `Dashboard.md`
  - `Company_Handbook.md`
- MUST use the repo vault path convention: `My_AI_Employee/AI_Employee_Vault/`.

### III. Agent Skills for All AI Behavior (NON-NEGOTIABLE)
Express all AI behavior as Claude Code Agent Skills.

- MUST implement AI workflows via skills under `.claude/skills/`.
- MUST be able to run all automation via Claude Code prompts invoking skills.
- MUST avoid hidden manual steps other than starting the watcher process.

### IV. Vault Safety and Non-Destructive Operations (NON-NEGOTIABLE)
Prevent accidental data loss in a local-first vault.

- MUST NOT delete user-authored vault content.
- MUST preserve YAML frontmatter when moving/processing markdown action items.
- SHOULD prefer append/section updates over full-file rewrites (especially for `Dashboard.md`).
- MUST ask for clarification when the vault root is ambiguous or when an edit risks overwriting user notes.

### V. Secure Configuration and Secrets Hygiene (NON-NEGOTIABLE)
Keep credentials out of git and out of the vault.

- MUST NOT commit secrets.
- MUST store credentials/configuration in `.env` (gitignored) or OS secret stores.
- SHOULD redact sensitive values from logs and example files.

### VI. Testable, Minimal, Reliable Implementation
Keep changes small, verifiable, and resilient.

- MUST prefer minimal diffs and avoid unrelated refactors.
- MUST make the watcher resilient: log errors, continue running, and prevent duplicates (tracked IDs/hashes).
- SHOULD provide deterministic end-to-end validation steps for Bronze.

## Project Guardrails

### Technology & Tooling

- Python: 3.13+ (or latest available)
- Package manager: uv
- Tests: pytest
- Obsidian: vault of markdown files
- Claude Code: used as the terminal-based reasoning and write-back engine

### Constraints

- Bronze tier only: no MCP servers and no external actions.
- Path convention: `My_AI_Employee/AI_Employee_Vault/` is the default vault root.

## Workflow & Quality Gates

- MUST keep the workflow demonstrable end-to-end:
  - drop file → `Needs_Action` item → Claude processes → plan + dashboard update → item moved to `Done/`
- MUST add tests for watcher core logic and action-item formatting.
- SHOULD keep formatting consistent; avoid heavy tooling unless already present in the repo.

### Artifact Conventions (Bronze)

#### Action Item Contract (Needs_Action)

- Action items MUST be Markdown files stored under `Needs_Action/`.
- Action items SHOULD include YAML frontmatter with (at minimum):
  - `type`: `email|file_drop|manual`
  - `received`: ISO timestamp
  - `status`: `pending|processed`
  - `priority`: `high|medium|low|auto` (optional)
  - optional: `source_id`, `from`, `subject`

#### Plan Output Location

- Plans MUST be written to `Plans/` when that folder exists (recommended).
- If `Plans/` is not used, the chosen plan output location MUST be consistent and documented in the feature spec.

#### Watcher File Handling Default

- Default behavior: the watcher writes a Markdown action item that references the original dropped file path (metadata-only).
- Copying dropped files into the vault is OPTIONAL and must be an explicit design choice documented in the plan (and ADR if it has long-term impact).


## Governance

- This constitution supersedes feature specs, plans, and tasks when there is conflict.
- Amendments MUST update the version and record the rationale.
- Significant architecture choices with multiple viable options and long-term impact SHOULD be documented with an ADR.
  - Example: whether the watcher copies dropped files into the vault vs storing metadata-only links.

**Version**: 1.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-12

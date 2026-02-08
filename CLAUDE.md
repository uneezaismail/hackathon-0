# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

## Active Technologies
- Python 3.13+ + `watchdog`, `python-frontmatter` (plus existing repo deps) (001-bronze-ai-employee)
- Local files (Obsidian vault + a local non-vault state file for dedupe) (001-bronze-ai-employee)
- Python 3.13+ + FastMCP (MCP server framework with Pydantic v2), Playwright (browser automation), google-api-python-client (Gmail API), google-auth-oauthlib (OAuth 2.0), watchdog (filesystem monitoring, already in Bronze), python-frontmatter (YAML parsing, already in Bronze) (002-silver-ai-employee)
- Obsidian vault (local markdown files), JSONL audit logs (/Logs/YYYY-MM-DD.json), local queue files for offline resilience (002-silver-ai-employee)
- Python 3.13+ + OdooRPC (Odoo JSON-RPC client), facebook-sdk (Facebook Graph API), tweepy (Twitter API v2), FastMCP (MCP framework, from Silver tier), keyring (credential storage), watchdog (filesystem monitoring, from Bronze tier), python-frontmatter (YAML parsing, from Bronze tier), Playwright (browser automation, from Silver tier) (003-gold-ai-employee)
- Obsidian vault (local markdown files), Odoo database (self-hosted PostgreSQL), JSONL audit logs (/Logs/YYYY-MM-DD.json), local queue files for offline resilience, Ralph state file (.ralph_state.json) (003-gold-ai-employee)

## Gold Tier AI Employee Skills

This project uses 14 specialized skills that work together to create an autonomous AI Employee system. Skills are automatically invoked based on context - you don't need to manually call them in most cases.

### Skill Categories and Usage

#### 1. INPUT LAYER (Perception) - 2 Skills

**watcher-runner-filesystem** (Bronze Tier)
- Monitors local drop folder for new files
- Creates action items in `/Needs_Action/`
- Use when: Setting up Bronze tier, testing filesystem watcher
- Trigger: "run filesystem watcher", "start Bronze tier watcher"

**multi-watcher-runner** (Silver/Gold Tier)
- Orchestrates Gmail, LinkedIn, WhatsApp, and filesystem watchers
- Monitors multiple input sources simultaneously
- Creates action items in `/Needs_Action/`
- Use when: Setting up Silver/Gold tier, running all watchers
- Trigger: "start all watchers", "run multi-watcher", "monitor Gmail WhatsApp LinkedIn"

#### 2. PROCESSING LAYER (Reasoning) - 3 Skills

**obsidian-vault-ops** (Core Infrastructure)
- Safely read/write/move files in Obsidian vault
- Preserves YAML frontmatter, prevents data loss
- Used by: ALL other skills for file operations
- Use when: Any vault file operation needed
- Trigger: Automatic - invoked by other skills

**needs-action-triage** (Core Processing)
- Processes items from `/Needs_Action/` folder
- Reads `Company_Handbook.md` for rules
- Creates plans in `/Plans/` folder
- Determines if approval needed
- Use when: Processing new action items, creating plans
- Trigger: "process Needs_Action", "triage pending items", "check what needs to be done"

**approval-workflow-manager** (HITL Workflow)
- Routes sensitive actions for human approval
- Creates approval requests in `/Pending_Approval/`
- Tracks approval decisions
- Use when: External actions, financial operations, sensitive content
- Trigger: Automatic - invoked by needs-action-triage when approval needed

#### 3. EXECUTION LAYER (Action) - 4 Skills

**mcp-executor** (Core Execution)
- Executes approved actions via MCP servers
- Routes to appropriate MCP server (email, Odoo, social media)
- Handles errors and retries
- Moves completed items to `/Done/`
- Use when: Executing approved actions
- Trigger: Automatic - processes `/Approved/` folder

**odoo-integration** (Accounting/ERP)
- Integrates with Odoo Community for accounting
- Creates invoices, records payments, tracks expenses
- Generates financial reports
- Use when: Accounting operations, financial tasks
- Trigger: "create invoice", "record payment", "generate financial report"

**social-media-poster** (Social Media)
- Posts to Facebook, Instagram, Twitter, LinkedIn
- Adapts content for each platform
- Tracks engagement metrics
- Use when: Social media posting, cross-platform content
- Trigger: "post to facebook", "post to instagram", "share on social media"

**ralph-wiggum-runner** (Autonomous Operation)
- Implements autonomous loop pattern
- Keeps Claude working until task complete
- Uses stop hook to prevent exit
- Monitors `/Done/` folder for completion
- Use when: Autonomous task processing, batch operations
- Trigger: "start ralph loop", "process until complete", "run autonomously"

#### 4. INTELLIGENCE LAYER (Business Intelligence) - 2 Skills

**ceo-briefing-generator** (Weekly Reporting)
- Generates weekly business and accounting audit
- Analyzes completed tasks, financial data, social metrics
- Identifies bottlenecks and opportunities
- Creates Monday morning CEO briefing
- Use when: Weekly reporting, business analysis
- Trigger: "generate ceo briefing", "weekly business audit", "monday morning briefing"

**audit-logger** (Compliance Tracking)
- Logs all external actions with full audit trail
- Records who, what, when, why, result
- Sanitizes credentials automatically
- Generates compliance reports
- Use when: Logging actions, compliance reporting
- Trigger: Automatic - invoked by all execution skills

#### 5. VALIDATION LAYER (Quality Assurance) - 2 Skills

**bronze-demo-check** (Bronze Validation)
- Validates Bronze tier end-to-end workflow
- Checks vault structure, watcher, triage, dashboard
- Use when: Validating Bronze tier, preparing demo
- Trigger: "validate bronze tier", "bronze tier checklist", "demo bronze"

**gold-tier-validator** (Gold Validation)
- Validates complete Gold tier implementation
- Checks all 5 user stories, MCPs, Ralph Loop, CEO briefing
- Generates validation report
- Use when: Validating Gold tier, preparing submission
- Trigger: "validate gold tier", "check gold implementation", "submission readiness"

#### 6. META LAYER (Skill Management) - 1 Skill

**skill-creator** (Skill Development)
- Guides creation of new skills
- Provides best practices and patterns
- Use when: Creating or updating skills
- Trigger: User explicitly asks to create a skill

### Gold Tier Workflow Integration

**Complete Workflow (All Skills Working Together):**

```
1. INPUT (Perception)
   Watchers detect inputs → Create files in /Needs_Action/
   Skills: watcher-runner-filesystem, multi-watcher-runner

2. PROCESSING (Reasoning)
   Ralph Loop processes files → Create plans → Route for approval
   Skills: ralph-wiggum-runner, needs-action-triage,
           approval-workflow-manager, obsidian-vault-ops

3. APPROVAL (Human-in-the-Loop)
   Human reviews in Obsidian → Approve/reject
   Skills: approval-workflow-manager, obsidian-vault-ops

4. EXECUTION (Action)
   Ralph Loop executes → Route to MCP servers → Log results
   Skills: mcp-executor, odoo-integration, social-media-poster,
           audit-logger, obsidian-vault-ops

5. INTELLIGENCE (Business Intelligence)
   Weekly briefing → Analyze data → Generate insights
   Skills: ceo-briefing-generator, odoo-integration,
           social-media-poster, audit-logger, obsidian-vault-ops

6. VALIDATION (Quality Assurance)
   Before submission → Validate implementation
   Skills: bronze-demo-check, gold-tier-validator
```

### Key Principles for Using Skills

1. **Most skills are invoked automatically** - Ralph Loop orchestrates the workflow
2. **Don't manually invoke core skills** - They trigger based on context
3. **obsidian-vault-ops is used by all skills** - It's the file operation layer
4. **audit-logger runs automatically** - All actions are logged
5. **Ralph Loop is the orchestrator** - It keeps everything running autonomously

### Reference Documentation

For complete workflow details, see: `COMPLETE_SKILLS_WORKFLOW_GUIDE.md`

## Recent Changes
- 001-bronze-ai-employee: Added Python 3.13+ + `watchdog`, `python-frontmatter` (plus existing repo deps)
- 003-gold-ai-employee: Added 14 specialized skills for autonomous AI Employee operation

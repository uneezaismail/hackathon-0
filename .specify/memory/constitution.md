<!--
Sync Impact Report

- Version change: 2.0.0 → 3.0.0
- Modified principles:
  - Principle I: "Bronze-First, Silver-Second Scope" → "Bronze-First, Silver-Second, Gold-Third Scope" (expanded)
  - Principle II: "Local-First Vault as Source of Truth" → expanded with Gold folders (/Briefings/, Business_Goals.md)
  - Principle V: "Secure Configuration and Secrets Hygiene" → expanded with OS keyring requirement
  - Principle VI: "Testable, Minimal, Reliable Implementation" → expanded with 24-hour continuous operation test
  - Principle VII: "Human-in-the-Loop (HITL) Approval Workflow" → expanded with financial and social media thresholds
  - Principle IX: "Graceful Degradation and Error Recovery" → expanded with queue files and PM2 requirement
- Added sections:
  - Principle X: Autonomous Operation with Ralph Wiggum Loop
  - Principle XI: Enterprise Accounting Integration (Odoo Community)
  - Principle XII: Multi-Channel Social Media Automation
  - Principle XIII: Proactive Business Intelligence (Weekly CEO Briefing)
  - Principle XIV: Enhanced Resilience and Process Management
  - Technology & Tooling: Added OdooRPC, facebook-sdk, tweepy, keyring, PM2 (required)
  - Artifact Conventions (Gold): Ralph state file, queue files, CEO briefing format
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (no changes needed - constitution check is generic)
  - ✅ .specify/templates/spec-template.md (no changes needed - requirements remain technology-agnostic)
  - ✅ .specify/templates/tasks-template.md (no changes needed - task structure remains valid)
- Deferred TODOs: None
- Rationale: MAJOR version bump (2.0.0 → 3.0.0) because Gold tier adds 5 new non-negotiable principles (autonomous operation, enterprise accounting, social media automation, proactive intelligence, enhanced resilience), introduces Ralph Wiggum Loop paradigm, adds mandatory Odoo integration, and significantly expands technology stack and security requirements. Bronze and Silver tier principles remain valid and unchanged.
-->

# My AI Employee (Hackathon Zero) Constitution

## Core Principles

### I. Bronze-First, Silver-Second, Gold-Third Scope (NON-NEGOTIABLE)
Build Bronze tier first, then extend to Silver tier, then extend to Gold tier.

**Bronze Tier (Foundation)**:
- MUST implement only Bronze deliverables initially: Obsidian vault, one watcher, Claude vault I/O, and skills.
- MUST NOT introduce MCP servers or external actions in Bronze (no email sending, posting, payments).
- SHOULD allow a `Plans/` folder even though only `Inbox/`, `Needs_Action/`, and `Done/` are required.

**Silver Tier (Extension)**:
- MUST implement Human-in-the-Loop (HITL) approval workflow for all external actions.
- MUST add multiple watchers: Gmail (OAuth 2.0), WhatsApp Web (Playwright), LinkedIn, filesystem.
- MUST implement MCP servers for external actions: email (Gmail API + SMTP), LinkedIn, browser automation.
- MUST implement orchestrator.py that watches `/Approved/` folder and executes actions via MCP servers.
- Silver tier is ADDITIVE to Bronze; Bronze tier remains valid and operational.

**Gold Tier (Autonomous Enterprise)**:
- MUST implement autonomous operation via Ralph Wiggum Loop with file movement detection.
- MUST integrate Odoo Community (self-hosted) for enterprise accounting via JSON-RPC APIs.
- MUST implement multi-channel social media automation: Facebook, Instagram, Twitter (X).
- MUST implement weekly CEO briefing generation (Sunday 8:00 PM) with business intelligence.
- MUST implement enhanced resilience: exponential backoff, graceful degradation, PM2 process management.
- Gold tier is ADDITIVE to Silver; Bronze and Silver tiers remain valid and operational.

### II. Local-First Vault as Source of Truth (NON-NEGOTIABLE)
Treat the Obsidian vault as the single source of truth.

**Bronze Tier Structure**:
- MUST store operational state and artifacts in local markdown inside the vault.
- MUST keep the required vault structure:
  - `Inbox/`
  - `Needs_Action/`
  - `Done/`
  - `Dashboard.md`
  - `Company_Handbook.md`
- MUST use the repo vault path convention: `My_AI_Employee/AI_Employee_Vault/`.

**Silver Tier Structure (Additions)**:
- MUST add HITL approval folders:
  - `Pending_Approval/` - Actions awaiting human decision
  - `Approved/` - Actions approved for execution
  - `Rejected/` - Actions rejected by human
  - `Failed/` - Actions that failed execution
  - `Logs/` - Audit logs in JSON format (YYYY-MM-DD.json)
- Approval workflow: `Needs_Action` → `Pending_Approval` → `Approved` → execution → `Done` or `Failed`

**Gold Tier Structure (Additions)**:
- MUST add business intelligence folders:
  - `Briefings/` - Weekly CEO briefings (YYYY-MM-DD_Monday_Briefing.md)
- MUST add root-level business configuration:
  - `Business_Goals.md` - Revenue targets, KPIs, alert thresholds, active projects
- MUST add state files (gitignored):
  - `.ralph_state.json` - Ralph Wiggum Loop state persistence
  - `.odoo_queue.jsonl` - Offline Odoo operation queue
  - `.facebook_queue.jsonl` - Offline Facebook operation queue
  - `.instagram_queue.jsonl` - Offline Instagram operation queue
  - `.twitter_queue.jsonl` - Offline Twitter operation queue

### III. Agent Skills for All AI Behavior (NON-NEGOTIABLE)
Express all AI behavior as Claude Code Agent Skills.

- MUST implement AI workflows via skills under `.claude/skills/`.
- MUST be able to run all automation via Claude Code prompts invoking skills.
- MUST avoid hidden manual steps other than starting watcher processes and MCP servers.

### IV. Vault Safety and Non-Destructive Operations (NON-NEGOTIABLE)
Prevent accidental data loss in a local-first vault.

- MUST NOT delete user-authored vault content.
- MUST preserve YAML frontmatter when moving/processing markdown action items.
- SHOULD prefer append/section updates over full-file rewrites (especially for `Dashboard.md`).
- MUST ask for clarification when the vault root is ambiguous or when an edit risks overwriting user notes.

### V. Secure Configuration and Secrets Hygiene (NON-NEGOTIABLE)
Keep credentials out of git and out of the vault.

**Bronze Tier**:
- MUST NOT commit secrets.
- MUST store credentials/configuration in `.env` (gitignored) or OS secret stores.
- SHOULD redact sensitive values from logs and example files.

**Silver Tier (Additions)**:
- MUST sanitize credentials in audit logs (redact API keys, tokens, passwords, credit card numbers, PII).
- MUST implement dry-run mode (DRY_RUN=true) for development and testing.
- MUST define permission boundaries: which actions auto-approve vs require human approval.
- MUST retain audit logs for minimum 90 days.

**Gold Tier (Additions)**:
- MUST store ALL credentials in OS keyring via credentials.py utility (keyring library).
- MUST NEVER store credentials in .env for production (only for development with DRY_RUN=true).
- Credential types requiring keyring storage:
  - Odoo: ODOO_USERNAME, ODOO_API_KEY (or ODOO_PASSWORD)
  - Facebook: FACEBOOK_PAGE_ACCESS_TOKEN
  - Instagram: INSTAGRAM_ACCOUNT_ID, INSTAGRAM_ACCESS_TOKEN
  - Twitter: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
- MUST sanitize credentials in ALL queue files (.odoo_queue.jsonl, .facebook_queue.jsonl, etc.).
- Financial operations: NO auto-approve threshold (ALL require human approval).
- Social media operations: ALL require human approval, max 10 posts per day per platform.

### VI. Testable, Minimal, Reliable Implementation
Keep changes small, verifiable, and resilient.

**Bronze Tier**:
- MUST prefer minimal diffs and avoid unrelated refactors.
- MUST make the watcher resilient: log errors, continue running, and prevent duplicates (tracked IDs/hashes).
- SHOULD provide deterministic end-to-end validation steps for Bronze.

**Silver Tier (Additions)**:
- MUST test all MCP servers independently (email, LinkedIn, browser automation).
- MUST test approval workflow end-to-end (Needs_Action → Pending_Approval → Approved → execution → Done).
- MUST test error handling and retry logic (exponential backoff, max 3 retries).
- MUST test credential sanitization in audit logs.
- MUST test graceful degradation when components fail.
- All Bronze tier tests must continue passing.

**Gold Tier (Additions)**:
- MUST test all Gold tier MCP servers independently (Odoo, Facebook, Instagram, Twitter).
- MUST test Ralph Wiggum Loop: task file creation → autonomous processing → file movement to /Done/.
- MUST test CEO briefing generation: scheduled trigger → data collection → briefing generation → file creation.
- MUST test financial approval workflow: invoice creation → approval → Odoo execution → audit log.
- MUST test social media approval workflow: post draft → approval → platform posting → audit log.
- MUST test 24-hour continuous operation: all watchers running, no crashes, no memory leaks.
- MUST test queue resilience: service down → queue locally → service restored → process queue.
- All Bronze and Silver tier tests must continue passing.

### VII. Human-in-the-Loop (HITL) Approval Workflow (NON-NEGOTIABLE - Silver Tier)
All external actions require human approval before execution.

- MUST route external/sensitive actions to `/Pending_Approval/` folder.
- MUST wait for human to move file to `/Approved/` before execution.
- MUST support rejection by moving to `/Rejected/` folder.
- Approval request format MUST include:
  - YAML frontmatter: type, action_type, requires_approval, status, priority, created_at
  - Body: requested action, why approval needed, rules applied from Company_Handbook.md, recommendation
- Orchestrator.py MUST watch `/Approved/` folder and execute via MCP servers.
- MUST move executed items to `/Done/` (success) or `/Failed/` (error) with execution results.
- Permission boundaries define auto-approve thresholds (e.g., emails to known contacts, payments < $50 recurring).

**Gold Tier (Additions)**:
- Financial operations: ALL require approval (NO auto-approve threshold, even for recurring payments).
- Social media operations: ALL require approval before posting (max 10 posts per day per platform).
- Approval request MUST include platform-specific preview for social media (character count, hashtags, mentions).
- Approval request MUST include financial impact summary for Odoo operations (amount, account, tax implications).

### VIII. Comprehensive Audit Logging (NON-NEGOTIABLE - Silver Tier)
Log all external actions with who/what/when/why/result.

- MUST log ALL external actions to `/Logs/YYYY-MM-DD.json` in JSONL format (one JSON object per line).
- Log entry MUST include: timestamp (ISO8601), action_type, actor, target, approval_status, approved_by, result.
- MUST sanitize credentials: API keys, tokens, passwords, credit card numbers (show last 4 digits only), PII.
- MUST retain audit logs for minimum 90 days.
- Logs are write-only and immutable during retention period.
- MUST support audit trail queries: by action type, by status, by actor, by date range.

**Gold Tier (Additions)**:
- MUST log ALL Odoo operations: invoice creation, payment recording, expense categorization, report generation.
- MUST log ALL social media operations: post creation, post publishing, engagement metrics.
- MUST log Ralph Wiggum Loop iterations: task start, iterations, completion signal, total time.
- MUST log CEO briefing generation: trigger time, data sources, generation time, file path.
- Audit log retention: 90 days minimum, then archive for 2 years for compliance (financial regulations).

### IX. Graceful Degradation and Error Recovery (NON-NEGOTIABLE - Silver Tier)
System continues operating when components fail.

- MUST implement retry logic with exponential backoff (max 3 retries: 1s → 5s → 10s → 30s).
- MUST implement graceful degradation:
  - Gmail API down: queue emails locally, process when restored
  - Banking API timeout: NEVER auto-retry payments, require fresh approval
  - Claude Code unavailable: watchers continue collecting, queue grows for later processing
  - Obsidian vault locked: write to temporary folder, sync when available
- MUST implement watchdog process to monitor and restart critical processes (or use PM2).
- MUST implement dead-letter queue for failed actions after max retries.
- MUST notify human on critical errors (authentication failures, system crashes).

**Gold Tier (Additions)**:
- MUST implement exponential backoff with 4 retries: 1s → 2s → 4s → 8s (configurable via RetryConfig).
- MUST implement queue files for ALL external services:
  - `.odoo_queue.jsonl` - Odoo operations when service unavailable
  - `.facebook_queue.jsonl` - Facebook posts when API unavailable
  - `.instagram_queue.jsonl` - Instagram posts when API unavailable
  - `.twitter_queue.jsonl` - Twitter posts when API unavailable
- MUST use PM2 for process management (required, not optional):
  - All watchers MUST run under PM2
  - Orchestrator.py MUST run under PM2
  - PM2 MUST be configured for auto-restart on crash
  - PM2 MUST be configured for startup persistence (pm2 startup, pm2 save)
- MUST implement health checks for all MCP servers (health_check tool).
- MUST alert human when queue size exceeds threshold (e.g., 50 items).

### X. Autonomous Operation with Ralph Wiggum Loop (NON-NEGOTIABLE - Gold Tier)
Enable multi-step task completion without human intervention.

- MUST implement Ralph Wiggum Loop pattern using stop hook.
- Stop hook MUST intercept Claude's exit and re-inject prompt until task complete.
- Completion signal: task file moves from `/Needs_Action/` to `/Done/` (file movement detection).
- MUST support configurable max iterations via RALPH_MAX_ITERATIONS environment variable (default: 10).
- MUST persist loop state in `.ralph_state.json` (gitignored) for crash recovery.
- MUST log each iteration: task ID, iteration number, actions taken, completion status.
- MUST respect HITL approval thresholds: autonomous operation pauses when approval required.
- Ralph Wiggum Loop MUST NOT bypass approval workflow (financial and social media operations still require approval).

### XI. Enterprise Accounting Integration (NON-NEGOTIABLE - Gold Tier)
Integrate with Odoo Community for all accounting operations.

- MUST use Odoo Community (self-hosted, local) as single source of truth for accounting.
- MUST use Odoo JSON-RPC APIs (Odoo 19+) via OdooRPC library.
- MUST implement odoo_mcp.py with required tools:
  - create_invoice: Create customer invoices with line items, taxes, payment terms
  - send_invoice: Send invoice via email to customer
  - record_payment: Record payment received against invoice
  - create_expense: Categorize and record business expenses
  - generate_report: Generate financial reports (revenue, expenses, profit/loss)
  - health_check: Verify Odoo connection and authentication
- Financial data MUST NEVER leave local network (no cloud accounting services).
- ALL financial operations REQUIRE human approval (no auto-approve threshold).
- MUST implement graceful degradation: queue operations in `.odoo_queue.jsonl` when Odoo unavailable.
- MUST reconcile Odoo data with vault task completion in weekly CEO briefing.

### XII. Multi-Channel Social Media Automation (NON-NEGOTIABLE - Gold Tier)
Automate social media posting across Facebook, Instagram, and Twitter.

- MUST implement dedicated MCP servers for each platform:
  - facebook_mcp.py: Post to Facebook page, retrieve engagement metrics
  - instagram_mcp.py: Post to Instagram account, retrieve engagement metrics
  - twitter_mcp.py: Post tweets, retrieve engagement metrics
- ALL social media posts REQUIRE human approval before publishing (no exceptions).
- MUST adapt content per platform:
  - Twitter: 280 character limit, hashtag optimization, @mentions
  - Facebook: longer form, link previews, audience targeting
  - Instagram: image-first, hashtag strategy (max 30), caption optimization
- MUST implement rate limiting: max 10 posts per day per platform.
- MUST track engagement metrics: likes, shares, comments, reach, impressions.
- MUST include engagement summary in weekly CEO briefing.
- MUST implement graceful degradation: queue posts in platform-specific queue files when API unavailable.

### XIII. Proactive Business Intelligence (NON-NEGOTIABLE - Gold Tier)
Generate weekly CEO briefing with business insights and recommendations.

- MUST generate CEO briefing every Sunday at 8:00 PM (configurable via cron or Task Scheduler).
- Briefing MUST be stored in `/Briefings/YYYY-MM-DD_Monday_Briefing.md`.
- Briefing MUST include:
  - Executive Summary: 2-3 sentence overview of week's performance
  - Revenue: This week, month-to-date, trend vs target (from Odoo)
  - Completed Tasks: Summary of items moved to /Done/ this week
  - Bottlenecks: Tasks that took longer than expected, delays, blockers
  - Proactive Suggestions: Cost optimization (unused subscriptions), upcoming deadlines, process improvements
  - Social Media Performance: Engagement metrics, top-performing posts, audience growth
- MUST use Business_Goals.md to define KPIs and alert thresholds.
- MUST identify unused subscriptions: no activity in 30 days, cost increased >20%, duplicate functionality.
- MUST flag upcoming deadlines: project milestones, tax prep, contract renewals.
- Briefing generation MUST be autonomous (no human intervention required).

### XIV. Enhanced Resilience and Process Management (NON-NEGOTIABLE - Gold Tier)
Ensure 24/7 operation with automatic recovery from failures.

- MUST use PM2 for process management (required, not optional).
- MUST configure PM2 for:
  - Auto-restart on crash (max 10 restarts per minute)
  - Startup persistence (pm2 startup, pm2 save)
  - Log rotation (max 10MB per log file)
  - Memory monitoring (restart if memory exceeds threshold)
- MUST implement exponential backoff retry logic: 1s → 2s → 4s → 8s (configurable via RetryConfig).
- MUST implement health checks for all critical components:
  - Watchers: last successful check timestamp
  - MCP servers: health_check tool response
  - Odoo connection: authentication and database access
  - Social media APIs: authentication and rate limit status
- MUST implement watchdog monitoring (or rely on PM2):
  - Check process health every 60 seconds
  - Restart crashed processes automatically
  - Alert human on repeated failures (>3 crashes in 10 minutes)
- MUST implement queue-based resilience:
  - All external operations queue locally when service unavailable
  - Process queues automatically when service restored
  - Alert human when queue size exceeds threshold (50 items)
- MUST pass 24-hour continuous operation test: all watchers running, no crashes, no memory leaks.

## Project Guardrails

### Technology & Tooling

**Bronze Tier**:
- Python: 3.13+ (or latest available)
- Package manager: uv
- Tests: pytest
- Obsidian: vault of markdown files
- Claude Code: used as the terminal-based reasoning and write-back engine

**Silver Tier (Additions)**:
- FastMCP: library for MCP servers with Pydantic v2 validation
- Playwright: browser automation for WhatsApp Web and payment forms
- PM2: process management (recommended) OR custom watchdog.py for health monitoring
- Multiple watchers: Gmail (OAuth 2.0), WhatsApp Web, LinkedIn, filesystem

**Gold Tier (Additions - REQUIRED)**:
- OdooRPC: Odoo JSON-RPC client for accounting integration
- facebook-sdk: Facebook Graph API for page posting
- tweepy: Twitter API v2 for tweet posting
- keyring: OS credential manager for secure storage (Linux/macOS/Windows)
- PM2: process management (REQUIRED, not optional) for always-on operation

### Constraints

**Bronze Tier**:
- Bronze tier only: no MCP servers and no external actions.
- Path convention: `My_AI_Employee/AI_Employee_Vault/` is the default vault root.

**Silver Tier (Additions)**:
- All external actions MUST go through HITL approval workflow (no exceptions without explicit ADR).
- Orchestrator.py location: `My_AI_Employee/orchestrator.py`
- Watchers location: `My_AI_Employee/watchers/`
- MCP servers location: `My_AI_Employee/mcp_servers/` or `.claude/skills/mcp-executor/scripts/`
- Security and audit logging requirements are NON-NEGOTIABLE.

**Gold Tier (Additions)**:
- ALL financial operations REQUIRE human approval (no auto-approve threshold).
- ALL social media posts REQUIRE human approval (no exceptions).
- Odoo MUST be self-hosted and local (no cloud Odoo instances).
- PM2 MUST be used for process management (required for Gold tier).
- Ralph Wiggum Loop MUST respect HITL approval workflow (cannot bypass approvals).
- Credentials MUST be stored in OS keyring (not .env) for production.

## Workflow & Quality Gates

**Bronze Tier**:
- MUST keep the workflow demonstrable end-to-end:
  - drop file → `Needs_Action` item → Claude processes → plan + dashboard update → item moved to `Done/`
- MUST add tests for watcher core logic and action-item formatting.
- SHOULD keep formatting consistent; avoid heavy tooling unless already present in the repo.

**Silver Tier (Additions)**:
- MUST demonstrate Silver tier end-to-end workflow:
  - Watcher detects external action → creates item in `Needs_Action/`
  - Triage skill determines approval needed → creates request in `Pending_Approval/`
  - Human approves → moves to `Approved/`
  - Orchestrator.py executes via MCP server → moves to `Done/` with result
  - Audit log entry created in `/Logs/YYYY-MM-DD.json`
- All Bronze tier workflows must continue functioning.

**Gold Tier (Additions)**:
- MUST demonstrate Gold tier end-to-end workflows:
  - **Financial workflow**: Invoice request → approval → Odoo execution → audit log → CEO briefing
  - **Social media workflow**: Post draft → approval → platform posting → engagement tracking → CEO briefing
  - **Autonomous workflow**: Task file → Ralph Wiggum Loop → multi-step processing → file movement to /Done/
  - **CEO briefing workflow**: Sunday 8PM trigger → data collection (Odoo + vault) → briefing generation → file creation
- MUST pass 24-hour continuous operation test: all watchers running, no crashes, no memory leaks.
- MUST pass queue resilience test: service down → queue locally → service restored → process queue.
- All Bronze and Silver tier workflows must continue functioning.

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

### Artifact Conventions (Silver)

#### Approval Request Contract (Pending_Approval)

- Approval requests MUST be Markdown files stored under `Pending_Approval/`.
- YAML frontmatter MUST include:
  - `type`: `approval_request`
  - `action_type`: `send_email|send_message|create_post|payment|system_change`
  - `requires_approval`: `true`
  - `status`: `pending|approved|rejected`
  - `priority`: `high|medium|low`
  - `created_at`: ISO timestamp
  - `approved_by`: null (filled by human)
  - `approved_at`: null (filled by human)
- Body MUST include: requested action, why approval needed, rules applied from Company_Handbook.md, recommendation.

#### Audit Log Entry Contract (Logs/)

- Audit logs MUST be stored as `/Logs/YYYY-MM-DD.json` in JSONL format (one JSON object per line).
- Each entry MUST include: timestamp, action_type, actor, target, approval_status, approved_by, result.
- MUST sanitize: API keys (show first 4 chars + ***), tokens (redact entirely), passwords (redact entirely), credit card numbers (show last 4 digits only), PII (truncate emails as user@*****.com).
- Retention: 90 days minimum, then archive for 2 years for compliance.

#### Orchestrator.py Contract

- MUST watch `/Approved/` folder with configurable check interval (default 5 seconds).
- MUST route actions to appropriate MCP server based on action_type field.
- MUST implement retry logic (max 3 attempts with exponential backoff: 2s, 5s, 10s).
- MUST move successful executions to `/Done/` with results in frontmatter.
- MUST move failed executions to `/Failed/` with error details in frontmatter.
- MUST log all executions to audit trail via audit-logger skill.

### Artifact Conventions (Gold)

#### Ralph State File Contract (.ralph_state.json)

- Ralph Wiggum Loop state MUST be stored in `.ralph_state.json` (gitignored).
- State file MUST include:
  - `task_id`: Unique identifier for current task
  - `task_file`: Path to task file being processed
  - `iteration`: Current iteration number
  - `max_iterations`: Maximum iterations allowed
  - `started_at`: ISO timestamp when loop started
  - `last_iteration_at`: ISO timestamp of last iteration
  - `completion_signal`: File movement detection status
- State file MUST be updated after each iteration.
- State file MUST be cleared when task completes (file moves to /Done/).

#### Queue File Contract (*.jsonl)

- Queue files MUST be stored in vault root: `.odoo_queue.jsonl`, `.facebook_queue.jsonl`, `.instagram_queue.jsonl`, `.twitter_queue.jsonl`.
- Queue files MUST use JSONL format (one JSON object per line).
- Each queue entry MUST include:
  - `operation_type`: Type of operation (e.g., create_invoice, post_tweet)
  - `parameters`: Operation parameters (sanitized)
  - `queued_at`: ISO timestamp when queued
  - `retry_count`: Number of retry attempts (default: 0)
  - `max_retries`: Maximum retry attempts (default: 3)
- Queue files MUST be processed when service becomes available.
- Queue entries MUST be removed after successful execution.
- Failed entries (max retries exceeded) MUST be moved to dead-letter queue or logged.

#### CEO Briefing Contract (Briefings/)

- CEO briefings MUST be stored as `/Briefings/YYYY-MM-DD_Monday_Briefing.md`.
- YAML frontmatter MUST include:
  - `generated`: ISO timestamp when briefing generated
  - `period`: Date range covered (YYYY-MM-DD to YYYY-MM-DD)
  - `data_sources`: List of data sources (Odoo, vault, social media APIs)
- Body MUST include sections:
  - Executive Summary (2-3 sentences)
  - Revenue (this week, MTD, trend vs target)
  - Completed Tasks (summary from /Done/)
  - Bottlenecks (delayed tasks, blockers)
  - Proactive Suggestions (cost optimization, deadlines, improvements)
  - Social Media Performance (engagement metrics, top posts)
- Briefing MUST be generated automatically every Sunday at 8:00 PM.

#### Business Goals Contract (Business_Goals.md)

- Business_Goals.md MUST be stored in vault root.
- YAML frontmatter MUST include:
  - `last_updated`: ISO timestamp of last update
  - `review_frequency`: How often to review (e.g., weekly, monthly)
- Body MUST include sections:
  - Q1/Q2/Q3/Q4 Objectives (revenue targets, key metrics)
  - Active Projects (name, due date, budget)
  - Subscription Audit Rules (thresholds for flagging unused services)
- Business_Goals.md MUST be referenced by CEO briefing generation.

## Governance

- This constitution supersedes feature specs, plans, and tasks when there is conflict.
- Amendments MUST update the version and record the rationale.
- Significant architecture choices with multiple viable options and long-term impact SHOULD be documented with an ADR.
  - Example: whether the watcher copies dropped files into the vault vs storing metadata-only links.
- Silver tier principles are ADDITIVE to Bronze tier; Bronze tier remains valid and operational.
- Gold tier principles are ADDITIVE to Silver tier; Bronze and Silver tiers remain valid and operational.
- All external actions MUST go through HITL approval workflow (no exceptions without explicit ADR).
- Security and audit logging requirements are NON-NEGOTIABLE.
- Financial operations: ALL require approval (no auto-approve threshold).
- Social media operations: ALL require approval (no exceptions).

**Version**: 3.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-28

# Feature Specification: Gold Tier AI Employee

**Feature Branch**: `003-gold-ai-employee`
**Created**: 2026-01-27
**Status**: Draft
**Input**: User description: "Implement Gold Tier AI Employee with full autonomous operation. Build on Bronze and Silver tiers to add: (1) Odoo Community (self-hosted, local) integration via JSON-RPC APIs (Odoo 19+) for accounting, invoicing, payment tracking, expense categorization, and financial reporting, (2) Facebook, Instagram, and Twitter/X MCP servers for social media posting with platform-specific content adaptation and engagement metrics tracking, (3) Ralph Wiggum Loop for autonomous multi-step task completion using stop hooks with file movement detection (task file moves to /Done/ as completion signal), (4) Weekly Business and Accounting Audit with CEO Briefing generation scheduled for Sunday 8:00 PM analyzing completed tasks from /Done/ folder, Odoo financial data (revenue, expenses, invoices, aged receivables), social media metrics (reach, engagement, top posts), and Business_Goals.md to generate comprehensive Monday morning briefing with executive summary, revenue analysis, bottleneck identification, proactive suggestions (unused subscriptions, revenue opportunities), and upcoming deadlines, (5) Comprehensive error recovery with retry logic using exponential backoff for transient errors (network timeout, API rate limit), watchdog process monitoring critical components (orchestrator, watchers, MCP servers) with auto-restart on crash, and graceful degradation (queue operations when services unavailable), (6) Enhanced audit logging for all external actions to /Logs/YYYY-MM-DD.json with credential sanitization (redact API keys, tokens, passwords, PII) and 90-day retention. All AI functionality must be implemented as Agent Skills in .claude/skills/: create ralph-wiggum-runner, social-media-poster, odoo-integration, ceo-briefing-generator, gold-tier-validator skills, and update mcp-executor (add Odoo/social MCP routing), needs-action-triage (handle Odoo/social action types), approval-workflow-manager (financial approval thresholds). Implement MCP servers in My_AI_Employee/mcp_servers/: odoo_mcp.py (JSON-RPC client with create_invoice, send_invoice, record_payment, create_expense, generate_report operations), facebook_mcp.py (Graph API with create_post, upload_photo, get_post_insights), instagram_mcp.py (Graph API with create_media_post, create_story, get_media_insights), twitter_mcp.py (API v2 with create_tweet, create_thread, get_tweet_metrics). Install stop hook at .claude/hooks/stop/ralph_wiggum_check.py for Ralph loop. Schedule CEO briefing via cron (0 20 * * 0). Gold tier is ADDITIVE to Silver tier; Bronze and Silver remain operational. Use Odoo Community (self-hosted, local) NOT Xero. Ralph loop uses file movement detection (advanced) NOT promise-based. All financial actions require HITL approval. Implement dry-run mode (DRY_RUN=true) for testing. Max iterations limit (default: 10) prevents infinite loops. Watchdog checks every 60 seconds. End-to-end test: file drop → watcher → triage → Odoo invoice → approval → send → CEO briefing."

## Scope, Constraints, Non-Goals

### In Scope

- **Accounting Integration**: Self-hosted local accounting system for invoicing, payment tracking, expense categorization, and financial reporting
- **Social Media Management**: Multi-platform posting with content adaptation and engagement tracking for Facebook, Instagram, and Twitter
- **Autonomous Operation**: Multi-step task completion without manual intervention using completion detection
- **Business Intelligence**: Weekly automated business audit with comprehensive briefing covering revenue, tasks, expenses, social media, and proactive suggestions
- **Reliability**: Error recovery with automatic retries, component health monitoring with auto-restart, and graceful degradation
- **Compliance**: Comprehensive audit logging with credential sanitization and retention policies

### Out of Scope (Gold Tier)

- Cloud deployment and always-on infrastructure (Platinum tier)
- Multi-agent orchestration with work delegation (Platinum tier)
- Real-time vault synchronization between agents (Platinum tier)
- Production-grade monitoring dashboards and alerting systems (Platinum tier)

### Constraints

- Gold tier is ADDITIVE to Silver tier; all Bronze and Silver functionality must remain operational
- Accounting system must be self-hosted and local (no cloud dependencies)
- All financial operations require human approval before execution
- Autonomous operation must have safety limits (max iterations, timeouts)
- All external actions must be logged with credentials sanitized

### Assumptions

- User has local infrastructure capable of running self-hosted accounting system
- User has social media accounts with API access configured
- User's business operates during standard business hours (for briefing timing)
- Weekly briefing schedule (Sunday 8:00 PM) aligns with user's Monday morning review needs
- 90-day audit log retention meets user's compliance requirements

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage business accounting locally (Priority: P1)

As a business owner, I want to create invoices, record payments, categorize expenses, and generate financial reports through a self-hosted accounting system, so I can manage my business finances locally without cloud dependencies or subscription fees.

**Why this priority**: Core Gold tier requirement. Financial operations are foundational for business management and enable all other business intelligence features.

**Independent Test**: Can be tested by installing the accounting system locally, creating an invoice through the AI employee, and verifying the invoice appears in the accounting system and can be sent to a customer.

**Acceptance Scenarios**:

1. **Given** the accounting system is running locally, **When** I tell the AI employee "create invoice for Client A: $1,500 for consulting", **Then** a draft invoice is created in the accounting system, an approval request appears for review, and after approval the invoice is sent to the client via email.
2. **Given** I receive a payment notification, **When** the AI employee processes it, **Then** the payment is recorded in the accounting system, matched to the correct invoice, and the invoice status updates to paid.
3. **Given** I have an expense receipt, **When** the AI employee categorizes it, **Then** an expense record is created with the correct category and the receipt is attached for audit purposes.
4. **Given** it's month-end, **When** I request financial reports, **Then** the AI employee generates profit & loss, balance sheet, and cash flow reports from the accounting data.

---

### User Story 2 - Maintain social media presence efficiently (Priority: P2)

As a business owner, I want to post content to Facebook, Instagram, and Twitter with platform-appropriate formatting and track engagement metrics, so I can maintain my social media presence without manually adapting content for each platform.

**Why this priority**: Enables marketing automation and provides data for business intelligence. Depends on approval workflow from Silver tier.

**Independent Test**: Can be tested by configuring social media accounts, asking the AI employee to post content, and verifying posts appear on each platform with appropriate formatting.

**Acceptance Scenarios**:

1. **Given** social media accounts are configured, **When** I tell the AI employee "post to all platforms: Big announcement tomorrow!", **Then** platform-specific content is created (respecting character limits and format requirements), approval requests appear, and after approval posts are published to all three platforms.
2. **Given** posts have been published this week, **When** the weekly briefing is generated, **Then** social media metrics (reach, engagement, top-performing posts) are included in the briefing.
3. **Given** I want to schedule a post, **When** I specify a future date and time, **Then** the post is scheduled in each platform's scheduler and I receive confirmation.

---

### User Story 3 - Work autonomously on multi-step tasks (Priority: P3)

As a business owner, I want the AI employee to work autonomously on complex multi-step tasks until completion, so I can "set it and forget it" without manually re-prompting for each step.

**Why this priority**: Enables true autonomous operation. Without this, the AI employee requires manual intervention between steps, limiting its value.

**Independent Test**: Can be tested by starting an autonomous task with multiple action items, observing the AI employee continue working through iterations, and verifying completion when all items are processed.

**Acceptance Scenarios**:

1. **Given** multiple action items exist awaiting processing, **When** I start an autonomous task to "process all pending items", **Then** the AI employee processes each item, creates plans, handles approvals, and continues until all items are complete.
2. **Given** an autonomous task is running, **When** the AI employee completes a step and attempts to exit, **Then** the system checks if the task is complete, and if not, automatically continues to the next step.
3. **Given** an autonomous task reaches the safety limit, **When** the maximum iterations are hit, **Then** the task exits gracefully, saves its state, and notifies me of the incomplete work.

---

### User Story 4 - Receive weekly business intelligence (Priority: P4)

As a business owner, I want an automated weekly business audit that generates a comprehensive briefing every Sunday night, so I start Monday morning with clear visibility into revenue, completed work, bottlenecks, expenses, social media performance, and opportunities.

**Why this priority**: High-value feature demonstrating full system integration. Depends on accounting, social media, and task completion data being available.

**Independent Test**: Can be tested by manually triggering briefing generation, verifying it collects data from all sources (accounting, social media, completed tasks, business goals), and produces a comprehensive report.

**Acceptance Scenarios**:

1. **Given** it's Sunday 8:00 PM, **When** the scheduled task triggers, **Then** the AI employee collects data from all sources, generates the briefing, and saves it for Monday morning review.
2. **Given** the briefing is generated, **When** I open it, **Then** it includes executive summary, revenue vs target, completed tasks, identified bottlenecks, expense analysis, proactive suggestions, social media performance, and upcoming deadlines.
3. **Given** a subscription hasn't been used in 30+ days, **When** the briefing is generated, **Then** it includes a proactive suggestion to cancel the subscription with estimated cost savings.

---

### User Story 5 - Operate reliably with automatic recovery (Priority: P5)

As a business owner, I want the system to handle errors gracefully with automatic retries and component monitoring, so temporary failures don't break my workflow or require manual intervention.

**Why this priority**: Production-readiness feature. Critical for reliability but depends on core functionality being implemented first.

**Independent Test**: Can be tested by simulating various error conditions (network timeout, service unavailable, component crash) and verifying the system recovers appropriately.

**Acceptance Scenarios**:

1. **Given** a network timeout occurs during an operation, **When** the error is detected, **Then** the system automatically retries with increasing delays between attempts (1s, 2s, 4s, 8s) up to a maximum number of attempts.
2. **Given** a critical component crashes, **When** the monitoring system detects it's not running, **Then** the component is automatically restarted and I receive a notification.
3. **Given** the accounting system is temporarily unavailable, **When** financial operations are requested, **Then** they are queued locally and processed automatically when the system becomes available.

---

### Edge Cases

- **What happens when the accounting system database is corrupted or inaccessible?**
  - System queues operations locally, alerts user, continues with non-accounting operations

- **How does the system handle social media API rate limits?**
  - Implements automatic retry with increasing delays, respects rate limit headers, queues posts for later

- **What if autonomous operation gets stuck in an infinite loop?**
  - Maximum iterations limit (default: 10) forces exit, state is saved for manual review

- **How to handle conflicting approval requests (e.g., two invoices for the same client)?**
  - Each approval is independent, processed in order, with clear timestamps and context

- **What if briefing generation fails mid-process?**
  - Autonomous operation retries, partial data is saved, error is logged, user is notified

- **How does the system handle multiple simultaneous autonomous tasks?**
  - Each task runs independently with its own state file, completion detection prevents conflicts

- **What if a component repeatedly crashes (crash loop)?**
  - After 3 restart attempts within 5 minutes, monitoring pauses restarts and alerts user

## Requirements *(mandatory)*

### Functional Requirements

**Accounting Integration:**
- **FR-001**: System MUST integrate with self-hosted local accounting system for invoice management
- **FR-002**: System MUST support creating draft invoices with customer details, line items, amounts, and due dates
- **FR-003**: System MUST support sending invoices to customers and tracking invoice status (draft, sent, paid, overdue)
- **FR-004**: System MUST support recording payments and matching them to invoices
- **FR-005**: System MUST support categorizing expenses and attaching receipt documentation
- **FR-006**: System MUST generate financial reports showing revenue, expenses, and cash flow

**Social Media Integration:**
- **FR-007**: System MUST integrate with Facebook for posting and retrieving engagement metrics
- **FR-008**: System MUST integrate with Instagram for media posting and retrieving engagement metrics
- **FR-009**: System MUST integrate with Twitter for posting and retrieving engagement metrics
- **FR-010**: System MUST adapt content for each platform's character limits and format requirements
- **FR-011**: System MUST retrieve engagement metrics (reach, likes, comments, shares) from each platform

**Autonomous Operation:**
- **FR-012**: System MUST support autonomous multi-step task completion without manual intervention
- **FR-013**: System MUST detect task completion by monitoring task file location
- **FR-014**: System MUST enforce maximum iterations limit (configurable, default: 10) to prevent infinite loops
- **FR-015**: System MUST save task state after each iteration for crash recovery
- **FR-016**: System MUST support graceful shutdown when interrupted

**Business Intelligence:**
- **FR-017**: System MUST generate weekly business briefing every Sunday at 8:00 PM
- **FR-018**: System MUST collect data from completed tasks (last 7 days), accounting system (revenue/expenses), social media (metrics), and business goals
- **FR-019**: System MUST identify bottlenecks by detecting tasks taking significantly longer than expected
- **FR-020**: System MUST generate proactive suggestions (unused subscriptions, revenue opportunities, cost optimizations)
- **FR-021**: System MUST save briefing for Monday morning review

**Error Recovery:**
- **FR-022**: System MUST implement automatic retry with exponential backoff for transient errors (network timeout, API rate limit)
- **FR-023**: System MUST monitor critical components and automatically restart them on crash
- **FR-024**: System MUST implement graceful degradation by queuing operations when services are unavailable
- **FR-025**: System MUST alert user for authentication errors and pause operations
- **FR-026**: System MUST quarantine corrupted data and alert user

**Audit & Compliance:**
- **FR-027**: System MUST log all external actions with timestamp, action type, actor, target, parameters, approval status, and result
- **FR-028**: System MUST sanitize credentials before logging (redact API keys, tokens, passwords, personally identifiable information)
- **FR-029**: System MUST retain audit logs for minimum 90 days
- **FR-030**: System MUST support dry-run mode for testing without executing real actions

**Integration & Compatibility:**
- **FR-031**: Gold tier MUST maintain all Bronze tier functionality (filesystem watcher, vault operations, basic triage)
- **FR-032**: Gold tier MUST maintain all Silver tier functionality (multi-channel monitoring, approval workflow, MCP execution)
- **FR-033**: All financial operations MUST require human approval before execution
- **FR-034**: System MUST support end-to-end workflow: file drop → detection → triage → accounting operation → approval → execution → briefing

### Key Entities

- **Invoice**: Accounting record with customer information, line items, total amount, due date, and status (draft/sent/paid/overdue)
- **Payment**: Financial transaction record with amount, payment method, date, and reconciliation status linking to invoice
- **Expense**: Business expense record with amount, category, vendor, description, and attached receipt documentation
- **Social Media Post**: Content record with platform identifier, post text, media attachments, scheduled time, post identifier, and engagement metrics
- **Business Briefing**: Weekly report with executive summary, revenue analysis, completed tasks, bottlenecks, expense analysis, proactive suggestions, social media performance, and upcoming deadlines
- **Autonomous Task**: Task execution record with description, iteration count, maximum iterations, start time, completion criteria, and current state
- **Audit Log Entry**: Compliance record with timestamp, action type, actor, target, parameters, approval status, execution result, and sanitized credentials

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can create and send invoices through the accounting system with less than 5 minutes of setup time
- **SC-002**: User can post to all 3 social media platforms (Facebook, Instagram, Twitter) with a single command
- **SC-003**: Autonomous operation processes multi-step tasks without manual intervention between steps
- **SC-004**: Business briefing is generated automatically every Sunday night and includes data from all sources (accounting, social media, tasks, goals)
- **SC-005**: System recovers from transient errors (network timeout, API rate limit) without user intervention
- **SC-006**: All external actions are logged to audit trail with credentials properly sanitized
- **SC-007**: Component monitoring detects and restarts crashed components within 60 seconds
- **SC-008**: System validation passes with greater than 95% of checks successful
- **SC-009**: End-to-end workflow (file drop → detection → triage → invoice → approval → send → briefing) completes successfully
- **SC-010**: System handles 50+ action items per week without performance degradation or manual intervention

### Acceptance Criteria

- All Bronze tier functionality remains operational (filesystem watcher, vault operations, basic triage)
- All Silver tier functionality remains operational (multi-channel monitoring, approval workflow, MCP execution)
- Self-hosted local accounting system installed and accessible
- Facebook, Instagram, Twitter integrations functional with posting and metrics retrieval
- Autonomous operation completes multi-step tasks without manual intervention
- Weekly briefing generated automatically every Sunday at 8:00 PM
- Component monitoring detects crashes and restarts within 60 seconds
- Automatic retry with exponential backoff implemented for all external operations
- Audit logging captures all external actions with credential sanitization
- Dry-run mode works for all external actions without executing real operations
- End-to-end test passes: file drop → invoice creation → approval → send → briefing
- System validation reports greater than 95% checks passed
- Documentation includes setup instructions, architecture overview, and lessons learned

## Assumptions

- **Infrastructure**: User has local infrastructure (computer/server) capable of running self-hosted accounting system continuously
- **API Access**: User has configured social media accounts with appropriate API access and permissions
- **Business Hours**: User's business operates during standard business hours, making Sunday 8:00 PM appropriate for briefing generation
- **Review Schedule**: Monday morning briefing review aligns with user's weekly planning routine
- **Compliance**: 90-day audit log retention meets user's compliance and regulatory requirements
- **Network**: User has reliable internet connection for social media and email operations
- **Approval Availability**: User reviews and processes approval requests within 24 hours during business days
- **Data Volume**: User's business generates fewer than 100 action items per week (within system capacity)

## Notes

- Gold tier is ADDITIVE to Silver tier; all Bronze and Silver functionality remains operational
- Accounting system must be self-hosted and local (not cloud-based) per requirements
- Autonomous operation uses file movement detection (advanced) not promise-based completion (simple)
- All financial operations require human approval through the existing HITL workflow
- Dry-run mode (DRY_RUN=true) enables testing without executing real external actions
- Maximum iterations limit (default: 10) prevents infinite loops in autonomous operation
- Component monitoring checks every 60 seconds for health status
- Weekly briefing scheduled for Sunday 8:00 PM to be ready for Monday morning review

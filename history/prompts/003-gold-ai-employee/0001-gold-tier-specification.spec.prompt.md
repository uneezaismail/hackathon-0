---
id: 00)1
title: Gold Tier Specification
stage: spec
date: 2026-01-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-gold-ai-employee
branch: 003-gold-ai-employee
user: cyb3r
command: /sp.specify
labels: ["gold-tier", "specification", "ai-employee", "odoo", "social-media", "autonomous-operation", "ceo-briefing", "ralph-wiggum-loop"]
links:
  spec: specs/003-gold-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-gold-ai-employee/spec.md
  - specs/003-gold-ai-employee/checklists/requirements.md
tests:
  - Specification validation checklist (all items passed)
  - Requirements completeness check (passed)
  - Technology-agnostic validation (passed)
---

## Prompt

Implement Gold Tier AI Employee with full autonomous operation. Build on Bronze and Silver tiers to add: (1) Odoo Community (self-hosted, local) integration via JSON-RPC APIs (Odoo 19+) for accounting, invoicing, payment tracking, expense categorization, and financial reporting, (2) Facebook, Instagram, and Twitter/X MCP servers for social media posting with platform-specific content adaptation and engagement metrics tracking, (3) Ralph Wiggum Loop for autonomous multi-step task completion using stop hooks with file movement detection (task file moves to /Done/ as completion signal), (4) Weekly Business and Accounting Audit with CEO Briefing generation scheduled for Sunday 8:00 PM analyzing completed tasks from /Done/ folder, Odoo financial data (revenue, expenses, invoices, aged receivables), social media metrics (reach, engagement, top posts), and Business_Goals.md to generate comprehensive Monday morning briefing with executive summary, revenue analysis, bottleneck identification, proactive suggestions (unused subscriptions, revenue opportunities), and upcoming deadlines, (5) Comprehensive error recovery with retry logic using exponential backoff for transient errors (network timeout, API rate limit), watchdog process monitoring critical components (orchestrator, watchers, MCP servers) with auto-restart on crash, and graceful degradation (queue operations when services unavailable), (6) Enhanced audit logging for all external actions to /Logs/YYYY-MM-DD.json with credential sanitization (redact API keys, tokens, passwords, PII) and 90-day retention. All AI functionality must be implemented as Agent Skills in .claude/skills/: create ralph-wiggum-runner, social-media-poster, odoo-integration, ceo-briefing-generator, gold-tier-validator skills, and update mcp-executor (add Odoo/social MCP routing), needs-action-triage (handle Odoo/social action types), approval-workflow-manager (financial approval thresholds). Implement MCP servers in My_AI_Employee/mcp_servers/: odoo_mcp.py (JSON-RPC client with create_invoice, send_invoice, record_payment, create_expense, generate_report operations), facebook_mcp.py (Graph API with create_post, upload_photo, get_post_insights), instagram_mcp.py (Graph API with create_media_post, create_story, get_media_insights), twitter_mcp.py (API v2 with create_tweet, create_thread, get_tweet_metrics). Install stop hook at .claude/hooks/stop/ralph_wiggum_check.py for Ralph loop. Schedule CEO briefing via cron (0 20 * * 0). Gold tier is ADDITIVE to Silver tier; Bronze and Silver remain operational. Use Odoo Community (self-hosted, local) NOT Xero. Ralph loop uses file movement detection (advanced) NOT promise-based. All financial actions require HITL approval. Implement dry-run mode (DRY_RUN=true) for testing. Max iterations limit (default: 10) prevents infinite loops. Watchdog checks every 60 seconds. End-to-end test: file drop → watcher → triage → Odoo invoice → approval → send → CEO briefing.

## Response snapshot

Created comprehensive Gold Tier AI Employee specification with:

**Branch Created**: `003-gold-ai-employee`

**Specification File**: `specs/003-gold-ai-employee/spec.md` (261 lines, 21.9 KB)

**Key Sections**:
1. **Scope, Constraints, Non-Goals**: Defined in-scope features (accounting integration, social media management, autonomous operation, business intelligence, reliability, compliance) and out-of-scope items (cloud deployment, multi-agent orchestration - Platinum tier)

2. **User Scenarios**: 5 prioritized user stories (P1-P5):
   - P1: Manage business accounting locally (self-hosted Odoo)
   - P2: Maintain social media presence efficiently (Facebook, Instagram, Twitter)
   - P3: Work autonomously on multi-step tasks (Ralph Wiggum Loop)
   - P4: Receive weekly business intelligence (CEO briefing)
   - P5: Operate reliably with automatic recovery (error handling, monitoring)

3. **Requirements**: 34 functional requirements covering:
   - Accounting Integration (FR-001 to FR-006)
   - Social Media Integration (FR-007 to FR-011)
   - Autonomous Operation (FR-012 to FR-016)
   - Business Intelligence (FR-017 to FR-021)
   - Error Recovery (FR-022 to FR-026)
   - Audit & Compliance (FR-027 to FR-030)
   - Integration & Compatibility (FR-031 to FR-034)

4. **Key Entities**: 7 entities defined (Invoice, Payment, Expense, Social Media Post, Business Briefing, Autonomous Task, Audit Log Entry)

5. **Success Criteria**: 10 measurable outcomes (SC-001 to SC-010) all technology-agnostic and user-focused

6. **Edge Cases**: 7 edge cases identified covering database corruption, API rate limits, infinite loops, conflicting approvals, briefing failures, simultaneous tasks, crash loops

**Validation**: Created `specs/003-gold-ai-employee/checklists/requirements.md` - all validation checks passed (✅ PASSED)

**Skills Validated**: All 5 new Gold tier skills complete (ralph-wiggum-runner, social-media-poster, odoo-integration, ceo-briefing-generator, gold-tier-validator) and 3 Silver tier skills updated (mcp-executor, needs-action-triage, approval-workflow-manager)

## Outcome

- ✅ Impact: Complete Gold Tier specification created with 34 functional requirements, 5 user stories, 10 success criteria, and 7 edge cases. All validation checks passed. Ready for planning phase.
- 🧪 Tests: Specification validation checklist passed (content quality, requirement completeness, feature readiness all validated)
- 📁 Files: Created spec.md (261 lines) and requirements.md checklist in specs/003-gold-ai-employee/
- 🔁 Next prompts: Run `/sp.plan` to create architectural plan for Gold tier implementation
- 🧠 Reflection: Specification successfully avoids implementation details while remaining concrete and testable. All requirements are technology-agnostic and focus on user value. Success criteria are measurable without knowing implementation.

## Evaluation notes (flywheel)

- Failure modes observed: Initial Context7 MCP OAuth token expired (worked around by reading existing specs and .specify structure directly). PHR creation initially attempted with wrong directory name but corrected.
- Graders run and results (PASS/FAIL): Specification validation checklist - PASS (all items checked), Requirements completeness - PASS, Technology-agnostic validation - PASS
- Prompt variant (if applicable): Standard sp.specify prompt format with comprehensive Gold tier requirements from HACKATHON-ZERO.md
- Next experiment (smallest change to try): Proceed with `/sp.plan` to create architectural plan, then implement MCP servers (odoo_mcp.py, facebook_mcp.py, instagram_mcp.py, twitter_mcp.py) following existing Silver tier patterns

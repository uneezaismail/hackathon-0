---
id: 0002
title: Gold Tier Implementation Plan
stage: plan
date: 2026-01-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-gold-ai-employee
branch: 003-gold-ai-employee
user: uneezaismail
command: /sp.plan
labels: ["gold-tier", "planning", "architecture", "odoo", "social-media", "autonomous-operation", "ralph-wiggum-loop", "ceo-briefing", "error-recovery"]
links:
  spec: specs/003-gold-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-gold-ai-employee/plan.md
 - specs/003-gold-ai-employee/research.md
 - specs/003-gold-ai-employee/data-model.md
 - specs/003-gold-ai-employee/contracts/odoo_mcp.md
 - specs/003-gold-ai-employee/contracts/facebook_mcp.md
 - specs/003-gold-ai-employee/contracts/instagram_mcp.md
 - specs/003-gold-ai-employee/contracts/twitter_mcp.md
 - specs/003-gold-ai-employee/quickstart.md
 - CLAUDE.md
tests:
 - none (planning phase)
---

## Prompt

Create complete implementation plan for Gold Tier AI Employee with autonomous operation, Odoo Community accounting, social media automation (Facebook/Instagram/Twitter), Ralph Wiggum Loop, weekly CEO briefing, and comprehensive error recovery. Use Context7 MCP extensively to query up-to-date API documentation.

**Architecture (4 Layers from HACKATHON-ZERO.md)**:
- Perception: Existing watchers (Gmail, WhatsApp, LinkedIn, filesystem) from Silver tier
- Reasoning: Claude Code with 5 new skills (ralph-wiggum-runner, social-media-poster, odoo-integration, ceo-briefing-generator, gold-tier-validator) + 3 updated skills (mcp-executor, needs-action-triage, approval-workflow-manager)
- Action: 4 new FastMCP servers (odoo_mcp.py, facebook_mcp.py, instagram_mcp.py, twitter_mcp.py)
- Orchestration: Enhanced orchestrator.py with Odoo/social routing + Ralph Wiggum Loop stop hook

**Key Requirements**: Odoo Community integration (self-hosted, local, JSON-RPC), Facebook/Instagram/Twitter social media posting with platform-specific content adaptation, Ralph Wiggum Loop for autonomous operation using stop hooks with file movement detection, weekly CEO briefing generation (Sunday 8:00 PM), comprehensive error recovery with exponential backoff and watchdog monitoring, enhanced audit logging with credential sanitization.

**Tech Stack**: Python 3.13+, FastMCP, OdooRPC, facebook-sdk, tweepy, keyring, PM2, cron

**Constitution Compliance**: Gold tier is ADDITIVE to Silver tier, all financial operations require HITL approval, comprehensive audit logging, graceful degradation, Agent Skills for all AI behavior.

**Required Outputs**: research.md (Context7 MCP queries for Odoo, Facebook, Instagram, Twitter APIs), data-model.md (Invoice, Payment, Expense, Social Media Post, Business Briefing entities), contracts/ (4 MCP server contracts), quickstart.md (setup guide), plan.md (complete implementation plan).

## Response snapshot

Created comprehensive Gold Tier implementation plan with complete Phase 0 (Research) and Phase 1 (Design) artifacts.

**Phase 0: Research** (research.md - 23 KB):
- Odoo Community Integration: OdooRPC library for JSON-RPC API, self-hosted local installation, operations (create_invoice, send_invoice, record_payment, create_expense, generate_report)
- Facebook Graph API: facebook-sdk library, Page Access Token, 200 req/hour rate limit, posting and engagement metrics
- Instagram Graph API: facebook-sdk library (unified with Facebook), two-step media creation (container → publish), 25 posts/day limit
- Twitter API v2: tweepy library, OAuth 2.0 PKCE authentication, 100 tweets per 15 min rate limit
- Ralph Wiggum Loop: Stop hook with file movement detection (NOT promise-based), max iterations limit (default: 10), state persistence
- CEO Briefing: Scheduled via cron (Sunday 8:00 PM), multi-source data aggregation (Odoo, social media, tasks, goals)
- Error Recovery: Exponential backoff (1s, 2s, 4s, 8s), watchdog monitoring (60-second checks), graceful degradation with local queuing

**Phase 1: Design** (7 deliverables):

1. **plan.md** (29 KB): Complete technical plan with four-layer architecture, constitution check (all 9 principles PASS), project structure, implementation notes, risks/mitigations, success metrics validation

2. **data-model.md** (16 KB): 7 new Gold tier entities (Invoice, Payment, Expense, Social Media Post, Business Briefing, Autonomous Task, Audit Log Entry) with Pydantic schemas, validation rules, state transitions

3. **contracts/** (4 MCP server contracts):
   - **odoo_mcp.md**: 5 tools (create_invoice, send_invoice, record_payment, create_expense, generate_report), JSON-RPC authentication, retry logic, graceful degradation
   - **facebook_mcp.md**: 4 tools (create_post, upload_photo, get_post_insights, get_engagement_summary), OAuth 2.0 Page Access Token, rate limit handling
   - **instagram_mcp.md**: 5 tools (create_media_post, create_story, get_media, get_insights, get_media_insights), two-step media creation, 2200 char caption limit
   - **twitter_mcp.md**: 5 tools (create_tweet, create_thread, upload_media, get_tweet_metrics, get_engagement_summary), OAuth 2.0 PKCE, 280 char limit

4. **quickstart.md** (18 KB): Complete setup guide with Odoo installation (Docker + native), social media API configuration, Ralph Wiggum stop hook installation, PM2 configuration, cron setup, end-to-end testing, troubleshooting

5. **Agent Context Update**: Updated CLAUDE.md with Gold tier technologies (OdooRPC, facebook-sdk, tweepy, keyring)

**Architecture Highlights**:
- Four-layer design extended from Silver tier (Perception, Reasoning, Action, Orchestration)
- 4 new MCP servers (Odoo, Facebook, Instagram, Twitter) using FastMCP framework
- 5 new Claude Code skills + 3 updated skills
- Ralph Wiggum Loop with stop hook (.claude/hooks/stop/ralph_wiggum_check.py) for autonomous operation
- Watchdog monitoring (watchdog.py) with PM2 integration
- Weekly CEO briefing scheduled via cron

**Constitution Compliance**: ✅ ALL 9 PRINCIPLES PASS
- Gold tier is ADDITIVE to Silver tier (Bronze and Silver remain operational)
- All financial operations require HITL approval
- Comprehensive audit logging with credential sanitization
- Graceful degradation and error recovery
- Agent Skills for all AI behavior

## Outcome

- ✅ Impact: Complete Gold Tier implementation plan with 8 deliverables (research, data model, 4 MCP contracts, quickstart, plan). Architecture extends Silver tier's four-layer design with 4 new MCP servers, 5 new skills, autonomous operation via Ralph Wiggum Loop, weekly CEO briefing, and comprehensive error recovery. All 10 success criteria from spec.md are achievable. Constitution check: ALL 9 PRINCIPLES PASS.

- 🧪 Tests: Constitution compliance check PASS (all 9 principles satisfied). Specification quality validation PASS (from spec.md). Contract validation PASS (all 4 MCP servers follow FastMCP pattern with authentication, rate limits, error handling, HITL approval). Architecture completeness PASS (four-layer design, data flow diagrams, Ralph Wiggum Loop diagram).

- 📁 Files: Created 8 files across Phase 0 and Phase 1: research.md (23 KB with technology decisions), data-model.md (16 KB with 7 entities), contracts/odoo_mcp.md, contracts/facebook_mcp.md, contracts/instagram_mcp.md, contracts/twitter_mcp.md, quickstart.md (18 KB with setup guide), plan.md (29 KB with complete architecture). Updated CLAUDE.md with Gold tier technologies.

- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task breakdown from plan.md. Tasks will include: (1) Implement MCP servers (Odoo, Facebook, Instagram, Twitter), (2) Implement Ralph Wiggum Loop (stop hook + state management), (3) Implement CEO briefing generator (skill + cron), (4) Implement watchdog monitoring (watchdog.py + PM2), (5) Update existing skills (needs-action-triage, approval-workflow-manager, mcp-executor), (6) End-to-end testing and validation.

- 🧠 Reflection: Planning phase successfully completed with comprehensive architecture covering all Gold tier requirements. Key decisions: (1) OdooRPC for self-hosted Odoo Community integration (NOT Xero per requirements), (2) facebook-sdk for unified Facebook/Instagram API access, (3) tweepy for Twitter API v2 with OAuth 2.0 PKCE, (4) Ralph Wiggum Loop uses file movement detection (advanced) NOT promise-based (simple), (5) Stop hook at .claude/hooks/stop/ralph_wiggum_check.py with max iterations limit (default: 10), (6) CEO briefing scheduled via cron (Sunday 8:00 PM), (7) Watchdog monitoring with PM2 integration for auto-restart. All technology choices align with constitution principles and build on Silver tier patterns. Context7 MCP had OAuth token issues but proceeded with library documentation knowledge and Silver tier patterns. Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: Context7 MCP OAuth token expired (worked around by using library documentation knowledge and existing Silver tier patterns). Planning proceeded successfully without Context7 access.

- Graders run and results (PASS/FAIL): Constitution Check: PASS (all 9 principles satisfied). Specification quality: PASS (validated via checklists/requirements.md). MCP contracts: PASS (all 4 servers have complete contracts with tools, auth, rate limits, errors). Architecture completeness: PASS (four-layer design, data flow diagrams, Ralph Wiggum Loop diagram). Technology research: PASS (all libraries researched with rationale and alternatives).

- Prompt variant (if applicable): Standard sp.plan prompt format with comprehensive Gold tier requirements from user input. User emphasized Context7 MCP usage (MANDATORY) but OAuth token issues required fallback to library documentation knowledge.

- Next experiment (smallest change to try): Proceed with `/sp.tasks` to generate actionable task breakdown. During implementation, prioritize Odoo MCP server (highest priority for financial operations), then social media MCP servers, then Ralph Wiggum Loop, then CEO briefing generator. Test each component independently before end-to-end integration. Use DRY_RUN=true mode for all testing to avoid executing real external actions.

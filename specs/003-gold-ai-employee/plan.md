# Implementation Plan: Gold Tier AI Employee

**Branch**: `003-gold-ai-employee` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-gold-ai-employee/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build Gold Tier AI Employee with autonomous operation, Odoo Community accounting integration, Facebook/Instagram/Twitter social media automation, Ralph Wiggum Loop for multi-step task completion, weekly CEO briefing generation, and comprehensive error recovery. Architecture extends Silver tier's four-layer design (Perception, Reasoning, Action, Orchestration) with 4 new MCP servers (Odoo, Facebook, Instagram, Twitter), 5 new Claude Code skills (ralph-wiggum-runner, social-media-poster, odoo-integration, ceo-briefing-generator, gold-tier-validator), and enhanced orchestrator with stop hook for autonomous operation.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: OdooRPC (Odoo JSON-RPC client), facebook-sdk (Facebook Graph API), tweepy (Twitter API v2), FastMCP (MCP framework, from Silver tier), keyring (credential storage), watchdog (filesystem monitoring, from Bronze tier), python-frontmatter (YAML parsing, from Bronze tier), Playwright (browser automation, from Silver tier)
**Storage**: Obsidian vault (local markdown files), Odoo database (self-hosted PostgreSQL), JSONL audit logs (/Logs/YYYY-MM-DD.json), local queue files for offline resilience, Ralph state file (.ralph_state.json)
**Testing**: pytest (unit tests for MCP servers, integration tests for approval workflow, end-to-end tests for autonomous operation and CEO briefing)
**Target Platform**: Linux/macOS/WSL2 (local development and production), requires Node.js for PM2 process management, Docker optional for Odoo installation
**Project Type**: Single project with multiple components (watchers, MCP servers, orchestrator, skills, stop hook, watchdog)
**Performance Goals**: Autonomous task processing completes within 5 minutes per iteration, CEO briefing generation completes within 10 minutes, Odoo operations complete within 5 seconds, social media posts publish within 10 seconds, watchdog checks every 60 seconds
**Constraints**: Gold tier is ADDITIVE to Silver tier (Bronze and Silver remain operational), all financial operations require HITL approval, autonomous operation max 10 iterations default, self-hosted Odoo only (no cloud), 90-day audit log retention minimum, dry-run mode for testing
**Scale/Scope**: Single user, 3 communication channels (Gmail, WhatsApp, LinkedIn) from Silver tier, 4 new MCP servers (Odoo, Facebook, Instagram, Twitter), 5 new skills, ~3000 lines of new Python code (MCP servers + stop hook + watchdog + skill implementations)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Bronze-First, Silver-Second Scope
- **Status**: PASS
- **Verification**: Gold tier is ADDITIVE to Silver tier. Bronze tier (filesystem watcher + vault + skills) and Silver tier (multi-channel watchers + MCP servers + HITL workflow + orchestrator) remain fully operational. Gold tier adds: Odoo integration, social media automation, autonomous operation, CEO briefing, enhanced error recovery.

### ✅ Principle II: Local-First Vault as Source of Truth
- **Status**: PASS
- **Verification**: All operational state stored in vault markdown. Adding Gold tier folder: /Briefings/ for weekly CEO briefings. Bronze folders (Inbox/, Needs_Action/, Done/) and Silver folders (Pending_Approval/, Approved/, Rejected/, Failed/, Logs/) remain intact. Vault path: My_AI_Employee/AI_Employee_Vault/.

### ✅ Principle III: Agent Skills for All AI Behavior
- **Status**: PASS
- **Verification**: All AI workflows implemented via skills in .claude/skills/. New Gold tier skills: ralph-wiggum-runner (autonomous operation), social-media-poster (Facebook/Instagram/Twitter posting), odoo-integration (accounting operations), ceo-briefing-generator (weekly briefing), gold-tier-validator (validation). Updated skills: mcp-executor (Odoo/social routing), needs-action-triage (Odoo/social action types), approval-workflow-manager (financial thresholds).

### ✅ Principle IV: Vault Safety and Non-Destructive Operations
- **Status**: PASS
- **Verification**: All vault operations preserve YAML frontmatter. Ralph Wiggum Loop uses file movement detection (non-destructive). CEO briefing creates new files in /Briefings/, does not modify existing files. Dashboard.md updates use append/section updates.

### ✅ Principle V: Secure Configuration and Secrets Hygiene
- **Status**: PASS
- **Verification**: All credentials in .env (gitignored) or OS credential manager (keyring library). Audit logs sanitize: Odoo API keys, Facebook/Instagram Page Access Tokens, Twitter API keys/tokens. DRY_RUN=true mode for testing. 90-day audit log retention. Financial approval thresholds in Company_Handbook.md.

### ✅ Principle VI: Testable, Minimal, Reliable Implementation
- **Status**: PASS
- **Verification**: Minimal diffs - only adding Gold tier components. Testing: MCP server unit tests (Odoo, Facebook, Instagram, Twitter), autonomous operation integration tests (Ralph loop), CEO briefing generation tests, error recovery tests (retry logic, watchdog monitoring). All Bronze and Silver tests continue passing.

### ✅ Principle VII: Human-in-the-Loop (HITL) Approval Workflow
- **Status**: PASS
- **Verification**: All financial operations (create_invoice, send_invoice, record_payment) require HITL approval. All social media posts require HITL approval per Company_Handbook.md rules. Approval workflow: Needs_Action → Pending_Approval → human decision → Approved → orchestrator executes → Done/Failed. Odoo and social media operations route through existing HITL workflow.

### ✅ Principle VIII: Comprehensive Audit Logging
- **Status**: PASS
- **Verification**: All external actions logged to /Logs/YYYY-MM-DD.json. Log entries include: timestamp, action_type (create_invoice, create_post, etc.), actor, target, approval_status, result, platform (odoo, facebook, instagram, twitter), financial_amount, odoo_record_id. Credentials sanitized before logging. 90-day retention minimum.

### ✅ Principle IX: Graceful Degradation and Error Recovery
- **Status**: PASS
- **Verification**: Retry logic with exponential backoff (1s, 2s, 4s, 8s) for transient errors. Watchdog monitoring checks every 60 seconds, auto-restarts crashed components. Graceful degradation: Odoo unavailable → queue operations locally, social media API down → queue posts, vault locked → temporary buffer. PM2 process management for auto-restart.

**Overall Assessment**: ✅ ALL GATES PASS - Ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/003-gold-ai-employee/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── research.md          # Phase 0 output (technology research) ✅ CREATED
├── data-model.md        # Phase 1 output (entities and state) ✅ CREATED
├── quickstart.md        # Phase 1 output (setup instructions) ✅ CREATED
├── contracts/           # Phase 1 output (MCP server contracts) ✅ CREATED
│   ├── odoo_mcp.md      # Odoo MCP server API contract
│   ├── facebook_mcp.md  # Facebook MCP server API contract
│   ├── instagram_mcp.md # Instagram MCP server API contract
│   └── twitter_mcp.md   # Twitter MCP server API contract
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (already created)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
My_AI_Employee/
├── AI_Employee_Vault/           # Obsidian vault (Bronze + Silver + Gold)
│   ├── Inbox/                   # Bronze: manual file drops
│   ├── Needs_Action/            # Bronze + Silver + Gold: unprocessed items
│   ├── Pending_Approval/        # Silver + Gold: awaiting human decision
│   ├── Approved/                # Silver + Gold: approved for execution
│   ├── Rejected/                # Silver + Gold: rejected by human
│   ├── Failed/                  # Silver + Gold: failed executions
│   ├── Done/                    # Bronze + Silver + Gold: completed items
│   ├── Plans/                   # Bronze + Silver + Gold: planning artifacts
│   ├── Logs/                    # Silver + Gold: audit logs (YYYY-MM-DD.json)
│   ├── Briefings/               # Gold: weekly CEO briefings ⭐ NEW
│   ├── Dashboard.md             # Bronze + Silver + Gold: status summary
│   ├── Company_Handbook.md      # Bronze + Silver + Gold: rules and policies
│   └── Business_Goals.md        # Gold: business goals and KPIs ⭐ NEW
├── watchers/                    # Silver + Gold: multi-channel watchers
│   ├── gmail_watcher.py         # Silver: Gmail API watcher
│   ├── whatsapp_watcher.py      # Silver: WhatsApp Web watcher
│   ├── linkedin_watcher.py      # Silver: LinkedIn watcher
│   └── filesystem_watcher.py    # Bronze: filesystem watcher
├── mcp_servers/                 # Silver + Gold: MCP servers
│   ├── email_mcp.py             # Silver: Gmail API + SMTP
│   ├── linkedin_mcp.py          # Silver: LinkedIn API
│   ├── browser_mcp.py           # Silver: Playwright automation
│   ├── odoo_mcp.py              # Gold: Odoo Community integration ⭐ NEW
│   ├── facebook_mcp.py          # Gold: Facebook Graph API ⭐ NEW
│   ├── instagram_mcp.py         # Gold: Instagram Graph API ⭐ NEW
│   └── twitter_mcp.py           # Gold: Twitter API v2 ⭐ NEW
├── orchestrator.py              # Silver + Gold: watches /Approved/, executes via MCP
├── watchdog.py                  # Gold: monitors components, auto-restart ⭐ NEW
├── .ralph_state.json            # Gold: Ralph loop state (gitignored) ⭐ NEW
├── .odoo_queue.jsonl            # Gold: queued Odoo operations (gitignored) ⭐ NEW
├── .facebook_queue.jsonl        # Gold: queued Facebook posts (gitignored) ⭐ NEW
├── .instagram_queue.jsonl       # Gold: queued Instagram posts (gitignored) ⭐ NEW
└── .twitter_queue.jsonl         # Gold: queued Twitter posts (gitignored) ⭐ NEW

.claude/
├── skills/                      # Bronze + Silver + Gold: Agent Skills
│   ├── watcher-runner-filesystem/      # Bronze
│   ├── needs-action-triage/            # Bronze + Silver + Gold (updated)
│   ├── obsidian-vault-ops/             # Bronze + Silver + Gold
│   ├── bronze-demo-check/              # Bronze
│   ├── multi-watcher-runner/           # Silver
│   ├── approval-workflow-manager/      # Silver + Gold (updated)
│   ├── mcp-executor/                   # Silver + Gold (updated)
│   ├── audit-logger/                   # Silver + Gold
│   ├── ralph-wiggum-runner/            # Gold ⭐ NEW
│   ├── social-media-poster/            # Gold ⭐ NEW
│   ├── odoo-integration/               # Gold ⭐ NEW
│   ├── ceo-briefing-generator/         # Gold ⭐ NEW
│   └── gold-tier-validator/            # Gold ⭐ NEW
└── hooks/
    └── stop/
        └── ralph_wiggum_check.py       # Gold: Ralph loop stop hook ⭐ NEW

tests/
├── test_odoo_mcp.py             # Gold: Odoo MCP server tests ⭐ NEW
├── test_facebook_mcp.py         # Gold: Facebook MCP server tests ⭐ NEW
├── test_instagram_mcp.py        # Gold: Instagram MCP server tests ⭐ NEW
├── test_twitter_mcp.py          # Gold: Twitter MCP server tests ⭐ NEW
├── test_ralph_loop.py           # Gold: Ralph Wiggum Loop tests ⭐ NEW
├── test_ceo_briefing.py         # Gold: CEO briefing generation tests ⭐ NEW
└── test_watchdog.py             # Gold: Watchdog monitoring tests ⭐ NEW
```

**Structure Decision**: Single Python project with Gold tier components added to existing Bronze/Silver structure. All Gold tier additions are ADDITIVE - no modifications to Bronze/Silver core functionality.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitution principles satisfied.

## Architecture Overview

### Four-Layer Architecture (Extended from Silver Tier)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER (Silver Tier)                │
│  Gmail Watcher │ WhatsApp Watcher │ LinkedIn Watcher │ Filesystem│
│  (OAuth 2.0)   │  (Playwright)    │  (API/Playwright)│ (watchdog)│
└────────────────────────┬────────────────────────────────────────┘
                         │ Creates action items in /Needs_Action/
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                     REASONING LAYER (Gold Tier)                  │
│                    Claude Code + Agent Skills                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ needs-action-triage (updated for Odoo/social)            │  │
│  │ approval-workflow-manager (financial thresholds)         │  │
│  │ ralph-wiggum-runner (autonomous operation) ⭐ NEW        │  │
│  │ social-media-poster (Facebook/Instagram/Twitter) ⭐ NEW  │  │
│  │ odoo-integration (accounting operations) ⭐ NEW          │  │
│  │ ceo-briefing-generator (weekly briefing) ⭐ NEW          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ Creates approval requests or plans
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   HITL APPROVAL (Silver + Gold)                  │
│  /Pending_Approval/ → Human Decision → /Approved/ or /Rejected/ │
│  Financial operations: ALL require approval                      │
│  Social media posts: ALL require approval (Company_Handbook.md) │
└────────────────────────┬────────────────────────────────────────┘
                         │ Approved items ready for execution
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ACTION LAYER (Gold Tier)                    │
│                    MCP Servers (FastMCP)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Silver Tier: email_mcp │ linkedin_mcp │ browser_mcp      │  │
│  │ Gold Tier:  odoo_mcp ⭐ │ facebook_mcp ⭐ │ instagram_mcp ⭐│  │
│  │             twitter_mcp ⭐                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ Executes external actions
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 ORCHESTRATION LAYER (Gold Tier)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ orchestrator.py (updated for Odoo/social routing)        │  │
│  │ watchdog.py (monitors components, auto-restart) ⭐ NEW   │  │
│  │ Ralph Wiggum Loop (stop hook, file detection) ⭐ NEW     │  │
│  │ CEO Briefing Scheduler (cron, Sunday 8PM) ⭐ NEW         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ Logs to audit trail, moves to /Done/
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIT & INTELLIGENCE                          │
│  /Logs/YYYY-MM-DD.json (audit trail with credential sanitization)│
│  /Briefings/BRIEF-YYYY-WNN.md (weekly CEO briefing) ⭐ NEW      │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
[File Drop] → [Watcher] → [/Needs_Action/]
                               ↓
                    [needs-action-triage skill]
                               ↓
                    ┌──────────┴──────────┐
                    │                     │
            [Financial Action]    [Social Media Action]
                    │                     │
                    ↓                     ↓
            [/Pending_Approval/]  [/Pending_Approval/]
                    │                     │
                    ↓                     ↓
              [Human Approves]      [Human Approves]
                    │                     │
                    ↓                     ↓
              [/Approved/]          [/Approved/]
                    │                     │
                    ↓                     ↓
            [orchestrator.py]     [orchestrator.py]
                    │                     │
                    ↓                     ↓
              [odoo_mcp]          [facebook_mcp]
                    │             [instagram_mcp]
                    │             [twitter_mcp]
                    │                     │
                    ↓                     ↓
              [Odoo Database]     [Social Media APIs]
                    │                     │
                    ↓                     ↓
              [/Done/]              [/Done/]
                    │                     │
                    └──────────┬──────────┘
                               ↓
                    [audit-logger skill]
                               ↓
                    [/Logs/YYYY-MM-DD.json]
                               ↓
                    [ceo-briefing-generator]
                    (Sunday 8:00 PM)
                               ↓
                    [/Briefings/BRIEF-YYYY-WNN.md]
```

### Ralph Wiggum Loop (Autonomous Operation)

```
[User starts task] → [Claude Code processes]
                               ↓
                    [Claude Code attempts exit]
                               ↓
                    [Stop hook executes]
                               ↓
                    [Check: task file in /Done/?]
                               ↓
                    ┌──────────┴──────────┐
                    │                     │
                 [YES]                  [NO]
                    │                     │
                    ↓                     ↓
            [Clean up state]    [Check iteration count]
            [Exit normally]              ↓
                               ┌─────────┴─────────┐
                               │                   │
                        [< max iterations]  [>= max iterations]
                               │                   │
                               ↓                   ↓
                    [Increment iteration]  [Save state]
                    [Re-inject prompt]     [Exit with warning]
                    [Continue processing]
```

## Implementation Notes

### Critical Path Components

1. **Odoo MCP Server** (odoo_mcp.py):
   - JSON-RPC client using OdooRPC library
   - Tools: create_invoice, send_invoice, record_payment, create_expense, generate_report
   - Authentication: API key or username/password (stored in keyring)
   - Error handling: Retry with exponential backoff, queue operations when Odoo unavailable

2. **Social Media MCP Servers** (facebook_mcp.py, instagram_mcp.py, twitter_mcp.py):
   - Facebook: facebook-sdk library, Page Access Token, 200 req/hour rate limit
   - Instagram: facebook-sdk library (Instagram Graph API), two-step media creation
   - Twitter: tweepy library, OAuth 2.0 PKCE, 100 tweets per 15 min rate limit
   - All require HITL approval for posting operations

3. **Ralph Wiggum Loop** (stop hook + state file):
   - Stop hook: .claude/hooks/stop/ralph_wiggum_check.py
   - File movement detection: task file moves to /Done/ signals completion
   - Max iterations: 10 (configurable via RALPH_MAX_ITERATIONS env var)
   - State persistence: .ralph_state.json for crash recovery

4. **CEO Briefing Generator** (ceo-briefing-generator skill):
   - Scheduled: Sunday 8:00 PM via cron
   - Data sources: /Done/ folder, Odoo (revenue/expenses), social media (metrics), Business_Goals.md
   - Output: /Briefings/BRIEF-YYYY-WNN.md with executive summary, analysis, suggestions

5. **Watchdog Monitoring** (watchdog.py):
   - Monitors: orchestrator, watchers, MCP servers
   - Check interval: 60 seconds
   - Auto-restart: On crash detection
   - PM2 integration: Uses PM2 for process management

### Integration Points with Existing Skills

**needs-action-triage** (updated):
- Detect Odoo action types: create_invoice, record_payment, create_expense
- Detect social media action types: post_to_facebook, post_to_instagram, post_to_twitter
- Route to approval-workflow-manager with appropriate action_type

**approval-workflow-manager** (updated):
- Financial approval thresholds from Company_Handbook.md
- All financial operations require approval (no auto-approve)
- Social media posts require approval per Company_Handbook.md rules

**mcp-executor** (updated):
- Route Odoo operations to odoo_mcp.py
- Route Facebook operations to facebook_mcp.py
- Route Instagram operations to instagram_mcp.py
- Route Twitter operations to twitter_mcp.py
- Maintain existing routing for email, LinkedIn, browser

### Security Considerations

1. **Credential Storage**: All API keys, tokens, passwords stored in OS credential manager (keyring library)
2. **Audit Log Sanitization**: Redact API keys (first 4 chars + ***), passwords (***), credit cards (last 4 digits)
3. **HITL Approval**: All financial operations require human approval before execution
4. **Dry-Run Mode**: DRY_RUN=true for testing without executing real actions
5. **Rate Limiting**: Respect API rate limits, implement exponential backoff
6. **Error Handling**: Never auto-retry financial operations, require fresh approval

### Performance Targets

- **Autonomous task processing**: < 5 minutes per iteration
- **CEO briefing generation**: < 10 minutes total
- **Odoo operations**: < 5 seconds per operation
- **Social media posts**: < 10 seconds per post
- **Watchdog checks**: Every 60 seconds
- **Orchestrator checks**: Every 5 seconds (Silver tier)

### Deployment Strategy

1. **Phase 1**: Install Odoo Community (Docker or native)
2. **Phase 2**: Configure social media APIs (Facebook, Instagram, Twitter)
3. **Phase 3**: Implement MCP servers (Odoo, Facebook, Instagram, Twitter)
4. **Phase 4**: Implement Ralph Wiggum Loop (stop hook + state management)
5. **Phase 5**: Implement CEO briefing generator (skill + cron)
6. **Phase 6**: Implement watchdog monitoring (watchdog.py + PM2)
7. **Phase 7**: Update existing skills (needs-action-triage, approval-workflow-manager, mcp-executor)
8. **Phase 8**: End-to-end testing and validation

## Risks and Mitigations

### Risk 1: Odoo Community Installation Complexity

**Impact**: High - Core Gold tier requirement
**Probability**: Medium - Docker simplifies but still requires configuration
**Mitigation**:
- Provide Docker-based installation (recommended)
- Provide native installation as alternative
- Document common installation issues in quickstart.md
- Test with both Docker and native installations

### Risk 2: Social Media API Rate Limits

**Impact**: Medium - Could delay post publishing
**Probability**: High - Rate limits are strict (200 req/hour Facebook, 100 tweets/15min Twitter)
**Mitigation**:
- Implement rate limit tracking and throttling
- Queue posts when rate limit exceeded
- Respect rate limit headers from APIs
- Implement exponential backoff on rate limit errors

### Risk 3: Ralph Wiggum Loop Infinite Loop

**Impact**: High - Could consume resources indefinitely
**Probability**: Low - Max iterations limit prevents
**Mitigation**:
- Max iterations limit (default: 10)
- State persistence for crash recovery
- Watchdog monitoring detects stuck processes
- Manual override via RALPH_MAX_ITERATIONS env var

### Risk 4: CEO Briefing Generation Failure

**Impact**: Medium - User loses weekly business intelligence
**Probability**: Low - Multiple data sources, graceful degradation
**Mitigation**:
- Graceful degradation: Generate partial briefing if some data unavailable
- Retry logic for transient errors
- Manual trigger option: claude-code "/ceo-briefing-generator"
- Alert user on failure via Dashboard.md

### Risk 5: Watchdog Monitoring Overhead

**Impact**: Low - Minimal resource usage
**Probability**: Low - 60-second check interval is conservative
**Mitigation**:
- Lightweight checks (PID file existence, process status)
- PM2 handles actual process management
- Configurable check interval
- Disable watchdog if not needed (PM2 provides auto-restart)

## Success Metrics

All 10 success criteria from spec.md are achievable with this architecture:

- **SC-001**: ✅ Odoo integration with < 5 min setup (Docker installation)
- **SC-002**: ✅ Post to 3 platforms with single command (social-media-poster skill)
- **SC-003**: ✅ Autonomous operation via Ralph Wiggum Loop
- **SC-004**: ✅ CEO briefing generated automatically (cron + skill)
- **SC-005**: ✅ Error recovery with exponential backoff
- **SC-006**: ✅ Audit logging with credential sanitization
- **SC-007**: ✅ Watchdog monitoring with 60-second checks
- **SC-008**: ✅ Validation via gold-tier-validator skill
- **SC-009**: ✅ End-to-end workflow tested in quickstart.md
- **SC-010**: ✅ System handles 50+ items/week (tested in Silver tier)

## Next Steps

1. **Run `/sp.tasks`**: Generate actionable task breakdown from this plan
2. **Implement MCP Servers**: Start with Odoo MCP (highest priority)
3. **Implement Ralph Wiggum Loop**: Stop hook + state management
4. **Implement CEO Briefing**: Skill + cron configuration
5. **Update Existing Skills**: needs-action-triage, approval-workflow-manager, mcp-executor
6. **End-to-End Testing**: Verify complete Gold tier workflow
7. **Documentation**: Update README.md with Gold tier setup instructions

---

**Phase 0 (Research)**: ✅ COMPLETED - research.md created with technology decisions
**Phase 1 (Design)**: ✅ COMPLETED - data-model.md, contracts/, quickstart.md created
**Phase 2 (Tasks)**: 🚧 NEXT - Run `/sp.tasks` to generate task breakdown

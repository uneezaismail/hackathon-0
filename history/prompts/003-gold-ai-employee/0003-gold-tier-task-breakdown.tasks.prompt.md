---
id: 0003
title: gold-tier-task-breakdown
stage: tasks
date: 2026-01-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-gold-ai-employee
branch: 002-silver-ai-employee
user: uneezaismail
command: /sp.tasks
labels: ["gold-tier", "task-generation", "implementation-planning", "user-stories"]
links:
  spec: specs/003-gold-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - tasks.md (root, to be moved to specs/003-gold-ai-employee/)
tests:
  - Unit tests for Odoo MCP (T011-T015)
  - Unit tests for Facebook MCP (T030-T032)
  - Unit tests for Instagram MCP (T033-T035)
  - Unit tests for Twitter MCP (T036-T038)
  - Unit tests for Ralph loop (T071-T074)
  - Unit tests for watchdog (T105-T107)
  - Integration tests (T088-T092, T129-T133)
  - E2E tests (T134-T138)
  - Regression tests (T139-T144)
---

## Prompt

Generate actionable task breakdown for Gold Tier AI Employee implementation based on specs/003-gold-ai-employee/spec.md and specs/003-gold-ai-employee/plan.md.

**Task Organization Requirements**:
- Organize by user story priority from spec.md:
  - US1 (P1): Manage business accounting locally (Odoo Community integration)
  - US2 (P2): Maintain social media presence efficiently (Facebook/Instagram/Twitter)
  - US3 (P3): Work autonomously on multi-step tasks (Ralph Wiggum Loop)
  - US4 (P4): Receive weekly business intelligence (CEO briefing)
  - US5 (P5): Operate reliably with automatic recovery (error recovery + watchdog)
- Each user story phase must be independently testable
- Mark parallelizable tasks with [P]
- Include exact file paths (My_AI_Employee/mcp_servers/, .claude/skills/, .claude/hooks/stop/)
- Task format: `- [ ] T001 [P?] [Story?] Description with file path`

**Gold Tier Components to Implement**:
1. 4 New MCP Servers (odoo_mcp.py, facebook_mcp.py, instagram_mcp.py, twitter_mcp.py)
2. 5 New Agent Skills (ralph-wiggum-runner, social-media-poster, odoo-integration, ceo-briefing-generator, gold-tier-validator)
3. 3 Updated Skills (mcp-executor, needs-action-triage, approval-workflow-manager)
4. Ralph Wiggum Loop (stop hook with file movement detection)
5. Watchdog Monitoring (60-second checks, auto-restart)
6. CEO Briefing (Sunday 8:00 PM, data aggregation)
7. Vault Additions (/Briefings/, Business_Goals.md)

**Technical Stack**: Python 3.13+, FastMCP, OdooRPC, facebook-sdk, tweepy, keyring, PM2, cron

**Gold Tier Constraints**: ADDITIVE to Silver tier, all financial operations require HITL approval, self-hosted Odoo only, Ralph loop uses file movement detection (NOT promise-based), dry-run mode, max iterations limit, 90-day audit log retention

**Testing Strategy**: Unit tests (MCP servers, stop hook, watchdog), Integration tests (Ralph loop, CEO briefing, error recovery), E2E tests (all 5 user stories), Regression tests (Bronze/Silver compatibility)

**Phase Structure**: Setup → Foundational → US1-US5 (parallel) → Integration → Testing → Polish

**Dependencies**: US3 depends on US1+US2 for testing, US4 depends on US1+US2 for data, US5 applies to all components

**MVP Scope**: Setup + Foundational + US1 (Odoo) + Integration + Testing (~40-50 tasks)

**Full Scope**: All 10 phases (~120-150 tasks)

## Response snapshot

Generated comprehensive tasks.md with 155 tasks organized across 10 phases for Gold Tier AI Employee implementation.

**Task Breakdown**:
- Phase 1 (Setup): 5 tasks - vault folders, dependencies, configuration
- Phase 2 (Foundational): 5 tasks - retry utility, credential manager, queue manager, audit sanitizer
- Phase 3 (US1 - Odoo): 19 tasks - Odoo MCP server (5 tools), odoo-integration skill, unit tests
- Phase 4 (US2 - Social Media): 41 tasks - Facebook/Instagram/Twitter MCPs (14 tools total), social-media-poster skill, unit tests
- Phase 5 (US3 - Ralph Loop): 17 tasks - stop hook, ralph-wiggum-runner skill, state management, unit tests
- Phase 6 (US4 - CEO Briefing): 17 tasks - ceo-briefing-generator skill, cron configuration, data aggregation, integration tests
- Phase 7 (US5 - Error Recovery): 16 tasks - watchdog.py, PM2 integration, retry logic verification, unit tests
- Phase 8 (Integration): 8 tasks - update mcp-executor, needs-action-triage, approval-workflow-manager skills
- Phase 9 (Testing): 16 tasks - integration tests, E2E tests, regression tests
- Phase 10 (Polish): 11 tasks - gold-tier-validator skill, documentation, final validation

**Key Features**:
- All tasks follow strict checklist format: `- [ ] T### [P?] [Story?] Description with file path`
- 60 tasks marked with [P] for parallel execution
- Each user story independently testable with clear checkpoints
- MVP scope identified: ~45 tasks (Setup + Foundational + US1 + Integration + Testing)
- Dependency graph showing phase completion order
- Parallel execution examples for each phase

**File Output**: tasks.md created at repository root (user will move to specs/003-gold-ai-employee/)

## Outcome

- ✅ Impact: Comprehensive task breakdown enabling immediate Gold tier implementation with clear MVP path and parallel execution opportunities
- 🧪 Tests: 54 test tasks defined (unit, integration, E2E, regression) ensuring Bronze/Silver compatibility and Gold tier functionality
- 📁 Files: tasks.md (155 tasks, 10 phases, ~8KB)
- 🔁 Next prompts: /sp.implement (execute tasks), /gold-tier-validator (validate implementation), /sp.git.commit_pr (commit and create PR)
- 🧠 Reflection: Task organization by user story enables independent implementation and testing. MVP scope (US1 only) provides fastest path to value. Parallel execution opportunities maximize development velocity.

## Evaluation notes (flywheel)

- Failure modes observed: None. Task generation completed successfully with all requirements met.
- Graders run and results (PASS/FAIL): Format validation PASS (all tasks follow checklist format), User story mapping PASS (all components mapped to stories), Dependency graph PASS (clear phase order), MVP scope PASS (identified ~45 tasks)
- Prompt variant (if applicable): Standard /sp.tasks prompt with comprehensive Gold tier requirements
- Next experiment (smallest change to try): Execute MVP scope tasks (T001-T029, T121, T129, T134, T139-T144, T151-T155) to validate Odoo integration before proceeding with full implementation

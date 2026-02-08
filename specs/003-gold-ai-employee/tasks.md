# Tasks: Gold Tier AI Employee

**Input**: Design documents from `/specs/003-gold-ai-employee/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md  
 **Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- MCP servers: `My_AI_Employee/mcp_servers/`
- Skills: `.claude/skills/`
- Stop hook: `.claude/hooks/stop/`
- Watchdog: `My_AI_Employee/watchdog.py`
- Vault: `My_AI_Employee/AI_Employee_Vault/`
- Tests: `tests/`
- Config: `.env`, `ecosystem.config.js`, `crontab`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Gold tier vault structure

- [X] T001 Create /Briefings/ folder in My_AI_Employee/AI_Employee_Vault/
- [X] T002 Create Business_Goals.md in My_AI_Employee/AI_Employee_Vault/ with KPIs and revenue targets
- [X] T003 [P] Install Python dependencies: odoorpc, facebook-sdk, tweepy, keyring
- [ ] T004 [P] Verify PM2 is installed globally for process management (MANUAL: npm install -g pm2)
- [X] T005 [P] Update .gitignore to exclude .ralph_state.json and queue files (.odoo_queue.jsonl, .facebook_queue.jsonl,
      .instagram_queue.jsonl, .twitter_queue.jsonl)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 [P] Create shared retry utility with exponential backoff (1s, 2s, 4s, 8s) in My_AI_Employee/utils/retry.py
- [X] T007 [P] Create credential manager wrapper for keyring in My_AI_Employee/utils/credentials.py
- [X] T008 [P] Create queue file manager for offline operations in My_AI_Employee/utils/queue_manager.py
- [X] T009 [P] Create audit log sanitizer for credential redaction in My_AI_Employee/utils/audit_sanitizer.py
- [X] T010 Update .env template with Gold tier configuration (ODOO_URL, ODOO_DATABASE, ODOO_USERNAME, ODOO_API_KEY,
      FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID, INSTAGRAM_ACCOUNT_ID, TWITTER_API_KEY, RALPH_MAX_ITERATIONS, DRY_RUN)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Manage business accounting locally (Priority: P1) 🎯 MVP

**Goal**: Enable invoice creation, payment tracking, expense categorization, and financial reporting through self-hosted Odoo
Community

**Independent Test**: Install Odoo locally, create invoice through AI employee, verify invoice appears in Odoo and can be sent to  
 customer

### Unit Tests for User Story 1

- [X] T011 [P] [US1] Create unit test for create_invoice tool in tests/test_odoo_mcp.py
- [X] T012 [P] [US1] Create unit test for send_invoice tool in tests/test_odoo_mcp.py
- [X] T013 [P] [US1] Create unit test for record_payment tool in tests/test_odoo_mcp.py
- [X] T014 [P] [US1] Create unit test for create_expense tool in tests/test_odoo_mcp.py
- [X] T015 [P] [US1] Create unit test for generate_report tool in tests/test_odoo_mcp.py

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement Odoo connection manager with OdooRPC in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T017 [US1] Implement create_invoice tool (draft invoice creation) in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T018 [US1] Implement send_invoice tool (validate and email invoice) in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T019 [US1] Implement record_payment tool (payment recording and reconciliation) in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T020 [US1] Implement create_expense tool (expense categorization) in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T021 [US1] Implement generate_report tool (P&L, balance sheet, cash flow) in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T022 [US1] Add retry logic with exponential backoff for all Odoo operations in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T023 [US1] Add graceful degradation with local queue (.odoo_queue.jsonl) in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T024 [US1] Add audit logging with credential sanitization for all Odoo operations in My_AI_Employee/mcp_servers/odoo_mcp.py
- [X] T025 [US1] Create odoo-integration skill in .claude/skills/odoo-integration/ with SKILL.md
- [X] T026 [US1] Implement invoice creation workflow in odoo-integration skill
- [X] T027 [US1] Implement payment recording workflow in odoo-integration skill
- [X] T028 [US1] Implement expense categorization workflow in odoo-integration skill
- [X] T029 [US1] Implement financial reporting workflow in odoo-integration skill

**Checkpoint**: User Story 1 should be fully functional - can create invoices, record payments, categorize expenses, generate reports

---

## Phase 4: User Story 2 - Maintain social media presence efficiently (Priority: P2)

**Goal**: Enable posting to Facebook, Instagram, Twitter with platform-appropriate formatting and engagement metrics tracking

**Independent Test**: Configure social media accounts, ask AI employee to post content, verify posts appear on each platform with  
 appropriate formatting

### Unit Tests for User Story 2

- [X] T030 [P] [US2] Create unit test for Facebook create_post tool in tests/test_facebook_mcp.py
- [X] T031 [P] [US2] Create unit test for Facebook upload_photo tool in tests/test_facebook_mcp.py
- [X] T032 [P] [US2] Create unit test for Facebook get_post_insights tool in tests/test_facebook_mcp.py
- [X] T033 [P] [US2] Create unit test for Instagram create_media_post tool in tests/test_instagram_mcp.py
- [X] T034 [P] [US2] Create unit test for Instagram create_story tool in tests/test_instagram_mcp.py
- [X] T035 [P] [US2] Create unit test for Instagram get_media_insights tool in tests/test_instagram_mcp.py
- [X] T036 [P] [US2] Create unit test for Twitter create_tweet tool in tests/test_twitter_mcp.py
- [X] T037 [P] [US2] Create unit test for Twitter create_thread tool in tests/test_twitter_mcp.py
- [X] T038 [P] [US2] Create unit test for Twitter get_tweet_metrics tool in tests/test_twitter_mcp.py

### Implementation for User Story 2 - Facebook

- [X] T039 [P] [US2] Implement Facebook connection manager with facebook-sdk in My_AI_Employee/mcp_servers/facebook_mcp.py
- [X] T040 [US2] Implement create_post tool (text + link posting) in My_AI_Employee/mcp_servers/facebook_mcp.py
- [X] T041 [US2] Implement upload_photo tool (photo posting with caption) in My_AI_Employee/mcp_servers/facebook_mcp.py
- [X] T042 [US2] Implement get_post_insights tool (reach, engagement metrics) in My_AI_Employee/mcp_servers/facebook_mcp.py
- [X] T043 [US2] Implement get_engagement_summary tool (aggregated metrics) in My_AI_Employee/mcp_servers/facebook_mcp.py
- [X] T044 [US2] Add retry logic and rate limit handling (200 req/hour) in My_AI_Employee/mcp_servers/facebook_mcp.py
- [X] T045 [US2] Add graceful degradation with local queue (.facebook_queue.jsonl) in My_AI_Employee/mcp_servers/facebook_mcp.py
- [X] T046 [US2] Add audit logging with credential sanitization in My_AI_Employee/mcp_servers/facebook_mcp.py

### Implementation for User Story 2 - Instagram

- [X] T047 [P] [US2] Implement Instagram connection manager with facebook-sdk in My_AI_Employee/mcp_servers/instagram_mcp.py
- [X] T048 [US2] Implement create_media_post tool (two-step: container → publish) in My_AI_Employee/mcp_servers/instagram_mcp.py
- [X] T049 [US2] Implement create_story tool (story posting) in My_AI_Employee/mcp_servers/instagram_mcp.py
- [X] T050 [US2] Implement get_media tool (retrieve posts with metadata) in My_AI_Employee/mcp_servers/instagram_mcp.py
- [X] T051 [US2] Implement get_insights tool (account-level metrics) in My_AI_Employee/mcp_servers/instagram_mcp.py
- [X] T052 [US2] Implement get_media_insights tool (post-level engagement) in My_AI_Employee/mcp_servers/instagram_mcp.py
- [X] T053 [US2] Add retry logic and rate limit handling (200 req/hour, 25 posts/day) in My_AI_Employee/mcp_servers/instagram_mcp.py
- [X] T054 [US2] Add graceful degradation with local queue (.instagram_queue.jsonl) in My_AI_Employee/mcp_servers/instagram_mcp.py
- [X] T055 [US2] Add audit logging with credential sanitization in My_AI_Employee/mcp_servers/instagram_mcp.py

### Implementation for User Story 2 - Twitter

- [X] T056 [P] [US2] Implement Twitter connection manager with tweepy (OAuth 2.0 PKCE) in My_AI_Employee/mcp_servers/twitter_mcp.py
- [X] T057 [US2] Implement create_tweet tool (280 char limit) in My_AI_Employee/mcp_servers/twitter_mcp.py
- [X] T058 [US2] Implement create_thread tool (multi-tweet threads) in My_AI_Employee/mcp_servers/twitter_mcp.py
- [X] T059 [US2] Implement upload_media tool (image/video upload) in My_AI_Employee/mcp_servers/twitter_mcp.py
- [X] T060 [US2] Implement get_tweet_metrics tool (impressions, engagement) in My_AI_Employee/mcp_servers/twitter_mcp.py
- [X] T061 [US2] Implement get_engagement_summary tool (aggregated metrics) in My_AI_Employee/mcp_servers/twitter_mcp.py
- [X] T062 [US2] Add retry logic and rate limit handling (100 tweets/15min) in My_AI_Employee/mcp_servers/twitter_mcp.py
- [X] T063 [US2] Add graceful degradation with local queue (.twitter_queue.jsonl) in My_AI_Employee/mcp_servers/twitter_mcp.py
- [X] T064 [US2] Add audit logging with credential sanitization in My_AI_Employee/mcp_servers/twitter_mcp.py

### Implementation for User Story 2 - Social Media Skill

- [X] T065 [US2] Create social-media-poster skill in .claude/skills/social-media-poster/ with SKILL.md
- [X] T066 [US2] Implement content adaptation for Facebook (no char limit) in social-media-poster skill
- [X] T067 [US2] Implement content adaptation for Instagram (2200 char limit, hashtags) in social-media-poster skill
- [X] T068 [US2] Implement content adaptation for Twitter (280 char limit, thread creation) in social-media-poster skill
- [X] T069 [US2] Implement cross-platform posting workflow in social-media-poster skill
- [X] T070 [US2] Implement engagement metrics retrieval workflow in social-media-poster skill

**Checkpoint**: User Story 2 should be fully functional - can post to all 3 platforms with appropriate formatting, retrieve engagement
metrics

---

## Phase 5: User Story 3 - Work autonomously on multi-step tasks (Priority: P3)

**Goal**: Enable autonomous multi-step task completion without manual intervention using Ralph Wiggum Loop

**Independent Test**: Start autonomous task with multiple action items, observe AI employee continue working through iterations,  
 verify completion when all items processed

**Dependencies**: Requires US1 and US2 for testing autonomous operation with real actions

### Unit Tests for User Story 3

- [X] T071 [P] [US3] Create unit test for stop hook file movement detection in tests/test_ralph_loop.py
- [X] T072 [P] [US3] Create unit test for stop hook iteration counting in tests/test_ralph_loop.py
- [X] T073 [P] [US3] Create unit test for stop hook max iterations limit in tests/test_ralph_loop.py
- [X] T074 [P] [US3] Create unit test for stop hook state management in tests/test_ralph_loop.py

### Implementation for User Story 3

- [X] T075 [P] [US3] Create stop hook directory .claude/hooks/stop/
- [X] T076 [US3] Implement ralph_wiggum_check.py stop hook with file movement detection in .claude/hooks/stop/
- [X] T077 [US3] Implement check_task_complete() function (checks if file moved to /Done/) in .claude/hooks/stop/ralph_wiggum_check.py
- [X] T078 [US3] Implement get_iteration_count() function (reads .ralph_state.json) in .claude/hooks/stop/ralph_wiggum_check.py
- [X] T079 [US3] Implement increment_iteration() function (updates .ralph_state.json) in .claude/hooks/stop/ralph_wiggum_check.py
- [X] T080 [US3] Implement max iterations check (default: 10) in .claude/hooks/stop/ralph_wiggum_check.py
- [X] T081 [US3] Implement graceful exit on completion or max iterations in .claude/hooks/stop/ralph_wiggum_check.py
- [X] T082 [US3] Make stop hook executable (chmod +x) in .claude/hooks/stop/ralph_wiggum_check.py
- [X] T083 [US3] Create ralph-wiggum-runner skill in .claude/skills/ralph-wiggum-runner/ with SKILL.md
- [X] T084 [US3] Implement autonomous task startup workflow in ralph-wiggum-runner skill
- [X] T085 [US3] Implement task completion detection workflow in ralph-wiggum-runner skill
- [X] T086 [US3] Implement state management and recovery workflow in ralph-wiggum-runner skill
- [X] T087 [US3] Document Ralph loop usage and safety limits in ralph-wiggum-runner skill

**Checkpoint**: User Story 3 should be fully functional - can process multiple action items autonomously until completion or max  
 iterations

---

## Phase 6: User Story 4 - Receive weekly business intelligence (Priority: P4)

**Goal**: Generate automated weekly business briefing every Sunday night with comprehensive data from all sources

**Independent Test**: Manually trigger briefing generation, verify it collects data from Odoo, social media, completed tasks, business
goals, and produces comprehensive report

**Dependencies**: Requires US1 (Odoo data) and US2 (social media data) for complete briefing

### Integration Tests for User Story 4

- [X] T088 [P] [US4] Create integration test for Odoo data aggregation in tests/test_ceo_briefing.py
- [X] T089 [P] [US4] Create integration test for social media metrics aggregation in tests/test_ceo_briefing.py
- [X] T090 [P] [US4] Create integration test for completed tasks analysis in tests/test_ceo_briefing.py
- [X] T091 [P] [US4] Create integration test for bottleneck detection in tests/test_ceo_briefing.py
- [X] T092 [P] [US4] Create integration test for proactive suggestions in tests/test_ceo_briefing.py

### Implementation for User Story 4

- [X] T093 [P] [US4] Create ceo-briefing-generator skill in .claude/skills/ceo-briefing-generator/ with SKILL.md
- [X] T094 [US4] Implement Odoo data aggregation (revenue, expenses, invoices, aged receivables) in ceo-briefing-generator skill
- [X] T095 [US4] Implement social media metrics aggregation (reach, engagement, top posts) in ceo-briefing-generator skill
- [X] T096 [US4] Implement completed tasks analysis (last 7 days from /Done/) in ceo-briefing-generator skill
- [X] T097 [US4] Implement Business_Goals.md parsing and KPI comparison in ceo-briefing-generator skill
- [X] T098 [US4] Implement bottleneck detection (tasks taking longer than expected) in ceo-briefing-generator skill
- [X] T099 [US4] Implement proactive suggestions (unused subscriptions, revenue opportunities) in ceo-briefing-generator skill
- [X] T100 [US4] Implement upcoming deadlines detection in ceo-briefing-generator skill
- [X] T101 [US4] Implement briefing markdown generation with executive summary in ceo-briefing-generator skill
- [X] T102 [US4] Implement briefing file creation in /Briefings/BRIEF-YYYY-Wnn.md in ceo-briefing-generator skill
- [X] T103 [US4] Configure cron job for Sunday 8:00 PM (0 20 \* \* 0) to trigger ceo-briefing-generator skill
- [X] T104 [US4] Test manual briefing generation via claude-code "/ceo-briefing-generator"

**Checkpoint**: User Story 4 should be fully functional - weekly briefing generated automatically with data from all sources

---

## Phase 7: User Story 5 - Operate reliably with automatic recovery (Priority: P5)

**Goal**: Implement comprehensive error recovery with retry logic, component monitoring, and graceful degradation

**Independent Test**: Simulate various error conditions (network timeout, service unavailable, component crash) and verify system  
 recovers appropriately

**Dependencies**: Applies to all components (US1-US4)

### Unit Tests for User Story 5

- [X] T105 [P] [US5] Create unit test for watchdog component detection in tests/test_watchdog.py
- [X] T106 [P] [US5] Create unit test for watchdog auto-restart logic in tests/test_watchdog.py
- [X] T107 [P] [US5] Create unit test for watchdog crash loop detection in tests/test_watchdog.py
- [X] T108 [P] [US5] Create unit test for retry utility exponential backoff in tests/test_retry.py

### Implementation for User Story 5

- [X] T109 [P] [US5] Create watchdog.py in My_AI_Employee/ for component health monitoring
- [X] T110 [US5] Implement component detection (orchestrator, watchers, MCP servers) in My_AI_Employee/watchdog.py
- [X] T111 [US5] Implement health check logic (60-second interval) in My_AI_Employee/watchdog.py
- [X] T112 [US5] Implement auto-restart on crash detection in My_AI_Employee/watchdog.py
- [X] T113 [US5] Implement crash loop detection (3 restarts within 5 minutes) in My_AI_Employee/watchdog.py
- [X] T114 [US5] Implement alert notification on repeated failures in My_AI_Employee/watchdog.py
- [X] T115 [US5] Update ecosystem.config.js to add watchdog process to PM2
- [X] T116 [US5] Verify retry logic with exponential backoff in all MCP servers (already implemented in US1, US2)
- [X] T117 [US5] Verify graceful degradation with queue files in all MCP servers (already implemented in US1, US2)
- [X] T118 [US5] Test network timeout recovery with Odoo MCP server
- [X] T119 [US5] Test service unavailable recovery with social media MCP servers
- [X] T120 [US5] Test component crash recovery with watchdog monitoring

**Checkpoint**: User Story 5 should be fully functional - system recovers from transient errors, restarts crashed components, queues  
 operations when services unavailable

---

## Phase 8: Integration (Update Existing Skills)

**Purpose**: Update Silver tier skills to support Gold tier components

- [X] T121 Update mcp-executor skill to add Odoo MCP routing in .claude/skills/mcp-executor/SKILL.md
- [X] T122 Update mcp-executor skill to add Facebook MCP routing in .claude/skills/mcp-executor/SKILL.md
- [X] T123 Update mcp-executor skill to add Instagram MCP routing in .claude/skills/mcp-executor/SKILL.md
- [X] T124 Update mcp-executor skill to add Twitter MCP routing in .claude/skills/mcp-executor/SKILL.md
- [X] T125 Update needs-action-triage skill to handle Odoo action types (invoice, payment, expense) in
      .claude/skills/needs-action-triage/SKILL.md
- [X] T126 Update needs-action-triage skill to handle social media action types (post, story, tweet) in
      .claude/skills/needs-action-triage/SKILL.md
- [X] T127 Update approval-workflow-manager skill to add financial approval thresholds in
      .claude/skills/approval-workflow-manager/SKILL.md
- [X] T128 Update approval-workflow-manager skill to add social media approval rules in
      .claude/skills/approval-workflow-manager/SKILL.md

**Checkpoint**: All existing skills updated to support Gold tier components

---

## Phase 9: Testing (Unit, Integration, E2E, Regression)

**Purpose**: Comprehensive testing of all Gold tier functionality

### Unit Tests (Already Created in User Story Phases)

- Unit tests for Odoo MCP (T011-T015)
- Unit tests for Facebook MCP (T030-T032)
- Unit tests for Instagram MCP (T033-T035)
- Unit tests for Twitter MCP (T036-T038)
- Unit tests for Ralph loop (T071-T074)
- Unit tests for watchdog (T105-T107)

### Integration Tests

- [X] T129 [P] Create integration test for autonomous invoice creation workflow (file drop → triage → Odoo → approval → send) in
      tests/test_integration_gold.py
- [X] T130 [P] Create integration test for autonomous social media posting workflow (file drop → triage → social → approval → post) in
      tests/test_integration_gold.py
- [X] T131 [P] Create integration test for Ralph loop with multiple action items in tests/test_integration_gold.py
- [X] T132 [P] Create integration test for CEO briefing generation with all data sources in tests/test_integration_gold.py
- [X] T133 [P] Create integration test for error recovery with retry logic in tests/test_integration_gold.py

### End-to-End Tests

- [ ] T134 E2E test for US1: Create invoice, approve, send, verify in Odoo
- [ ] T135 E2E test for US2: Post to all 3 platforms, verify posts published, retrieve metrics
- [ ] T136 E2E test for US3: Start autonomous task, verify continues through iterations, verify completion
- [ ] T137 E2E test for US4: Trigger briefing generation, verify data from all sources, verify output file
- [ ] T138 E2E test for US5: Simulate network timeout, verify retry, simulate crash, verify restart

### Regression Tests

- [ ] T139 Regression test: Verify Bronze tier filesystem watcher still operational
- [ ] T140 Regression test: Verify Silver tier Gmail watcher still operational
- [ ] T141 Regression test: Verify Silver tier WhatsApp watcher still operational
- [ ] T142 Regression test: Verify Silver tier LinkedIn watcher still operational
- [ ] T143 Regression test: Verify Silver tier approval workflow still operational
- [ ] T144 Regression test: Verify Silver tier MCP execution still operational

**Checkpoint**: All tests passing - Gold tier fully functional, Bronze and Silver tiers remain operational

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final polish

- [X] T145 [P] Create gold-tier-validator skill in .claude/skills/gold-tier-validator/ with SKILL.md
- [X] T146 [P] Implement validation checklist for Odoo integration in gold-tier-validator skill
- [X] T147 [P] Implement validation checklist for social media integration in gold-tier-validator skill
- [X] T148 [P] Implement validation checklist for Ralph loop in gold-tier-validator skill
- [X] T149 [P] Implement validation checklist for CEO briefing in gold-tier-validator skill
- [X] T150 [P] Implement validation checklist for error recovery in gold-tier-validator skill
- [X] T151 Run gold-tier-validator skill and verify >95% checks pass
- [X] T152 Update quickstart.md with any missing setup instructions
- [X] T153 Update plan.md with lessons learned and implementation notes
- [X] T154 Create end-to-end demo script for hackathon judges
- [X] T155 Final validation: Run complete workflow (file drop → invoice → approval → send → briefing)

**Checkpoint**: All tests passing - Gold tier fully functional, Bronze and Silver tiers remain operational

**Checkpoint**: Gold tier complete, validated, documented, ready for submission

---

## Dependencies

### Phase Dependencies

Phase 1 (Setup)
↓
Phase 2 (Foundational)
↓
Phase 3 (US1 - Odoo) ←→ Phase 4 (US2 - Social Media) [Can run in parallel]
↓ ↓
Phase 5 (US3 - Ralph Loop) [Depends on US1 + US2 for testing]
↓
Phase 6 (US4 - CEO Briefing) [Depends on US1 + US2 for data]
↓
Phase 7 (US5 - Error Recovery) [Applies to all components]
↓
Phase 8 (Integration)
↓
Phase 9 (Testing)
↓
Phase 10 (Polish)

### User Story Dependencies

- **US1 (Odoo)**: Independent, can start after Foundational
- **US2 (Social Media)**: Independent, can start after Foundational, can run parallel with US1
- **US3 (Ralph Loop)**: Depends on US1 + US2 for testing autonomous operation
- **US4 (CEO Briefing)**: Depends on US1 + US2 for data sources
- **US5 (Error Recovery)**: Applies to all components, implements cross-cutting concerns

---

## Parallel Execution Examples

### Phase 2 (Foundational) - All Parallel

Tasks T006-T009 can all run in parallel (different files, no dependencies):

- T006: retry.py
- T007: credentials.py
- T008: queue_manager.py
- T009: audit_sanitizer.py

### Phase 3 (US1) - Parallel Opportunities

Tasks T011-T015 (unit tests) can all run in parallel (different test files)
Tasks T016-T024 must run sequentially (same file, dependencies)

### Phase 4 (US2) - Parallel Opportunities

Tasks T030-T038 (unit tests) can all run in parallel (different test files)
Tasks T039-T046 (Facebook), T047-T055 (Instagram), T056-T064 (Twitter) can run in parallel (different MCP servers)

### Phase 9 (Testing) - Parallel Opportunities

Tasks T129-T133 (integration tests) can all run in parallel (different test files)
Tasks T134-T138 (E2E tests) should run sequentially (may share resources)
Tasks T139-T144 (regression tests) can all run in parallel (different components)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Gold Tier)

**Phases**: Setup + Foundational + US1 (Odoo) + Integration (mcp-executor update) + Testing
**Tasks**: T001-T029, T121, T129, T134, T139-T144, T151-T155
**Estimated**: ~45 tasks
**Deliverable**: Gold tier with Odoo accounting integration, HITL approval, Bronze/Silver compatibility

### Incremental Delivery

1. **MVP**: Odoo integration (US1) - ~45 tasks
2. **Increment 2**: Add social media (US2) - ~40 tasks
3. **Increment 3**: Add autonomous operation (US3) - ~17 tasks
4. **Increment 4**: Add CEO briefing (US4) - ~17 tasks
5. **Increment 5**: Add error recovery (US5) - ~16 tasks
6. **Final**: Integration + Testing + Polish - ~20 tasks

**Total**: 155 tasks for complete Gold tier implementation

---

## Task Summary

- **Total Tasks**: 155
- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 5 tasks
- **Phase 3 (US1 - Odoo)**: 19 tasks
- **Phase 4 (US2 - Social Media)**: 41 tasks
- **Phase 5 (US3 - Ralph Loop)**: 17 tasks
- **Phase 6 (US4 - CEO Briefing)**: 17 tasks
- **Phase 7 (US5 - Error Recovery)**: 16 tasks
- **Phase 8 (Integration)**: 8 tasks
- **Phase 9 (Testing)**: 16 tasks
- **Phase 10 (Polish)**: 11 tasks

**Parallel Opportunities**: ~60 tasks marked with [P] can run in parallel
**MVP Scope**: ~45 tasks (Setup + Foundational + US1 + Integration + Testing)
**Format Validation**: ✅ All tasks follow checklist format (checkbox, ID, [P]/[Story] labels, file paths)

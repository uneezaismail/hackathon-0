---
id: 0003
title: gold-tier-constitution-update
stage: constitution
date: 2026-01-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 002-silver-ai-employee
user: uneezaismail
command: /sp.constitution
labels: ["gold-tier", "constitution", "governance", "v3.0.0", "autonomous-operation", "odoo-integration", "social-media", "ceo-briefing"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md (updated v2.0.0 → v3.0.0)
tests:
  - N/A (documentation update, no code changes)
---

## Prompt

Update constitution to v3.0.0 for Gold Tier AI Employee with:
                                                                                                                                          New Principles:
  - X. Autonomous Operation: Ralph Wiggum Loop with file movement detection, stop hook pattern, max iterations control
  - XI. Enterprise Accounting: Odoo Community (self-hosted) via JSON-RPC, local-only financial data, weekly reconciliation                - XII. Social Media Automation: Facebook/Instagram/Twitter MCPs with HITL approval, platform-specific content adaptation
  - XIII. Proactive Intelligence: Weekly CEO Briefing (Sunday 8PM) with revenue, bottlenecks, suggestions, deadlines
  - XIV. Resilience: Exponential backoff (1s,2s,4s,8s), graceful degradation, watchdog monitoring, PM2 management

  Tech Stack Additions:
  OdooRPC, facebook-sdk, tweepy, keyring, PM2

  Vault Additions:
  /Briefings/, Business_Goals.md, .ralph_state.json, queue files (.odoo_queue.jsonl, .facebook_queue.jsonl, .instagram_queue.jsonl,
  .twitter_queue.jsonl)

  Security:
  - All financial operations require approval (no auto-approve)
  - All social posts require approval (max 10/day/platform)
  - Credentials in OS keyring, audit logs sanitized

## Response snapshot

Successfully updated constitution from v2.0.0 to v3.0.0 with comprehensive Gold tier requirements.

**Version Change:** 2.0.0 → 3.0.0 (MAJOR bump)

**Rationale:** Gold tier adds 5 new non-negotiable principles (autonomous operation, enterprise accounting, social media automation, proactive intelligence, enhanced resilience), introduces Ralph Wiggum Loop paradigm, adds mandatory Odoo integration, and significantly expands technology stack and security requirements.

**Modified Principles:**
- Principle I: Expanded to "Bronze-First, Silver-Second, Gold-Third Scope"
- Principle II: Added Gold tier vault structure (/Briefings/, Business_Goals.md, queue files)
- Principle V: Added OS keyring requirement for production credentials
- Principle VI: Added 24-hour continuous operation test requirement
- Principle VII: Added financial and social media approval thresholds
- Principle IX: Added queue files and PM2 requirement

**New Principles (X-XIV):**
- X. Autonomous Operation with Ralph Wiggum Loop
- XI. Enterprise Accounting Integration (Odoo Community)
- XII. Multi-Channel Social Media Automation
- XIII. Proactive Business Intelligence (Weekly CEO Briefing)
- XIV. Enhanced Resilience and Process Management

**Technology Stack Additions:**
- OdooRPC (Odoo JSON-RPC client)
- facebook-sdk (Facebook Graph API)
- tweepy (Twitter API v2)
- keyring (OS credential manager)
- PM2 (process management - REQUIRED for Gold tier)

**Security Enhancements:**
- ALL financial operations require approval (no auto-approve threshold)
- ALL social media posts require approval (max 10/day/platform)
- Credentials MUST be stored in OS keyring (not .env) for production
- Audit logs MUST sanitize credentials in queue files

**Artifact Conventions Added:**
- Ralph State File Contract (.ralph_state.json)
- Queue File Contract (*.jsonl)
- CEO Briefing Contract (Briefings/)
- Business Goals Contract (Business_Goals.md)

## Outcome

- ✅ Impact: Constitution updated to v3.0.0 with 5 new Gold tier principles. All Gold tier requirements now formally documented and enforceable. Bronze and Silver tier principles remain valid (additive approach).
- 🧪 Tests: N/A (documentation update). Gold tier testing requirements defined in Principle VI (24-hour continuous operation, queue resilience, end-to-end workflows).
- 📁 Files: 1 file updated (.specify/memory/constitution.md, 507 lines). Sync Impact Report included in HTML comment at top of file.
- 🔁 Next prompts: Continue Phase 3-10 implementation following new constitution. All new code MUST comply with Gold tier principles (autonomous operation, Odoo integration, social media automation, CEO briefing, enhanced resilience).
- 🧠 Reflection: Constitution now provides complete governance for Gold tier. MAJOR version bump justified by 5 new non-negotiable principles and paradigm shift to autonomous operation. All templates validated (no changes needed). Ready to proceed with implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Constitution update completed successfully with comprehensive Gold tier requirements.
- Graders run and results (PASS/FAIL): Constitution structure PASS (all placeholders filled), Sync Impact Report PASS (comprehensive change documentation), Template validation PASS (no updates needed), Version bump rationale PASS (MAJOR bump justified)
- Prompt variant (if applicable): Standard /sp.constitution command with detailed Gold tier requirements
- Next experiment (smallest change to try): Proceed with Phase 3-10 implementation. Monitor if constitution principles are sufficient or require clarification during implementation.

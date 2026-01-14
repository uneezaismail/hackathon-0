---
name: needs-action-triage
description: >
  Triage and plan items in an Obsidian vault's /Needs_Action folder for Hackathon Zero (Bronze tier).
  This skill should be used when the user asks to "process Needs_Action", "triage pending items",
  "create a plan for each item", "turn watcher output into tasks", "update the dashboard after new items",
  "summarize what needs attention", or when Claude detects new action-item markdown files created by a watcher.
  Trigger phrases include: "check /Needs_Action", "process action items", "create Plan.md", "prioritize these",
  "archive to Done", "apply Company_Handbook rules", "process tasks", "check pending tasks",
  "handle Needs_Action items", "complete my tasks", "check what needs to be done", "process pending tasks",
  "check Needs_Action folder", "complete task requests", "move finished work to Done folder",
  "update activity dashboard", or when the user mentions the Needs_Action folder, task processing,
  or wants to see completed work moved to Done.
---

# Needs Action Triage

Convert watcher-created inputs into clear next steps **inside the vault**.

Bronze tier scope:
- Read items in `Needs_Action/`
- Read rules from `Company_Handbook.md`
- Write plans/drafts back into the vault
- Update `Dashboard.md`
- Move processed inputs to `Done/`
- Do **not** perform external actions

## Workflow (Bronze)

1. Locate vault root using `@obsidian-vault-ops` workflow.
2. Scan `Needs_Action/` for pending items.
3. For each item:
   - Read file and parse minimal frontmatter (type/received/status/priority).
   - Read `Company_Handbook.md` and apply processing + priority rules.
   - Produce a plan using `templates/PlanTemplate.md`.
   - If the item is missing required info, include a “Questions” section in the plan.
4. Update `Dashboard.md`:
   - Update counts and append a short recent-activity line per processed item.
5. Archive processed input:
   - Move the action item to `Done/` folder
   - Add `processed` metadata to frontmatter:
     - `processed: [ISO timestamp]`
     - `result: planned`
     - `related_plan: Plans/[plan-filename].md`
     - `status: completed` (change from pending)
   - Mark all checkboxes in "Next Steps" section as completed `[x]`
   - Remove the original from `Needs_Action/`

## Output rules

- Keep plans actionable: checkboxes + concrete next steps.
- Always link back to the original action item path.
- If the item is malformed, do not move it; instead add a dashboard warning and leave it in `Needs_Action/`.

## Resources

- Reference: `references/action-item-schema.md`
- Reference: `references/triage-rules.md`
- Examples: `examples.md`
- Templates: `templates/PlanTemplate.md`, `templates/ActionItemTemplate.md`

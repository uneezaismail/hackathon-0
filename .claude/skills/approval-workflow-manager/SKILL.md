---
name: approval-workflow-manager
description: "WHAT: Manage human-in-the-loop approval requests (list, approve, reject, analytics). WHEN: User says 'check approvals', 'approve payment', 'reject email', 'show pending', 'approval analytics'. Trigger on: approval workflow, HITL tasks, reviewing pending actions."
---

# Approval Workflow Manager - Enhanced HITL System

## Overview

Advanced human-in-the-loop (HITL) approval system for managing sensitive AI actions. Features smart file matching, batch operations, approval analytics, and automated archival.

**Unique Features**:
- 🔍 **Fuzzy File Matching** - Find files by partial name, no need for exact match
- 📦 **Batch Operations** - Approve/reject multiple items at once
- 📊 **Analytics Dashboard** - Track approval rates and identify bottlenecks
- 🗄️ **Auto-Archive** - Automatically archive old approvals
- 📝 **Rich Annotations** - Detailed approval/rejection notes embedded in files
- ⏰ **Age Tracking** - See how long items have been pending

## When to Use

- Reviewing pending actions in the approval queue
- Approving specific sensitive actions (payments, emails to new contacts)
- Rejecting unsafe or incorrect actions
- Analyzing approval workflow performance
- Cleaning up expired approval requests
- Batch processing similar approval requests

## Quick Start

### 1. List Pending Approvals

```bash
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py --action list
```

**Output:**
```
================================================================================
PENDING APPROVALS (3 items)
================================================================================

ID                                  | Type               | Priority   | Age
--------------------------------------------------------------------------------
EMAIL_client_proposal.md            | send_email         | 🔴 high    | 2h 15m
PAYMENT_vendor_invoice.md           | payment            | 🟡 medium  | 1d 3h
SOCIAL_linkedin_post.md             | create_post        | 🟢 low     | 3d 5h

================================================================================
Total: 3 pending approvals
================================================================================
```

### 2. Approve an Action

```bash
# Simple approve
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py \
  --action approve \
  --id EMAIL_client_proposal

# Approve with notes
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py \
  --action approve \
  --id EMAIL_client_proposal \
  --notes "Reviewed with legal team, approved for sending"
```

### 3. Reject an Action

```bash
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py \
  --action reject \
  --id PAYMENT_vendor_invoice \
  --reason "Missing invoice documentation - request invoice before approving"
```

### 4. Batch Approve

```bash
# Approve all items matching pattern
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py \
  --action batch-approve \
  --pattern "SOCIAL_" \
  --notes "Batch approved social media posts for this week"
```

### 5. View Analytics

```bash
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py --action analytics
```

**Output:**
```
============================================================
APPROVAL WORKFLOW ANALYTICS
============================================================

📊 Current Status:
  Pending:     3 (15.0%)
  Approved:   14 (70.0%)
  Rejected:    3 (15.0%)
  Total:      20

⚠️  Old Pending Items (>7 days):
  - PAYMENT_old_invoice.md (12 days old)

============================================================
```

### 6. Archive Old Approvals

```bash
# Archive items older than 30 days (default)
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py --action archive

# Custom threshold
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py \
  --action archive \
  --days 60
```

## Smart File Matching

The approval manager uses intelligent fuzzy matching to find files:

```bash
# All of these work for file "EMAIL_client_proposal_20260212.md":

# Exact name
--id EMAIL_client_proposal_20260212.md

# Without extension
--id EMAIL_client_proposal_20260212

# Partial match
--id client_proposal

# Pattern match
--id EMAIL_client
```

If multiple files match, you'll see a list to choose from.

## Approval Request Format

### File Structure

```markdown
---
type: approval_request
source: gmail|whatsapp|linkedin|filesystem
action_type: send_email|send_message|create_post|payment|system_change
requires_approval: true
approved: false
status: pending
priority: high|medium|low
created_at: 2026-02-12T14:30:00Z
---

# Action Request: Send Email to Client

**Source**: Gmail
**Type**: Send email to external contact
**Priority**: HIGH
**Created**: 2026-02-12 14:30:00

## The Requested Action

Send email to: client@example.com
Subject: Project Proposal
Body: [Full email text]

## Why Approval is Needed

- External communication to client
- Commits to delivery timeline
- Impacts business relationship

## Approval Rules Applied

From Company_Handbook.md:
- External communications require human review
- Commitments > 1 day require approval
- Client-facing emails need tone review

## Recommendation

✅ **APPROVE** - Meets all company guidelines

---
```

### After Approval

The system automatically adds approval metadata:

```markdown
## ✅ APPROVAL GRANTED
- **Approved At**: 2026-02-12T15:00:00Z
- **Approved By**: Human Operator
- **Notes**: Reviewed with legal team, approved for sending
```

### After Rejection

The system automatically adds rejection metadata:

```markdown
## ❌ REJECTION NOTICE
- **Rejected At**: 2026-02-12T15:00:00Z
- **Rejected By**: Human Operator
- **Reason**: Missing invoice documentation - request invoice before approving

### Next Steps
This action has been rejected and will not be executed. Review the rejection reason above and take appropriate corrective action if needed.
```

## Folder Structure

```
My_AI_Employee/AI_Employee_Vault/
├── Pending_Approval/      # Items awaiting human decision
├── Approved/              # Approved items ready for execution
├── Rejected/              # Rejected items (with reasons)
├── Approval_Archive/      # Old approvals (auto-archived)
└── Logs/                  # Audit trail (YYYY-MM-DD.json)
```

## Action Lifecycle

```
1. Watcher/Processor → Creates item in /Needs_Action/
2. Triage Skill → Determines if approval needed
   ├─ YES → Move to /Pending_Approval/
   └─ NO → Move to /Approved/ (auto-approve)
3. Human → Reviews in /Pending_Approval/
   ├─ Approve → Move to /Approved/ (with notes)
   └─ Reject → Move to /Rejected/ (with reason)
4. MCP Executor → Processes /Approved/ items
5. Archive → Old items moved to /Approval_Archive/
```

## Configuration

### Environment Variables

```bash
# Approval expiration (days)
APPROVAL_EXPIRY_DAYS=7

# Vault path
AI_EMPLOYEE_VAULT_PATH=My_AI_Employee/AI_Employee_Vault
```

### Company_Handbook.md Rules

Define approval thresholds in `Company_Handbook.md`:

```markdown
## Approval Thresholds

### Auto-Approve (No Human Review)
- Emails to known contacts (in contact list)
- Recurring payments < $50
- Scheduled social posts (pre-approved content)

### Require Approval (Human Review)
- All external communications to new contacts
- Payments > $50
- Any commitments > 1 day
- Policy changes
- Client-facing communications

### Never Auto-Retry (Always Require Fresh Approval)
- Banking/payment actions
- Legal/compliance actions
- Account deletions
- Contract commitments
```

## Batch Operations

### Approve Multiple Items

```bash
# Approve all social media posts
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py \
  --action batch-approve \
  --pattern "SOCIAL_" \
  --notes "Weekly social media batch approval"

# Approve all emails to specific domain
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py \
  --action batch-approve \
  --pattern "example.com"
```

The system will:
1. Find all matching files
2. Show you the list
3. Ask for confirmation
4. Approve all confirmed items

## Analytics & Reporting

### Approval Rate Tracking

```bash
python3 .claude/skills/approval-workflow-manager/scripts/main_operation.py --action analytics
```

Tracks:
- **Pending count** - Items awaiting decision
- **Approved count** - Items approved and executed
- **Rejected count** - Items rejected with reasons
- **Approval rate** - Percentage of approvals vs rejections
- **Old items** - Items pending > 7 days (needs attention)

### Audit Trail

All actions are logged to `Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-02-12T15:00:00Z",
  "action_type": "approval_management",
  "operation": "approve",
  "target": "EMAIL_client_proposal.md",
  "result": "success",
  "actor": "human_via_approval_manager",
  "metadata": {
    "notes": "Reviewed with legal team"
  }
}
```

## Integration with Other Skills

### With needs-action-triage
- Triage skill determines if approval needed
- Creates approval requests in `/Pending_Approval/`
- This skill manages the approval workflow

### With mcp-executor
- This skill manages approvals
- Approved items moved to `/Approved/`
- MCP executor processes approved items

### With audit-logger
- All approval decisions logged
- Complete audit trail maintained
- Compliance reporting enabled

## Troubleshooting

### File not found
- Use fuzzy matching: `--id partial_name`
- Check spelling of file identifier
- List all pending: `--action list`

### Multiple files match
- Be more specific with identifier
- Use exact filename
- Check output for matching files list

### Approval not executing
- Check if file moved to `/Approved/`
- Verify MCP executor is running
- Check audit logs for errors

### Old pending items
- Run analytics to identify old items
- Review and approve/reject manually
- Consider auto-archive for very old items

## Validation

Run verification to test the system:

```bash
python3 .claude/skills/approval-workflow-manager/scripts/verify_operation.py
```

**Tests:**
- ✓ Directory structure exists
- ✓ Test file creation works
- ✓ List functionality works
- ✓ Approve functionality works
- ✓ Analytics functionality works

## Best Practices

1. **Review Daily** - Check pending approvals at least once per day
2. **Use Notes** - Add approval notes for audit trail
3. **Reject with Reason** - Always provide clear rejection reasons
4. **Batch Similar Items** - Use batch approve for efficiency
5. **Monitor Analytics** - Track approval rates and bottlenecks
6. **Archive Regularly** - Keep vault clean with auto-archive

## Security Considerations

- All approvals require explicit human action
- Rejection reasons are logged for audit
- No auto-approval for sensitive actions
- Complete audit trail maintained
- Files moved (not copied) to prevent duplicates

## Resources

- **scripts/main_operation.py** - Main approval manager (unique implementation)
- **scripts/verify_operation.py** - Verification tests
- **examples.md** - Real-world approval examples
- **references/approval-patterns.md** - Common approval workflows
- **references/approval-rules.md** - Configuration guide

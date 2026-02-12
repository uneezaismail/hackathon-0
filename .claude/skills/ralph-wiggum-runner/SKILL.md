---
name: ralph-wiggum-runner
description: "WHAT: Execute autonomous multi-step tasks until completion using persistent iteration loop. WHEN: User says 'run ralph loop', 'autonomous task', 'complete workflow', 'multi-step task'. Trigger on: complex workflows, batch processing, unattended execution, overnight tasks."
---

# Ralph Wiggum Runner - Enhanced Autonomous Task Executor

## Overview

Autonomous task completion using the Ralph Wiggum Loop pattern - keeps Claude working on multi-step tasks until completion without human intervention. Named after the Simpsons character who famously said "I'm helping!" - Claude keeps helping until the job is done.

**Enhanced Features** (Merged Implementation):
- ✅ State management with Ralph_State/ and Ralph_History/ folders
- ✅ Backup/recovery system for crash resilience
- ✅ HITL integration (pause for approval when needed)
- ✅ Review request creation on max iterations
- ✅ Graceful vs force shutdown options
- ✅ Promise-based AND file-movement completion strategies
- ✅ Comprehensive iteration tracking with audit logging

## When to Use

- Executing multi-step tasks autonomously (5+ steps)
- Running unattended batch operations
- Processing task queues to completion
- Overnight workflow execution
- Weekly scheduled tasks (CEO briefings)
- Any task requiring persistence until completion

## How It Works

1. Creates state file in Ralph_State/ with task prompt
2. Claude works on the task
3. Claude attempts to exit
4. Stop hook checks: Is task complete (file in Done/ or promise output)?
5. **YES** → Allow exit (success)
6. **NO** → Block exit, re-inject prompt, continue
7. Repeat until complete or max iterations reached
8. Move state to Ralph_History/ for archival

## Quick Start

### 1. Start Ralph Loop (Promise-based completion)

```bash
python3 .claude/skills/ralph-wiggum-runner/scripts/main_operation.py \
  --action start \
  --prompt "Process all files in Needs_Action/, move to Done/ when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

### 2. Start Ralph Loop (File-movement completion)

```bash
python3 .claude/skills/ralph-wiggum-runner/scripts/main_operation.py \
  --action start \
  --prompt "Process invoice request and send email" \
  --watch-file "My_AI_Employee/AI_Employee_Vault/Needs_Action/INVOICE_client_a.md" \
  --done-folder "My_AI_Employee/AI_Employee_Vault/Done/" \
  --max-iterations 10
```

### 3. Check Loop Status

```bash
python3 .claude/skills/ralph-wiggum-runner/scripts/main_operation.py --action status
```

### 4. Stop Active Loop

```bash
# Graceful stop (completes current iteration)
python3 .claude/skills/ralph-wiggum-runner/scripts/main_operation.py \
  --action stop --loop-id LOOP_ID

# Force stop (immediate)
python3 .claude/skills/ralph-wiggum-runner/scripts/main_operation.py \
  --action stop --loop-id LOOP_ID --force
```

### 5. View Loop History

```bash
python3 .claude/skills/ralph-wiggum-runner/scripts/main_operation.py \
  --action history --limit 10
```

### 6. List Backups

```bash
python3 .claude/skills/ralph-wiggum-runner/scripts/main_operation.py \
  --action backups --limit 10
```

## Completion Strategies

### Promise-Based (Simple)

Claude outputs `<promise>TASK_COMPLETE</promise>` when done.

**Pros:**
- Faster setup
- Works for any task type
- Claude decides when complete

**Cons:**
- Relies on Claude's judgment
- May complete prematurely or never

**Example:**
```bash
--completion-promise "TASK_COMPLETE"
```

### File-Movement (Robust)

Stop hook detects when task file moves to Done/.

**Pros:**
- More reliable (objective completion)
- Natural part of existing workflow
- No special output required
- Recommended for production

**Cons:**
- Requires file-based task tracking
- Task must involve file movement

**Example:**
```bash
--watch-file "My_AI_Employee/AI_Employee_Vault/Needs_Action/task.md" \
--done-folder "My_AI_Employee/AI_Employee_Vault/Done/"
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-iterations` | 10 | Maximum loop cycles |
| `--timeout` | 3600 | Max seconds per iteration |
| `--check-interval` | 5 | Seconds between completion checks |
| `--force` | false | Force stop (immediate) |

### Environment Variables

```bash
# Ralph Wiggum Loop Configuration
RALPH_MAX_ITERATIONS=10              # Max loop iterations
RALPH_ITERATION_TIMEOUT=3600         # Max seconds per iteration (1 hour)
RALPH_CHECK_INTERVAL=5               # Seconds between checks
AI_EMPLOYEE_VAULT_PATH=My_AI_Employee/AI_Employee_Vault  # Vault path
DRY_RUN=false                        # Enable dry-run mode for testing
```

## State Files

### Active Loops
- **Location**: `My_AI_Employee/AI_Employee_Vault/Ralph_State/`
- **Format**: `RALPH_YYYYMMDD_HHMMSS_hash.json`
- **Purpose**: Track currently running loops

### Completed Loops
- **Location**: `My_AI_Employee/AI_Employee_Vault/Ralph_History/`
- **Format**: `RALPH_YYYYMMDD_HHMMSS_hash.json`
- **Purpose**: Archive completed/stopped loops

### Backups
- **Location**: `.ralph_backups/`
- **Format**: `RALPH_YYYYMMDD_HHMMSS_hash_timestamp.json`
- **Purpose**: Crash recovery and state restoration

### State File Structure

```json
{
  "loop_id": "RALPH_20260212_143000_abc123",
  "prompt": "Process all invoices...",
  "max_iterations": 10,
  "completion_promise": "TASK_COMPLETE",
  "watch_file": "path/to/task.md",
  "done_folder": "My_AI_Employee/AI_Employee_Vault/Done",
  "current_iteration": 3,
  "status": "running",
  "started_at": "2026-02-12T14:30:00Z",
  "last_iteration_at": "2026-02-12T14:35:00Z",
  "iterations": [
    {
      "number": 1,
      "timestamp": "2026-02-12T14:30:05Z",
      "output_preview": "Processing invoice 1...",
      "completed": false
    }
  ],
  "errors": [],
  "paused_for_approval": false,
  "timeout": 3600,
  "check_interval": 5
}
```

## Status Values

- `pending` - Created but not started
- `running` - Actively executing
- `paused_awaiting_approval` - Waiting for HITL approval
- `completed` - Successfully finished
- `max_iterations_reached` - Hit limit without completion
- `stopped_graceful` - Manually stopped (graceful)
- `stopped_force` - Manually stopped (force)

## Safety Features

### Maximum Iteration Limit
Prevents infinite loops (default: 10 iterations)

### Timeout Per Iteration
Prevents hangs (default: 3600 seconds / 1 hour)

### Automatic HITL Pause
Pauses when sensitive actions require approval:
1. Loop detects approval request in `/Pending_Approval/`
2. Sets `paused_for_approval: true`
3. Waits for file to appear in `/Approved/`
4. Automatically resumes after approval

### Review Request on Max Iterations
Creates human review request when max iterations reached:
- Shows iteration history
- Provides recommendations
- Allows manual completion or restart

### Backup System
Automatic backups for crash recovery:
- Initial backup on loop start
- Periodic backups every 3 iterations
- Final backup on stop/completion

### Graceful Shutdown
Completes current iteration before stopping:
```bash
--action stop --loop-id LOOP_ID
```

### Force Shutdown
Immediate stop (may leave iteration incomplete):
```bash
--action stop --loop-id LOOP_ID --force
```

## Integration with Other Skills

### With needs-action-triage
```bash
--prompt "Triage all items in /Needs_Action using needs-action-triage skill"
```

### With mcp-executor
```bash
--prompt "Execute all approved actions in /Approved/ using mcp-executor skill"
```

### With ceo-briefing-generator
```bash
--prompt "Generate weekly CEO briefing using ceo-briefing-generator skill"
```

## Troubleshooting

### Loop never completes
- Check completion promise spelling
- Verify watch file path is correct
- Increase max_iterations
- Check if file is stuck in wrong folder

### Loop completes too early
- Use more specific completion promise
- Switch to file-movement strategy
- Add explicit completion criteria to prompt

### Loop paused for approval
- Check `/Pending_Approval/` folder
- Review and approve/reject the request
- Loop will auto-resume after approval

### Max iterations reached
- Review request created in `/Pending_Approval/`
- Check iteration history for progress
- Manually complete remaining work or restart with higher limit

### Memory issues
- Reduce max_iterations
- Clear Ralph_History periodically
- Check for large output in iterations

## Validation

Run verification script to check setup:

```bash
python3 .claude/skills/ralph-wiggum-runner/scripts/verify_operation.py
```

Checks:
- [ ] Ralph State directory exists
- [ ] Ralph History directory exists
- [ ] Backup directory exists
- [ ] Loop tracking functional
- [ ] State file creation works
- [ ] Audit logging works

## Resources

- **scripts/main_operation.py** - Main loop executor (merged implementation)
- **scripts/verify_operation.py** - Validation script
- **REFERENCE.md** - Detailed technical documentation
- **references/ralph-pattern.md** - Pattern explanation
- **references/stop-hook-implementation.md** - Stop hook code and API

See [REFERENCE.md](./REFERENCE.md) for detailed configuration and advanced usage.

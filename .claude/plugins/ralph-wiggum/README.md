# Ralph Wiggum Plugin

Official Claude Code plugin for autonomous task completion with Gold Tier file-movement detection.

## Overview

The Ralph Wiggum plugin implements a persistent execution loop that keeps Claude Code working on a task until completion. It intercepts exit attempts and re-injects the prompt, allowing Claude to see its previous work and continue iterating.

## Features

- **Hybrid Completion Detection**
  - Promise-based: Detects `<promise>TASK_COMPLETE</promise>` in output
  - File-movement: Detects when task files move from `Needs_Action/` to `Done/` (Gold Tier)

- **HITL Integration**
  - Automatic pause when approval needed
  - Human review requests on max iterations
  - Approval timeout handling

- **State Management**
  - State file: `.claude/ralph-loop.local.md` (official format)
  - Automatic backups in `.ralph_backups/`
  - History archival in `AI_Employee_Vault/Ralph_History/`

- **Error Handling**
  - Graceful degradation on errors
  - Retry logic for transient failures
  - Max consecutive error tracking

## Usage

### Via Skill (Recommended)

```bash
# Start autonomous task processing
/ralph-wiggum-runner --action start --task "Process all items in Needs_Action"

# Check status
/ralph-wiggum-runner --action status

# Stop loop
/ralph-wiggum-runner --action stop
```

### Manual State File Creation

Create `.claude/ralph-loop.local.md`:

```markdown
---
iteration: 1
max_iterations: 10
completion_promise: "TASK_COMPLETE"
watch_file: "My_AI_Employee/AI_Employee_Vault/Needs_Action/EMAIL_12345.md"
started_at: "2026-02-13T00:00:00Z"
---

Process all pending action items in Needs_Action folder.
Move completed items to Done folder.
Update Dashboard.md with progress.
```

Then run Claude Code normally. The stop hook will intercept exit attempts.

## Completion Strategies

### 1. Promise-Based (Simple)

Claude outputs a completion promise:

```markdown
All tasks completed successfully.

<promise>TASK_COMPLETE</promise>
```

### 2. File-Movement (Gold Tier)

Task file moves from `Needs_Action/` to `Done/`:

```bash
# Before
My_AI_Employee/AI_Employee_Vault/Needs_Action/EMAIL_12345.md

# After (task complete)
My_AI_Employee/AI_Employee_Vault/Done/EMAIL_12345.md
```

### 3. Hybrid (Default)

Completes on either promise OR file movement.

## Configuration

Edit `plugin.json` to customize:

```json
{
  "defaults": {
    "max_iterations": 10,
    "completion_strategy": "hybrid"
  },
  "hitl_integration": {
    "pause_on_approval_needed": true,
    "create_review_on_max_iterations": true
  }
}
```

## State File Format

The state file uses YAML frontmatter + Markdown body:

```markdown
---
iteration: 3
max_iterations: 10
completion_promise: "TASK_COMPLETE"
watch_file: "path/to/task.md"
started_at: "2026-02-13T00:00:00Z"
last_iteration_at: "2026-02-13T00:15:00Z"
status: "running"
---

Your task description here.
This is what Claude will work on.
```

## Stop Hook Behavior

The stop hook (`stop-hook.sh`) runs when Claude tries to exit:

1. **Check for active loop**: If no `.claude/ralph-loop.local.md`, allow exit
2. **Check completion**: Test promise and file-movement strategies
3. **If complete**: Archive state, allow exit
4. **If max iterations**: Create review request, allow exit
5. **If incomplete**: Increment iteration, block exit (Claude continues)

## Logging

All loop activity is logged to:
- `My_AI_Employee/AI_Employee_Vault/Logs/ralph-loop.log`

Log format:
```
[2026-02-13T00:00:00Z] Ralph Wiggum Stop Hook - Checking completion
[2026-02-13T00:00:00Z] Current state: iteration=3/10
[2026-02-13T00:00:00Z] 🔄 Task incomplete - continuing to iteration 4/10
```

## Integration with AI Employee

The Ralph Wiggum plugin is designed for Gold Tier autonomous operation:

```
1. Watcher detects input → Creates file in Needs_Action/
2. Ralph loop starts → Claude processes task
3. Claude moves file to Done/ → Loop detects completion
4. Loop exits → Ready for next task
```

## Troubleshooting

### Loop won't stop

Check if completion criteria are met:
- Promise: Is `<promise>TASK_COMPLETE</promise>` in output?
- File-movement: Did file move to `Done/`?

### Max iterations reached

Review request created in `Pending_Approval/`. Options:
1. Manually complete the task
2. Restart with higher max_iterations
3. Break task into smaller steps

### State file corruption

Backups are in `.ralph_backups/`. Restore with:
```bash
cp .ralph_backups/ralph-loop_TIMESTAMP.md .claude/ralph-loop.local.md
```

## Architecture

```
┌─────────────────────────────────────────┐
│ Claude Code Session                     │
│                                         │
│  1. Works on task                       │
│  2. Tries to exit                       │
│     ↓                                   │
│  ┌──────────────────────────────────┐  │
│  │ Stop Hook (stop-hook.sh)         │  │
│  │                                  │  │
│  │ • Read .claude/ralph-loop.local.md│ │
│  │ • Check completion (promise/file)│  │
│  │ • Increment iteration            │  │
│  │ • Return exit code               │  │
│  └──────────────────────────────────┘  │
│     ↓                                   │
│  3. Exit blocked (code 1)               │
│  4. Prompt re-injected                  │
│  5. Loop continues                      │
└─────────────────────────────────────────┘
```

## References

- Official Claude Code Plugin: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- HACKATHON-ZERO.md: Section 2D - Persistence (The "Ralph Wiggum" Loop)
- Gold Tier Requirements: Autonomous multi-step task completion

## License

Part of the Personal AI Employee Hackathon Zero project.

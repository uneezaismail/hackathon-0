# Ralph Wiggum Loop Pattern

## Pattern Overview

The Ralph Wiggum Loop is a persistence pattern that enables Claude Code to work autonomously on multi-step tasks until completion. It uses a **stop hook** to intercept Claude's exit and re-inject the prompt.

## Architecture Components

### 1. State File

Location: `/Active_Tasks/ralph_state_[timestamp].json`

Structure:
```json
{
  "task": "Process all files in /Needs_Action",
  "task_file": "20260127_143000_task.md",
  "iteration": 3,
  "max_iterations": 10,
  "started": "2026-01-27T14:30:00",
  "last_iteration": "2026-01-27T14:35:00",
  "completion_criteria": "file_movement",
  "target_folder": "Done"
}
```

### 2. Stop Hook

Location: `.claude/hooks/stop/ralph_wiggum_check.py`

Responsibilities:
- Intercept Claude's exit attempt
- Check completion criteria (file in /Done/)
- Re-inject prompt if incomplete
- Update state file with iteration count
- Allow exit if complete or max iterations reached

### 3. Orchestrator

Location: `scripts/start_ralph_loop.py`

Responsibilities:
- Create state file with task details
- Launch Claude Code with initial prompt
- Monitor loop progress
- Clean up state file on completion

## Completion Strategies

### File Movement Detection (Gold Tier)

**How it works:**
- Stop hook checks if task file moved to `/Done/` folder
- More reliable than promise-based completion
- Completion is natural part of workflow

**Advantages:**
- No special syntax required
- Works even if Claude forgets to signal completion
- Integrated with existing workflow

**Implementation:**
```python
def check_completion():
    task_file = state.get('task_file')
    done_dir = Path(os.getenv('VAULT_ROOT')) / 'Done'

    if task_file and (done_dir / task_file).exists():
        return True  # Task complete

    return False  # Continue loop
```

### Promise-Based Detection (Bronze/Silver Tier)

**How it works:**
- Claude outputs `<promise>TASK_COMPLETE</promise>`
- Stop hook parses Claude's output for promise tag

**Advantages:**
- Simple to implement
- Explicit completion signal

**Disadvantages:**
- Claude must remember to output promise
- Can fail if Claude forgets or output is truncated

## Workflow

```
1. User/Cron triggers task
   ↓
2. Orchestrator creates state file
   ↓
3. Orchestrator launches Claude with prompt
   ↓
4. Claude processes task (iteration 1)
   ↓
5. Claude tries to exit
   ↓
6. Stop hook intercepts exit
   ↓
7. Stop hook checks: File in /Done?
   ├─ YES → Clean up state file, allow exit
   └─ NO  → Update state file, re-inject prompt
   ↓
8. Claude continues (iteration 2)
   ↓
9. Repeat steps 5-8 until complete or max iterations
```

## Safety Mechanisms

### Max Iterations

Prevents infinite loops:
- Default: 10 iterations
- Configurable via `--max-iterations` flag
- After max: Graceful exit with state saved

### Timeouts

Prevents runaway processes:
- **Per-iteration timeout**: Max time for single iteration (default: 5 minutes)
- **Total timeout**: Max time for entire loop (default: 1 hour)
- On timeout: Graceful shutdown, save progress, alert human

### State Persistence

Enables recovery from crashes:
- State file saved after each iteration
- Contains: prompt, iteration count, start time, completion criteria
- If Claude crashes: Can resume from last saved state

### Graceful Shutdown

Handles interruptions cleanly:
- SIGINT (Ctrl+C): Complete current iteration, then exit
- SIGTERM: Immediate graceful shutdown
- State file cleanup on exit

## Integration Patterns

### With needs-action-triage

```bash
/ralph-loop "Triage all items in /Needs_Action using @needs-action-triage"
```

Loop continues until `/Needs_Action/` is empty.

### With mcp-executor

```bash
/ralph-loop "Execute all approved actions in /Approved/ using @mcp-executor"
```

Loop continues until `/Approved/` is empty.

### With ceo-briefing-generator

```bash
/ralph-loop "Generate weekly CEO briefing using @ceo-briefing-generator"
```

Loop completes when briefing file moves to `/Done/`.

## Monitoring

### Check Loop Status

```bash
python scripts/ralph_status.py
```

Output:
```
Ralph Loop Status: ACTIVE
Task: Process all files in /Needs_Action
Iteration: 3/10
Started: 2026-01-27 14:30:00
Last iteration: 2026-01-27 14:35:00
Elapsed: 5 minutes
```

### View Loop Logs

```bash
tail -f logs/ralph_loop.log
```

### Debug State File

```bash
cat Active_Tasks/ralph_state_*.json
```

## Troubleshooting

### Loop Not Starting

**Symptom**: Ralph loop command runs but Claude exits immediately

**Causes**:
- Stop hook not installed
- State file not created
- Permissions issue

**Fix**:
```bash
# Check stop hook exists
ls -la .claude/hooks/stop/ralph_wiggum_check.py

# Reinstall stop hook
python scripts/install_stop_hook.py
```

### Loop Running Forever

**Symptom**: Loop exceeds max iterations, doesn't exit

**Causes**:
- Task file never moves to /Done/
- Completion criteria not met
- Bug in stop hook logic

**Fix**:
```bash
# Force stop the loop
python scripts/stop_ralph_loop.py --force

# Check what's blocking completion
ls -la AI_Employee_Vault/Needs_Action/
ls -la AI_Employee_Vault/Done/
```

### Loop Exits Too Early

**Symptom**: Loop exits before task is complete

**Causes**:
- Completion criteria too loose
- Stop hook detecting false positive
- Max iterations too low

**Fix**:
```bash
# Increase max iterations
/ralph-loop "Task description" --max-iterations 20

# Review completion criteria in Company_Handbook.md
```

## Reference Implementation

See: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

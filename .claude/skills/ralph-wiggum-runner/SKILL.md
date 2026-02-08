---
name: ralph-wiggum-runner
description: >
  Autonomous task completion using the Ralph Wiggum Loop pattern. Implements a stop hook that
  intercepts Claude's exit and re-injects the prompt until the task is complete. Uses file movement
  detection (task file moves to /Done/) as the completion signal for Gold tier autonomous operation.
  Use when: (1) Starting autonomous task processing, (2) Running multi-step workflows that require
  persistence, (3) Processing batches of action items until completion, (4) Implementing "set it and
  forget it" business automation, (5) Weekly scheduled tasks like CEO briefings. Trigger phrases:
  "start ralph loop", "run autonomously", "process until complete", "autonomous mode", "keep working
  until done", "ralph wiggum loop", "process all pending items".
---

# Ralph Wiggum Runner

Autonomous task completion using the Ralph Wiggum Loop pattern - keeps Claude working on multi-step tasks until completion without human intervention.

## Overview

Claude Code runs in interactive mode and exits after processing a prompt. The Ralph Wiggum Loop uses a **stop hook** to intercept Claude's exit and re-inject the prompt until the task is complete. Named after the Simpsons character who famously said "I'm helping!" - Claude keeps helping until the job is done.

**Gold Tier Strategy**: File movement detection (advanced) - Stop hook monitors vault state, checking if task file moved to `/Done/`. More reliable than promise-based completion.

## How It Works

1. Orchestrator creates state file with task prompt
2. Claude works on task (processes action items, creates plans, executes actions)
3. Claude tries to exit
4. Stop hook intercepts and checks: Is task file in `/Done/`?
5. **If YES** → Allow exit (task complete)
6. **If NO** → Block exit, re-inject prompt, show Claude its previous output (loop continues)
7. Repeat until complete or max iterations reached

## Quick Start

### Starting a Ralph Loop

```bash
# Start autonomous processing
python scripts/start_ralph_loop.py \
  --task "Process all files in /Needs_Action, move to /Done when complete" \
  --max-iterations 10

# Or invoke directly in Claude Code
/ralph-loop "Process all pending action items until complete"
```

### Monitoring Progress

```bash
# Check loop status
python scripts/ralph_status.py

# View loop logs
tail -f logs/ralph_loop.log

# Check current iteration
cat Active_Tasks/ralph_state_*.json
```

### Stopping a Loop

```bash
# Graceful stop (completes current iteration)
python scripts/stop_ralph_loop.py --graceful

# Force stop (immediate)
python scripts/stop_ralph_loop.py --force
```

## Configuration

### In Company_Handbook.md

```markdown
## Ralph Wiggum Loop Configuration

### Autonomous Processing Rules
- Max iterations: 10 (prevent infinite loops)
- Check interval: 5 seconds (how often to check /Done/)
- Timeout per iteration: 300 seconds (5 minutes)
- Total timeout: 3600 seconds (1 hour)

### Completion Criteria
- Primary: Task file appears in /Done/ folder
- Secondary: All items in /Needs_Action/ processed
- Fallback: Max iterations reached
```

### In .env

```bash
# Ralph Wiggum Loop
RALPH_MAX_ITERATIONS=10              # Max loop iterations
RALPH_CHECK_INTERVAL=5               # Seconds between /Done/ checks
RALPH_ITERATION_TIMEOUT=300          # Max seconds per iteration
RALPH_TOTAL_TIMEOUT=3600             # Max total loop time
RALPH_STATE_DIR=Active_Tasks         # Where to store state files
```

## Usage Examples

### Process All Action Items

```bash
/ralph-loop "Process all files in /Needs_Action until none remain"
```

Claude will:
1. Read all files in `/Needs_Action/`
2. Create plans for each item
3. Move processed items to `/Done/`
4. Continue until `/Needs_Action/` is empty

### Weekly CEO Briefing (Scheduled)

```bash
# Cron job triggers Ralph loop
0 20 * * 0 python scripts/start_ralph_loop.py \
  --task "Generate weekly CEO briefing from Done/ folder and Odoo data" \
  --max-iterations 5
```

### Batch Email Processing

```bash
/ralph-loop "Execute all approved email actions in /Approved/ until complete"
```

## Integration with Other Skills

### With needs-action-triage

```bash
/ralph-loop "Triage all items in /Needs_Action using @needs-action-triage"
```

### With mcp-executor

```bash
/ralph-loop "Execute all approved actions in /Approved/ using @mcp-executor"
```

### With ceo-briefing-generator

```bash
/ralph-loop "Generate weekly CEO briefing using @ceo-briefing-generator"
```

## Safety Features

- **Max iterations**: Prevents infinite loops (default: 10)
- **Timeouts**: Per-iteration (5 min) and total (1 hour)
- **State persistence**: Enables recovery from crashes
- **Graceful shutdown**: Handles interruptions cleanly

## Resources

- **scripts/start_ralph_loop.py** - Start autonomous loop
- **scripts/ralph_status.py** - Monitor loop progress
- **scripts/stop_ralph_loop.py** - Stop running loop
- **scripts/install_stop_hook.py** - Install stop hook
- **references/ralph-pattern.md** - Detailed pattern explanation
- **references/stop-hook-implementation.md** - Stop hook code and API

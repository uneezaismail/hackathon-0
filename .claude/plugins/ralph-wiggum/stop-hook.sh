#!/bin/bash
# Ralph Wiggum Stop Hook - Official Claude Code Pattern + Gold Tier Enhancements
#
# This hook intercepts Claude Code's exit attempts and decides whether to:
# 1. Allow exit (task complete)
# 2. Block exit and continue loop (task incomplete)
#
# Completion Detection (Hybrid Strategy):
# - Promise-based: Output contains <promise>TASK_COMPLETE</promise>
# - File-movement: Task file moved from Needs_Action/ to Done/ (Gold Tier)
#
# State File: .claude/ralph-loop.local.md (official Claude Code format)
#
# Exit Codes:
# 0 = Allow exit (task complete or max iterations reached)
# 1 = Block exit and continue loop

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

STATE_FILE=".claude/ralph-loop.local.md"
VAULT_DIR="My_AI_Employee/AI_Employee_Vault"
NEEDS_ACTION_DIR="${VAULT_DIR}/Needs_Action"
DONE_DIR="${VAULT_DIR}/Done"
LOG_FILE="${VAULT_DIR}/Logs/ralph-loop.log"
HISTORY_DIR="${VAULT_DIR}/Ralph_History"
BACKUP_DIR=".ralph_backups"

# Ensure directories exist
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$HISTORY_DIR"
mkdir -p "$BACKUP_DIR"

# ============================================================================
# LOGGING
# ============================================================================

log() {
    echo "[$(date -Iseconds)] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date -Iseconds)] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

parse_frontmatter() {
    local key="$1"
    local value

    if [ ! -f "$STATE_FILE" ]; then
        echo ""
        return
    fi

    # Extract value from YAML frontmatter
    value=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE" | \
            grep "^${key}:" | \
            sed "s/^${key}: *//" | \
            sed 's/^"\(.*\)"$/\1/')

    echo "$value"
}

update_frontmatter() {
    local key="$1"
    local value="$2"

    if [ ! -f "$STATE_FILE" ]; then
        return 1
    fi

    # Update value in frontmatter
    sed -i "/^${key}:/c\\${key}: ${value}" "$STATE_FILE"
}

increment_iteration() {
    local current
    current=$(parse_frontmatter "iteration")
    current=${current:-0}

    local new_iteration=$((current + 1))
    update_frontmatter "iteration" "$new_iteration"
    update_frontmatter "last_iteration_at" "\"$(date -Iseconds)\""

    echo "$new_iteration"
}

backup_state() {
    if [ -f "$STATE_FILE" ]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        local backup_file="${BACKUP_DIR}/ralph-loop_${timestamp}.md"
        cp "$STATE_FILE" "$backup_file"
        log "State backed up to: $backup_file"
    fi
}

archive_state() {
    if [ -f "$STATE_FILE" ]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        local archive_file="${HISTORY_DIR}/ralph-loop_${timestamp}.md"
        mv "$STATE_FILE" "$archive_file"
        log "State archived to: $archive_file"
    fi
}

# ============================================================================
# COMPLETION DETECTION
# ============================================================================

check_promise_completion() {
    local promise="$1"
    local transcript_path="$2"

    if [ -z "$promise" ]; then
        return 1
    fi

    if [ -z "$transcript_path" ] || [ ! -f "$transcript_path" ]; then
        # Fallback: check stdin/last output
        return 1
    fi

    # Extract last assistant output from transcript
    local last_output
    if command -v jq &> /dev/null; then
        last_output=$(grep '"role":"assistant"' "$transcript_path" 2>/dev/null | tail -1 | \
                     jq -r '.message.content | map(select(.type == "text")) | map(.text) | join("\n")' 2>/dev/null || echo "")
    else
        # Fallback without jq
        last_output=$(grep -o '"text":"[^"]*"' "$transcript_path" 2>/dev/null | tail -1 | cut -d'"' -f4 || echo "")
    fi

    # Check for promise tag
    if echo "$last_output" | grep -q "<promise>${promise}</promise>"; then
        log "✅ Promise completion detected: <promise>${promise}</promise>"
        return 0
    fi

    # Check for promise text (without tags)
    if echo "$last_output" | grep -q "${promise}"; then
        log "✅ Promise completion detected: ${promise}"
        return 0
    fi

    return 1
}

check_file_movement_completion() {
    local watch_file="$1"

    if [ -z "$watch_file" ]; then
        # No specific file to watch, check if Needs_Action is empty
        if [ -d "$NEEDS_ACTION_DIR" ]; then
            local count=$(find "$NEEDS_ACTION_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
            if [ "$count" -eq 0 ]; then
                log "✅ File-movement completion: Needs_Action/ is empty"
                return 0
            fi
        fi
        return 1
    fi

    local filename=$(basename "$watch_file")
    local done_path="${DONE_DIR}/${filename}"

    # Check if file moved to Done/
    if [ -f "$done_path" ]; then
        log "✅ File-movement completion: ${filename} found in Done/"
        return 0
    fi

    # Check if file no longer in Needs_Action/
    if [ ! -f "$watch_file" ]; then
        log "✅ File-movement completion: ${filename} no longer in Needs_Action/"
        return 0
    fi

    return 1
}

# ============================================================================
# HUMAN REVIEW REQUEST
# ============================================================================

create_review_request() {
    local iteration="$1"
    local max_iterations="$2"
    local prompt="$3"

    local review_file="${VAULT_DIR}/Pending_Approval/REVIEW_ralph_loop_$(date +%Y%m%d_%H%M%S).md"
    mkdir -p "$(dirname "$review_file")"

    cat > "$review_file" << EOF
---
type: review_request
source: ralph_wiggum_loop
action_type: loop_incomplete
requires_approval: true
approved: false
status: pending
priority: high
created_at: $(date -Iseconds)
---

# Ralph Wiggum Loop - Human Review Required

**Status**: Max iterations reached without completion

## Loop Details

- **Iterations Completed**: ${iteration}/${max_iterations}
- **Started**: $(parse_frontmatter "started_at")
- **Last Iteration**: $(date -Iseconds)

## Original Task

${prompt}

## Why Review is Needed

The Ralph Wiggum loop reached the maximum iteration limit without detecting task completion. This could mean:

1. The task is more complex than expected
2. The completion criteria need adjustment
3. There's a blocker preventing completion
4. The task needs to be broken into smaller steps

## Action Required

Please review the loop progress and either:

1. ✅ **Manually complete** the remaining work
2. 🔄 **Restart loop** with modified parameters (increase max_iterations)
3. 📝 **Adjust task** and create new action items
4. ❌ **Mark as abandoned** if no longer needed

## Next Steps

To restart the loop with more iterations:
\`\`\`bash
/ralph-wiggum-runner --action start --task "your task" --max-iterations 20
\`\`\`

---
*Generated by Ralph Wiggum Stop Hook*
EOF

    log "📋 Created human review request: $review_file"
}

# ============================================================================
# MAIN HOOK LOGIC
# ============================================================================

main() {
    log "========================================="
    log "Ralph Wiggum Stop Hook - Checking completion"
    log "========================================="

    # Quick exit if no active loop
    if [ ! -f "$STATE_FILE" ]; then
        log "No active Ralph loop found - allowing exit"
        exit 0
    fi

    # Backup state before processing
    backup_state

    # Parse state
    local iteration=$(parse_frontmatter "iteration")
    local max_iterations=$(parse_frontmatter "max_iterations")
    local completion_promise=$(parse_frontmatter "completion_promise")
    local watch_file=$(parse_frontmatter "watch_file")
    local started_at=$(parse_frontmatter "started_at")

    # Defaults
    iteration=${iteration:-0}
    max_iterations=${max_iterations:-10}

    log "Current state: iteration=${iteration}/${max_iterations}"
    log "Completion promise: ${completion_promise:-none}"
    log "Watch file: ${watch_file:-none}"

    # Get transcript path from hook input
    local transcript_path=""
    if [ -n "${HOOK_INPUT:-}" ]; then
        if command -v jq &> /dev/null; then
            transcript_path=$(echo "$HOOK_INPUT" | jq -r '.transcript_path' 2>/dev/null || echo "")
        fi
    fi

    # Check for completion
    local completed=false

    # Strategy 1: Promise-based completion
    if [ -n "$completion_promise" ]; then
        if check_promise_completion "$completion_promise" "$transcript_path"; then
            completed=true
        fi
    fi

    # Strategy 2: File-movement completion (Gold Tier)
    if [ "$completed" = false ]; then
        if check_file_movement_completion "$watch_file"; then
            completed=true
        fi
    fi

    # If completed, allow exit
    if [ "$completed" = true ]; then
        log "✅ Task completed successfully after ${iteration} iterations"
        update_frontmatter "status" "\"completed\""
        update_frontmatter "completed_at" "\"$(date -Iseconds)\""
        archive_state

        echo ""
        echo "✅ Ralph Wiggum Loop: Task complete after ${iteration} iterations"
        echo ""

        exit 0
    fi

    # Check if max iterations reached
    if [ "$iteration" -ge "$max_iterations" ]; then
        log "⚠️  Max iterations (${max_iterations}) reached without completion"
        update_frontmatter "status" "\"max_iterations_reached\""

        # Extract prompt from state file
        local prompt=$(sed -n '/^---$/,/^---$/!p' "$STATE_FILE" | sed '/^$/d')

        # Create human review request
        create_review_request "$iteration" "$max_iterations" "$prompt"

        archive_state

        echo ""
        echo "⚠️  Ralph Wiggum Loop: Max iterations (${max_iterations}) reached"
        echo "📋 Human review request created in Pending_Approval/"
        echo ""

        exit 0
    fi

    # Task not complete - increment iteration and continue
    local new_iteration=$(increment_iteration)

    log "🔄 Task incomplete - continuing to iteration ${new_iteration}/${max_iterations}"

    echo ""
    echo "🔄 Ralph Wiggum Loop: Continuing to iteration ${new_iteration}/${max_iterations}"
    echo "   Checking for completion..."
    echo ""

    # Block exit - Claude will continue working
    exit 1
}

# ============================================================================
# ENTRY POINT
# ============================================================================

main "$@"

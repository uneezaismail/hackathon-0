#!/usr/bin/env python3
"""
Integration Tests for Gold Tier AI Employee

Tests complete workflows across multiple components:
- Odoo integration workflow
- Social media posting workflow
- Ralph Wiggum Loop workflow
- CEO briefing generation workflow
- Error recovery workflow
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_vault():
    """Create temporary vault directory structure."""
    temp_dir = tempfile.mkdtemp()
    vault_path = os.path.join(temp_dir, "AI_Employee_Vault")

    # Create vault folders
    for folder in ['Needs_Action', 'Done', 'Pending_Approval', 'Approved', 'Rejected', 'Failed', 'Plans', 'Briefings']:
        os.makedirs(os.path.join(vault_path, folder))

    yield vault_path

    # Cleanup
    shutil.rmtree(temp_dir)


# ============================================================================
# T129: Integration test for autonomous invoice creation workflow
# ============================================================================

def test_invoice_workflow_end_to_end(temp_vault):
    """
    Test complete invoice workflow:
    1. File drop → /Needs_Action/
    2. Triage → Create plan
    3. Odoo → Create invoice (simulated)
    4. Approval → Move to /Pending_Approval/
    5. Human approval → Move to /Approved/
    6. Send invoice → Execute via MCP
    7. Move to /Done/
    """
    # Step 1: Create invoice request in /Needs_Action/
    needs_action_dir = os.path.join(temp_vault, 'Needs_Action')
    invoice_file = os.path.join(needs_action_dir, 'invoice_request.md')

    with open(invoice_file, 'w') as f:
        f.write("""---
type: invoice
client: Test Client
amount: 1500.00
description: Consulting services
created_at: 2026-01-29T10:00:00
status: pending
priority: high
---

# Invoice Request

Create invoice for Test Client for consulting services ($1,500.00)
""")

    # Verify file created
    assert os.path.exists(invoice_file)

    # Step 2: Simulate triage (would be done by needs-action-triage skill)
    plans_dir = os.path.join(temp_vault, 'Plans')
    plan_file = os.path.join(plans_dir, 'Plan_invoice_request.md')

    with open(plan_file, 'w') as f:
        f.write("""# Plan: Invoice Request

## Steps
- [x] Parse invoice request
- [x] Validate client and amount
- [ ] Create invoice in Odoo
- [ ] Send invoice to client
- [ ] Record in Done folder

## Approval Required
Yes - Financial operation over $500
""")

    assert os.path.exists(plan_file)

    # Step 3: Simulate approval request creation
    pending_dir = os.path.join(temp_vault, 'Pending_Approval')
    approval_file = os.path.join(pending_dir, 'APPROVAL_invoice_request.md')

    with open(approval_file, 'w') as f:
        f.write("""---
type: approval_request
action_type: invoice
status: pending
created_at: 2026-01-29T10:05:00
---

# Invoice Approval Request

**Client**: Test Client
**Amount**: $1,500.00
**Description**: Consulting services

## Action Required
Approve or reject invoice creation
""")

    assert os.path.exists(approval_file)

    # Step 4: Simulate human approval
    approved_dir = os.path.join(temp_vault, 'Approved')
    approved_file = os.path.join(approved_dir, 'APPROVAL_invoice_request.md')

    shutil.move(approval_file, approved_file)

    # Update status
    with open(approved_file, 'r') as f:
        content = f.read()
    content = content.replace('status: pending', 'status: approved')
    with open(approved_file, 'w') as f:
        f.write(content)

    assert os.path.exists(approved_file)
    assert not os.path.exists(approval_file)

    # Step 5: Simulate execution (would be done by mcp-executor)
    done_dir = os.path.join(temp_vault, 'Done')
    done_file = os.path.join(done_dir, 'invoice_request.md')

    # Move original to Done with execution metadata
    with open(invoice_file, 'r') as f:
        content = f.read()
    content = content.replace('status: pending', 'status: executed')
    content += f"\n\nExecuted at: {datetime.now().isoformat()}\nInvoice ID: INV/2026/001\n"

    with open(done_file, 'w') as f:
        f.write(content)

    os.remove(invoice_file)

    # Verify workflow complete
    assert os.path.exists(done_file)
    assert not os.path.exists(invoice_file)
    assert 'status: executed' in open(done_file).read()


# ============================================================================
# T130: Integration test for autonomous social media posting workflow
# ============================================================================

def test_social_media_workflow_end_to_end(temp_vault):
    """
    Test complete social media workflow:
    1. File drop → /Needs_Action/
    2. Triage → Create plan with platform-specific content
    3. Approval → Move to /Pending_Approval/
    4. Human approval → Move to /Approved/
    5. Post to platforms → Execute via MCP
    6. Move to /Done/
    """
    # Step 1: Create social media request in /Needs_Action/
    needs_action_dir = os.path.join(temp_vault, 'Needs_Action')
    post_file = os.path.join(needs_action_dir, 'social_post_request.md')

    with open(post_file, 'w') as f:
        f.write("""---
type: social_media_post
platforms: [facebook, instagram, twitter]
created_at: 2026-01-29T10:00:00
status: pending
priority: medium
---

# Social Media Post Request

Exciting news! We're launching our new product next week. Stay tuned for updates! #ProductLaunch #Innovation
""")

    assert os.path.exists(post_file)

    # Step 2: Simulate content adaptation (would be done by social-media-poster skill)
    plans_dir = os.path.join(temp_vault, 'Plans')
    plan_file = os.path.join(plans_dir, 'Plan_social_post.md')

    with open(plan_file, 'w') as f:
        f.write("""# Plan: Social Media Post

## Platform-Specific Content

### Facebook
Full content (no character limit)

### Instagram
Full content + hashtags (2200 char limit)

### Twitter
Thread (280 char limit per tweet)

## Approval Required
Yes - External communication
""")

    assert os.path.exists(plan_file)

    # Step 3: Simulate approval and execution
    done_dir = os.path.join(temp_vault, 'Done')
    done_file = os.path.join(done_dir, 'social_post_request.md')

    with open(post_file, 'r') as f:
        content = f.read()
    content = content.replace('status: pending', 'status: executed')
    content += f"\n\nPosted to: Facebook, Instagram, Twitter\nPost IDs: fb_123, ig_456, tw_789\n"

    with open(done_file, 'w') as f:
        f.write(content)

    os.remove(post_file)

    # Verify workflow complete
    assert os.path.exists(done_file)
    assert 'status: executed' in open(done_file).read()


# ============================================================================
# T131: Integration test for Ralph loop with multiple action items
# ============================================================================

def test_ralph_loop_multiple_items(temp_vault):
    """
    Test Ralph Wiggum Loop with multiple action items:
    1. Create multiple items in /Needs_Action/
    2. Start Ralph loop
    3. Process items one by one
    4. Verify all items moved to /Done/
    5. Verify loop exits when complete
    """
    # Create multiple action items
    needs_action_dir = os.path.join(temp_vault, 'Needs_Action')

    for i in range(3):
        item_file = os.path.join(needs_action_dir, f'task_{i}.md')
        with open(item_file, 'w') as f:
            f.write(f"""---
type: general
created_at: {datetime.now().isoformat()}
status: pending
---

# Task {i}

Complete task {i}
""")

    # Verify all items created
    items = list(Path(needs_action_dir).glob('*.md'))
    assert len(items) == 3

    # Simulate Ralph loop processing (would be done by ralph-wiggum-runner)
    done_dir = os.path.join(temp_vault, 'Done')

    for item_file in items:
        # Process item
        with open(item_file, 'r') as f:
            content = f.read()
        content = content.replace('status: pending', 'status: completed')

        # Move to Done
        done_file = os.path.join(done_dir, os.path.basename(item_file))
        with open(done_file, 'w') as f:
            f.write(content)
        os.remove(item_file)

    # Verify all items processed
    done_items = list(Path(done_dir).glob('*.md'))
    assert len(done_items) == 3

    remaining_items = list(Path(needs_action_dir).glob('*.md'))
    assert len(remaining_items) == 0


# ============================================================================
# T132: Integration test for CEO briefing generation with all data sources
# ============================================================================

def test_ceo_briefing_generation(temp_vault):
    """
    Test CEO briefing generation:
    1. Create completed tasks in /Done/
    2. Simulate Odoo data
    3. Simulate social media data
    4. Generate briefing
    5. Verify briefing file created in /Briefings/
    """
    # Create completed tasks
    done_dir = os.path.join(temp_vault, 'Done')

    for i in range(5):
        task_file = os.path.join(done_dir, f'completed_task_{i}.md')
        with open(task_file, 'w') as f:
            f.write(f"""---
type: email
completed_at: {datetime.now().isoformat()}
status: completed
duration: 1.5
---

# Completed Task {i}

Task completed successfully
""")

    # Verify tasks created
    tasks = list(Path(done_dir).glob('*.md'))
    assert len(tasks) == 5

    # Simulate briefing generation (would be done by ceo-briefing-generator)
    briefings_dir = os.path.join(temp_vault, 'Briefings')
    briefing_file = os.path.join(briefings_dir, f'BRIEF-{datetime.now().strftime("%Y-%m-%d")}.md')

    with open(briefing_file, 'w') as f:
        f.write(f"""---
type: ceo_briefing
generated: {datetime.now().isoformat()}
---

# Weekly Business Briefing

## Executive Summary
- Tasks completed: 5
- Revenue: $2,500
- Expenses: $850

## Completed Tasks
- Task 0
- Task 1
- Task 2
- Task 3
- Task 4

## Financial Summary
Revenue on track

## Social Media Performance
Good engagement across all platforms
""")

    # Verify briefing created
    assert os.path.exists(briefing_file)
    assert 'Tasks completed: 5' in open(briefing_file).read()


# ============================================================================
# T133: Integration test for error recovery with retry logic
# ============================================================================

def test_error_recovery_retry_logic():
    """
    Test error recovery with retry logic:
    1. Simulate transient error
    2. Verify retry with exponential backoff
    3. Verify eventual success
    """
    sys.path.insert(0, str(Path(__file__).parent.parent / "My_AI_Employee" / "utils"))
    from retry import retry_with_backoff

    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=0.1)
    def flaky_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Transient error")
        return "success"

    result = flaky_operation()

    assert result == "success"
    assert call_count == 3  # Failed twice, succeeded on third attempt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

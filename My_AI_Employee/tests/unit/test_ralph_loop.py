#!/usr/bin/env python3
"""
Unit Tests for Ralph Wiggum Loop Stop Hook

Tests file movement detection, iteration counting, max iterations limit,
and state management for autonomous task completion.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import stop hook functions
stop_hook_path = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "stop"
sys.path.insert(0, str(stop_hook_path))

import ralph_wiggum_check


@pytest.fixture
def temp_vault():
    """Create temporary vault directory structure."""
    temp_dir = tempfile.mkdtemp()
    vault_path = os.path.join(temp_dir, "AI_Employee_Vault")

    # Create vault folders
    os.makedirs(os.path.join(vault_path, "Needs_Action"))
    os.makedirs(os.path.join(vault_path, "Done"))
    os.makedirs(os.path.join(vault_path, "Pending_Approval"))
    os.makedirs(os.path.join(vault_path, "Approved"))
    os.makedirs(os.path.join(vault_path, "Rejected"))
    os.makedirs(os.path.join(vault_path, "Failed"))

    yield vault_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_state_file():
    """Create temporary Ralph state file."""
    temp_dir = tempfile.mkdtemp()
    state_file = os.path.join(temp_dir, ".ralph_state.json")

    yield state_file

    # Cleanup
    if os.path.exists(state_file):
        os.remove(state_file)
    shutil.rmtree(temp_dir)


# ============================================================================
# T071: Test file movement detection
# ============================================================================

def test_check_task_complete_file_in_needs_action(temp_vault):
    """Test that task is incomplete when file still in /Needs_Action/."""
    task_file = os.path.join(temp_vault, "Needs_Action", "test_task.md")

    # Create task file in /Needs_Action/
    with open(task_file, 'w') as f:
        f.write("# Test Task\n\nTest content")

    # Override VAULT_PATH for test
    original_vault = ralph_wiggum_check.VAULT_PATH
    ralph_wiggum_check.VAULT_PATH = temp_vault

    try:
        result = ralph_wiggum_check.check_task_complete(task_file)
        assert result is False, "Task should be incomplete when file in /Needs_Action/"
    finally:
        ralph_wiggum_check.VAULT_PATH = original_vault


def test_check_task_complete_file_moved_to_done(temp_vault):
    """Test that task is complete when file moved to /Done/."""
    task_filename = "test_task.md"
    task_file = os.path.join(temp_vault, "Needs_Action", task_filename)
    done_file = os.path.join(temp_vault, "Done", task_filename)

    # Create task file in /Done/ (simulating move)
    with open(done_file, 'w') as f:
        f.write("# Test Task\n\nTest content")

    # Override VAULT_PATH for test
    original_vault = ralph_wiggum_check.VAULT_PATH
    ralph_wiggum_check.VAULT_PATH = temp_vault

    try:
        result = ralph_wiggum_check.check_task_complete(task_file)
        assert result is True, "Task should be complete when file in /Done/"
    finally:
        ralph_wiggum_check.VAULT_PATH = original_vault


def test_check_task_complete_file_in_pending_approval(temp_vault):
    """Test that task is incomplete when file in /Pending_Approval/."""
    task_filename = "test_task.md"
    task_file = os.path.join(temp_vault, "Needs_Action", task_filename)
    pending_file = os.path.join(temp_vault, "Pending_Approval", task_filename)

    # Create task file in /Pending_Approval/
    with open(pending_file, 'w') as f:
        f.write("# Test Task\n\nTest content")

    # Override VAULT_PATH for test
    original_vault = ralph_wiggum_check.VAULT_PATH
    ralph_wiggum_check.VAULT_PATH = temp_vault

    try:
        result = ralph_wiggum_check.check_task_complete(task_file)
        assert result is False, "Task should be incomplete when file in /Pending_Approval/"
    finally:
        ralph_wiggum_check.VAULT_PATH = original_vault


def test_check_all_needs_action_processed_empty(temp_vault):
    """Test that all tasks processed when /Needs_Action/ is empty."""
    # Override VAULT_PATH for test
    original_vault = ralph_wiggum_check.VAULT_PATH
    ralph_wiggum_check.VAULT_PATH = temp_vault

    try:
        result = ralph_wiggum_check.check_all_needs_action_processed()
        assert result is True, "Should return True when /Needs_Action/ is empty"
    finally:
        ralph_wiggum_check.VAULT_PATH = original_vault


def test_check_all_needs_action_processed_has_files(temp_vault):
    """Test that tasks not processed when /Needs_Action/ has files."""
    # Create task files in /Needs_Action/
    task_file1 = os.path.join(temp_vault, "Needs_Action", "task1.md")
    task_file2 = os.path.join(temp_vault, "Needs_Action", "task2.md")

    with open(task_file1, 'w') as f:
        f.write("# Task 1")
    with open(task_file2, 'w') as f:
        f.write("# Task 2")

    # Override VAULT_PATH for test
    original_vault = ralph_wiggum_check.VAULT_PATH
    ralph_wiggum_check.VAULT_PATH = temp_vault

    try:
        result = ralph_wiggum_check.check_all_needs_action_processed()
        assert result is False, "Should return False when /Needs_Action/ has files"
    finally:
        ralph_wiggum_check.VAULT_PATH = original_vault


# ============================================================================
# T072: Test iteration counting
# ============================================================================

def test_get_ralph_state_no_file(temp_state_file):
    """Test getting state when no state file exists."""
    # Override state file path
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file

    try:
        result = ralph_wiggum_check.get_ralph_state()
        assert result is None, "Should return None when no state file exists"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state


def test_get_ralph_state_with_file(temp_state_file):
    """Test getting state when state file exists."""
    # Create state file
    state_data = {
        "task_file": "/path/to/task.md",
        "iteration": 3,
        "max_iterations": 10,
        "started_at": "2026-01-29T10:00:00"
    }

    with open(temp_state_file, 'w') as f:
        json.dump(state_data, f)

    # Override state file path
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file

    try:
        result = ralph_wiggum_check.get_ralph_state()
        assert result is not None, "Should return state when file exists"
        assert result["iteration"] == 3, "Should return correct iteration count"
        assert result["task_file"] == "/path/to/task.md", "Should return correct task file"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state


def test_increment_iteration(temp_state_file):
    """Test incrementing iteration counter."""
    state = {
        "task_file": "/path/to/task.md",
        "iteration": 3,
        "max_iterations": 10
    }

    result = ralph_wiggum_check.increment_iteration(state)

    assert result["iteration"] == 4, "Should increment iteration by 1"
    assert "last_iteration_at" in result, "Should add last_iteration_at timestamp"


def test_increment_iteration_from_zero(temp_state_file):
    """Test incrementing iteration from 0 (first iteration)."""
    state = {
        "task_file": "/path/to/task.md",
        "max_iterations": 10
    }

    result = ralph_wiggum_check.increment_iteration(state)

    assert result["iteration"] == 1, "Should increment from 0 to 1"


def test_update_ralph_state(temp_state_file):
    """Test updating Ralph state file."""
    state_data = {
        "task_file": "/path/to/task.md",
        "iteration": 5,
        "max_iterations": 10,
        "started_at": "2026-01-29T10:00:00"
    }

    # Override state file path
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file

    try:
        result = ralph_wiggum_check.update_ralph_state(state_data)
        assert result is True, "Should return True on successful update"

        # Verify file contents
        with open(temp_state_file, 'r') as f:
            saved_state = json.load(f)

        assert saved_state["iteration"] == 5, "Should save correct iteration"
        assert saved_state["task_file"] == "/path/to/task.md", "Should save correct task file"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state


# ============================================================================
# T073: Test max iterations limit
# ============================================================================

def test_main_max_iterations_reached(temp_vault, temp_state_file, monkeypatch):
    """Test that hook allows exit when max iterations reached."""
    # Create state with max iterations reached
    state_data = {
        "task_file": os.path.join(temp_vault, "Needs_Action", "task.md"),
        "iteration": 10,
        "max_iterations": 10,
        "started_at": "2026-01-29T10:00:00"
    }

    with open(temp_state_file, 'w') as f:
        json.dump(state_data, f)

    # Create task file (still incomplete)
    task_file = os.path.join(temp_vault, "Needs_Action", "task.md")
    with open(task_file, 'w') as f:
        f.write("# Test Task")

    # Override paths
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    original_vault = ralph_wiggum_check.VAULT_PATH
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file
    ralph_wiggum_check.VAULT_PATH = temp_vault

    # Suppress print statements
    monkeypatch.setattr('builtins.print', lambda *args, **kwargs: None)

    try:
        exit_code = ralph_wiggum_check.main()
        assert exit_code == 0, "Should return 0 (allow exit) when max iterations reached"

        # Verify state file cleared
        assert not os.path.exists(temp_state_file), "Should clear state file on max iterations"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state
        ralph_wiggum_check.VAULT_PATH = original_vault


def test_main_task_incomplete_continue(temp_vault, temp_state_file, monkeypatch):
    """Test that hook blocks exit when task incomplete and under max iterations."""
    # Create state with iterations under max
    state_data = {
        "task_file": os.path.join(temp_vault, "Needs_Action", "task.md"),
        "iteration": 3,
        "max_iterations": 10,
        "started_at": "2026-01-29T10:00:00"
    }

    with open(temp_state_file, 'w') as f:
        json.dump(state_data, f)

    # Create task file (still incomplete)
    task_file = os.path.join(temp_vault, "Needs_Action", "task.md")
    with open(task_file, 'w') as f:
        f.write("# Test Task")

    # Override paths
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    original_vault = ralph_wiggum_check.VAULT_PATH
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file
    ralph_wiggum_check.VAULT_PATH = temp_vault

    # Suppress print statements
    monkeypatch.setattr('builtins.print', lambda *args, **kwargs: None)

    try:
        exit_code = ralph_wiggum_check.main()
        assert exit_code == 1, "Should return 1 (block exit) when task incomplete"

        # Verify iteration incremented
        with open(temp_state_file, 'r') as f:
            updated_state = json.load(f)
        assert updated_state["iteration"] == 4, "Should increment iteration"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state
        ralph_wiggum_check.VAULT_PATH = original_vault


# ============================================================================
# T074: Test state management
# ============================================================================

def test_clear_ralph_state(temp_state_file):
    """Test clearing Ralph state file."""
    # Create state file
    state_data = {
        "task_file": "/path/to/task.md",
        "iteration": 5,
        "max_iterations": 10
    }

    with open(temp_state_file, 'w') as f:
        json.dump(state_data, f)

    # Override state file path
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file

    try:
        result = ralph_wiggum_check.clear_ralph_state()
        assert result is True, "Should return True on successful clear"
        assert not os.path.exists(temp_state_file), "Should delete state file"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state


def test_clear_ralph_state_no_file(temp_state_file):
    """Test clearing state when no file exists."""
    # Override state file path
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file

    try:
        result = ralph_wiggum_check.clear_ralph_state()
        assert result is True, "Should return True even when no file exists"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state


def test_main_no_active_loop(temp_state_file, monkeypatch):
    """Test that hook allows exit when no active Ralph loop."""
    # Override state file path (no file exists)
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file

    # Suppress print statements
    monkeypatch.setattr('builtins.print', lambda *args, **kwargs: None)

    try:
        exit_code = ralph_wiggum_check.main()
        assert exit_code == 0, "Should return 0 (allow exit) when no active loop"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state


def test_main_task_complete_allow_exit(temp_vault, temp_state_file, monkeypatch):
    """Test that hook allows exit when task complete."""
    task_filename = "task.md"

    # Create state
    state_data = {
        "task_file": os.path.join(temp_vault, "Needs_Action", task_filename),
        "iteration": 3,
        "max_iterations": 10,
        "started_at": "2026-01-29T10:00:00"
    }

    with open(temp_state_file, 'w') as f:
        json.dump(state_data, f)

    # Create task file in /Done/ (task complete)
    done_file = os.path.join(temp_vault, "Done", task_filename)
    with open(done_file, 'w') as f:
        f.write("# Test Task")

    # Override paths
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    original_vault = ralph_wiggum_check.VAULT_PATH
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file
    ralph_wiggum_check.VAULT_PATH = temp_vault

    # Suppress print statements
    monkeypatch.setattr('builtins.print', lambda *args, **kwargs: None)

    try:
        exit_code = ralph_wiggum_check.main()
        assert exit_code == 0, "Should return 0 (allow exit) when task complete"

        # Verify state file cleared
        assert not os.path.exists(temp_state_file), "Should clear state file on completion"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state
        ralph_wiggum_check.VAULT_PATH = original_vault


def test_state_persistence_across_iterations(temp_state_file):
    """Test that state persists correctly across multiple iterations."""
    # Initial state
    state = {
        "task_file": "/path/to/task.md",
        "iteration": 0,
        "max_iterations": 10,
        "started_at": "2026-01-29T10:00:00"
    }

    # Override state file path
    original_state = ralph_wiggum_check.RALPH_STATE_FILE
    ralph_wiggum_check.RALPH_STATE_FILE = temp_state_file

    try:
        # Simulate 3 iterations
        for i in range(3):
            state = ralph_wiggum_check.increment_iteration(state)
            ralph_wiggum_check.update_ralph_state(state)

            # Read back and verify
            loaded_state = ralph_wiggum_check.get_ralph_state()
            assert loaded_state["iteration"] == i + 1, f"Iteration {i+1} should persist"
            assert loaded_state["task_file"] == "/path/to/task.md", "Task file should persist"
    finally:
        ralph_wiggum_check.RALPH_STATE_FILE = original_state


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

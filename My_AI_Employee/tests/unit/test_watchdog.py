#!/usr/bin/env python3
"""
Unit Tests for Watchdog Component Monitor

Tests component detection, auto-restart logic, and crash loop detection.
"""

import os
import sys
import json
import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def temp_state_file():
    """Create temporary state file."""
    temp_dir = tempfile.mkdtemp()
    state_file = os.path.join(temp_dir, ".watchdog_state.json")
    yield state_file
    # Cleanup
    if os.path.exists(state_file):
        os.remove(state_file)


@pytest.fixture
def mock_watchdog():
    """Mock watchdog module."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "My_AI_Employee"))
    import watchdog
    return watchdog


# ============================================================================
# T105: Test component detection
# ============================================================================

def test_detect_components_empty(mock_watchdog):
    """Test component detection when no components running."""
    with patch('psutil.process_iter', return_value=[]):
        running = mock_watchdog.detect_components()
        assert running == {}


def test_detect_components_with_running(mock_watchdog):
    """Test component detection with running components."""
    # Mock process
    mock_proc = Mock()
    mock_proc.info = {
        'pid': 12345,
        'name': 'python3',
        'cmdline': ['python3', 'My_AI_Employee/run_watcher.py'],
        'create_time': time.time()
    }

    with patch('psutil.process_iter', return_value=[mock_proc]):
        # Enable orchestrator
        original_enabled = mock_watchdog.COMPONENTS['orchestrator']['enabled']
        mock_watchdog.COMPONENTS['orchestrator']['enabled'] = True

        try:
            running = mock_watchdog.detect_components()

            assert 'orchestrator' in running
            assert running['orchestrator']['pid'] == 12345
            assert running['orchestrator']['status'] == 'running'
        finally:
            mock_watchdog.COMPONENTS['orchestrator']['enabled'] = original_enabled


def test_is_component_running(mock_watchdog):
    """Test checking if specific component is running."""
    with patch.object(mock_watchdog, 'detect_components', return_value={'orchestrator': {'pid': 12345}}):
        assert mock_watchdog.is_component_running('orchestrator') is True
        assert mock_watchdog.is_component_running('gmail_watcher') is False


# ============================================================================
# T106: Test auto-restart logic
# ============================================================================

def test_start_component_success(mock_watchdog):
    """Test successful component start."""
    mock_proc = Mock()
    mock_proc.pid = 12345
    mock_proc.poll.return_value = None  # Still running

    with patch('subprocess.Popen', return_value=mock_proc):
        # Enable orchestrator
        original_enabled = mock_watchdog.COMPONENTS['orchestrator']['enabled']
        mock_watchdog.COMPONENTS['orchestrator']['enabled'] = True

        try:
            pid = mock_watchdog.start_component('orchestrator')
            assert pid == 12345
        finally:
            mock_watchdog.COMPONENTS['orchestrator']['enabled'] = original_enabled


def test_start_component_failure(mock_watchdog):
    """Test component start failure."""
    mock_proc = Mock()
    mock_proc.pid = 12345
    mock_proc.poll.return_value = 1  # Exited with error

    with patch('subprocess.Popen', return_value=mock_proc):
        # Enable orchestrator
        original_enabled = mock_watchdog.COMPONENTS['orchestrator']['enabled']
        mock_watchdog.COMPONENTS['orchestrator']['enabled'] = True

        try:
            pid = mock_watchdog.start_component('orchestrator')
            assert pid is None
        finally:
            mock_watchdog.COMPONENTS['orchestrator']['enabled'] = original_enabled


def test_start_component_disabled(mock_watchdog):
    """Test starting disabled component."""
    # Gmail watcher is disabled by default
    pid = mock_watchdog.start_component('gmail_watcher')
    assert pid is None


def test_stop_component_success(mock_watchdog):
    """Test successful component stop."""
    mock_proc = Mock()
    mock_proc.terminate = Mock()
    mock_proc.wait = Mock()

    with patch.object(mock_watchdog, 'detect_components', return_value={'orchestrator': {'pid': 12345, 'name': 'Orchestrator'}}):
        with patch('psutil.Process', return_value=mock_proc):
            result = mock_watchdog.stop_component('orchestrator')
            assert result is True
            mock_proc.terminate.assert_called_once()


def test_stop_component_not_running(mock_watchdog):
    """Test stopping component that's not running."""
    with patch.object(mock_watchdog, 'detect_components', return_value={}):
        result = mock_watchdog.stop_component('orchestrator')
        assert result is True  # Returns True if already stopped


def test_restart_component(mock_watchdog):
    """Test component restart."""
    with patch.object(mock_watchdog, 'is_component_running', return_value=True):
        with patch.object(mock_watchdog, 'stop_component', return_value=True):
            with patch.object(mock_watchdog, 'start_component', return_value=12345):
                result = mock_watchdog.restart_component('orchestrator')
                assert result is True


# ============================================================================
# T107: Test crash loop detection
# ============================================================================

def test_detect_crash_loop_no_restarts(mock_watchdog):
    """Test crash loop detection with no restarts."""
    state = {
        'components': {
            'orchestrator': {
                'restart_count': 0,
                'restart_history': []
            }
        }
    }

    result = mock_watchdog.detect_crash_loop('orchestrator', state)
    assert result is False


def test_detect_crash_loop_few_restarts(mock_watchdog):
    """Test crash loop detection with few restarts."""
    now = datetime.now()
    state = {
        'components': {
            'orchestrator': {
                'restart_count': 2,
                'restart_history': [
                    (now - timedelta(seconds=60)).isoformat(),
                    (now - timedelta(seconds=30)).isoformat()
                ]
            }
        }
    }

    result = mock_watchdog.detect_crash_loop('orchestrator', state)
    assert result is False  # Only 2 restarts, threshold is 3


def test_detect_crash_loop_threshold_reached(mock_watchdog):
    """Test crash loop detection when threshold reached."""
    now = datetime.now()
    state = {
        'components': {
            'orchestrator': {
                'restart_count': 3,
                'restart_history': [
                    (now - timedelta(seconds=240)).isoformat(),  # 4 minutes ago
                    (now - timedelta(seconds=120)).isoformat(),  # 2 minutes ago
                    (now - timedelta(seconds=60)).isoformat()    # 1 minute ago
                ]
            }
        }
    }

    result = mock_watchdog.detect_crash_loop('orchestrator', state)
    assert result is True  # 3 restarts within 5 minutes


def test_detect_crash_loop_old_restarts(mock_watchdog):
    """Test crash loop detection with old restarts outside window."""
    now = datetime.now()
    state = {
        'components': {
            'orchestrator': {
                'restart_count': 3,
                'restart_history': [
                    (now - timedelta(seconds=600)).isoformat(),  # 10 minutes ago (outside window)
                    (now - timedelta(seconds=120)).isoformat(),  # 2 minutes ago
                    (now - timedelta(seconds=60)).isoformat()    # 1 minute ago
                ]
            }
        }
    }

    result = mock_watchdog.detect_crash_loop('orchestrator', state)
    assert result is False  # Only 2 restarts within 5-minute window


def test_record_restart(mock_watchdog):
    """Test recording component restart."""
    state = {
        'components': {}
    }

    updated_state = mock_watchdog.record_restart('orchestrator', state)

    assert 'orchestrator' in updated_state['components']
    assert updated_state['components']['orchestrator']['restart_count'] == 1
    assert len(updated_state['components']['orchestrator']['restart_history']) == 1
    assert updated_state['components']['orchestrator']['last_restart'] is not None


def test_record_restart_multiple(mock_watchdog):
    """Test recording multiple restarts."""
    state = {
        'components': {
            'orchestrator': {
                'restart_count': 2,
                'restart_history': [
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ],
                'last_restart': datetime.now().isoformat()
            }
        }
    }

    updated_state = mock_watchdog.record_restart('orchestrator', state)

    assert updated_state['components']['orchestrator']['restart_count'] == 3
    assert len(updated_state['components']['orchestrator']['restart_history']) == 3


def test_send_alert(mock_watchdog, tmp_path):
    """Test alert notification."""
    # Mock vault path
    vault_path = tmp_path / "AI_Employee_Vault" / "Alerts"
    vault_path.mkdir(parents=True)

    with patch.object(Path, '__new__', return_value=tmp_path):
        mock_watchdog.send_alert('orchestrator', 'Test alert message')

    # Verify alert file created
    alert_files = list(vault_path.glob('ALERT_*.md'))
    assert len(alert_files) > 0


def test_health_check_all_running(mock_watchdog):
    """Test health check when all components running."""
    state = {'components': {}}

    with patch.object(mock_watchdog, 'detect_components', return_value={'orchestrator': {'pid': 12345}}):
        updated_state = mock_watchdog.health_check(state)

        # No restarts should be recorded
        assert updated_state == state


def test_health_check_component_down(mock_watchdog):
    """Test health check when component is down."""
    state = {'components': {}}

    # Enable orchestrator
    original_enabled = mock_watchdog.COMPONENTS['orchestrator']['enabled']
    mock_watchdog.COMPONENTS['orchestrator']['enabled'] = True

    try:
        with patch.object(mock_watchdog, 'detect_components', return_value={}):
            with patch.object(mock_watchdog, 'detect_crash_loop', return_value=False):
                with patch.object(mock_watchdog, 'restart_component', return_value=True):
                    updated_state = mock_watchdog.health_check(state)

                    # Restart should be recorded
                    assert 'orchestrator' in updated_state['components']
                    assert updated_state['components']['orchestrator']['restart_count'] == 1
    finally:
        mock_watchdog.COMPONENTS['orchestrator']['enabled'] = original_enabled


def test_health_check_crash_loop(mock_watchdog):
    """Test health check with crash loop detected."""
    state = {'components': {}}

    # Enable orchestrator
    original_enabled = mock_watchdog.COMPONENTS['orchestrator']['enabled']
    mock_watchdog.COMPONENTS['orchestrator']['enabled'] = True

    try:
        with patch.object(mock_watchdog, 'detect_components', return_value={}):
            with patch.object(mock_watchdog, 'detect_crash_loop', return_value=True):
                with patch.object(mock_watchdog, 'send_alert') as mock_alert:
                    updated_state = mock_watchdog.health_check(state)

                    # Alert should be sent
                    mock_alert.assert_called_once()
    finally:
        mock_watchdog.COMPONENTS['orchestrator']['enabled'] = original_enabled


def test_state_persistence(mock_watchdog, temp_state_file):
    """Test state save and load."""
    # Override state file
    original_state_file = mock_watchdog.STATE_FILE
    mock_watchdog.STATE_FILE = temp_state_file

    try:
        # Create state
        state = {
            'components': {
                'orchestrator': {
                    'restart_count': 5,
                    'restart_history': [datetime.now().isoformat()],
                    'last_restart': datetime.now().isoformat()
                }
            },
            'started_at': datetime.now().isoformat()
        }

        # Save state
        result = mock_watchdog.save_state(state)
        assert result is True

        # Load state
        loaded_state = mock_watchdog.load_state()
        assert loaded_state['components']['orchestrator']['restart_count'] == 5
    finally:
        mock_watchdog.STATE_FILE = original_state_file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

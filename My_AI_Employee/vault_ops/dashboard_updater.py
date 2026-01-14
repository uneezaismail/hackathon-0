"""
Dashboard updater for vault operations.

Updates Dashboard.md with system status, pending counts, recent activity,
and warnings while preserving user notes.
"""

from pathlib import Path
from datetime import datetime
import logging
import re


logger = logging.getLogger(__name__)


class DashboardUpdater:
    """
    Manages updates to the Dashboard.md file.

    Provides non-destructive updates that preserve user-added content
    while updating system-managed sections.
    """

    def __init__(self, vault_path: str | Path):
        """
        Initialize dashboard updater.

        Args:
            vault_path: Path to the Obsidian vault root

        Raises:
            ValueError: If vault_path is invalid
        """
        self.vault_path = Path(vault_path)

        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        self.dashboard_path = self.vault_path / "Dashboard.md"

        if not self.dashboard_path.exists():
            logger.warning(f"Dashboard not found, will create: {self.dashboard_path}")
            self._create_default_dashboard()

    def _create_default_dashboard(self) -> None:
        """Create a default dashboard if it doesn't exist."""
        default_content = """# AI Employee Dashboard

## Status Overview
**Pending Items**: 0
**Last Updated**: Never

## Recent Activity
No activity yet.

## System Health
✅ System operational

## Warnings
No warnings.

---
## User Notes
<!-- Add your notes below this line. They will be preserved during updates. -->

"""
        self.dashboard_path.write_text(default_content, encoding='utf-8')
        logger.info("Created default dashboard")

    def _read_dashboard(self) -> str:
        """Read current dashboard content."""
        try:
            return self.dashboard_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read dashboard: {e}")
            return ""

    def _write_dashboard(self, content: str) -> None:
        """Write updated dashboard content."""
        try:
            self.dashboard_path.write_text(content, encoding='utf-8')
            logger.debug("Dashboard updated successfully")
        except Exception as e:
            logger.error(f"Failed to write dashboard: {e}")
            raise

    def _update_section(self, content: str, section_name: str, new_section_content: str) -> str:
        """
        Update a specific section in the dashboard.

        Preserves content after the user notes separator.

        Args:
            content: Current dashboard content
            section_name: Name of the section to update (e.g., "Status Overview")
            new_section_content: New content for the section

        Returns:
            Updated dashboard content
        """
        # Find the section
        section_pattern = rf'(## {re.escape(section_name)}.*?)(?=\n## |\n---|\Z)'

        if re.search(section_pattern, content, re.DOTALL):
            # Replace existing section
            updated = re.sub(
                section_pattern,
                f'## {section_name}\n{new_section_content}\n',
                content,
                flags=re.DOTALL
            )
            return updated
        else:
            # Section doesn't exist, add it before user notes separator
            separator_index = content.find('---')
            if separator_index != -1:
                before_separator = content[:separator_index]
                after_separator = content[separator_index:]
                return f"{before_separator}## {section_name}\n{new_section_content}\n\n{after_separator}"
            else:
                # No separator, append to end
                return f"{content}\n## {section_name}\n{new_section_content}\n"

    def update_pending_count(self, count: int) -> None:
        """
        Update the pending items count in the dashboard.

        Args:
            count: Number of pending items in Needs_Action folder
        """
        content = self._read_dashboard()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status_content = f"""**Pending Items**: {count}
**Last Updated**: {timestamp}"""

        updated_content = self._update_section(content, "Status Overview", status_content)
        self._write_dashboard(updated_content)

        logger.info(f"Updated pending count: {count}")

    def add_recent_activity(self, activity_description: str, item_reference: str = None) -> None:
        """
        Add a recent activity entry to the dashboard.

        Args:
            activity_description: Description of the activity
            item_reference: Optional reference to related item
        """
        content = self._read_dashboard()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build activity entry
        if item_reference:
            activity_entry = f"- **{timestamp}**: {activity_description} (`{item_reference}`)"
        else:
            activity_entry = f"- **{timestamp}**: {activity_description}"

        # Extract current recent activity section
        activity_pattern = r'## Recent Activity\n(.*?)(?=\n## |\n---|\Z)'
        match = re.search(activity_pattern, content, re.DOTALL)

        if match:
            current_activities = match.group(1).strip()

            # Remove "No activity yet" message if present
            if "No activity yet" in current_activities:
                current_activities = ""

            # Add new activity at the top
            if current_activities:
                activities_list = current_activities.split('\n')
                activities_list.insert(0, activity_entry)

                # Keep only last 10 activities
                activities_list = activities_list[:10]

                new_activities = '\n'.join(activities_list)
            else:
                new_activities = activity_entry
        else:
            new_activities = activity_entry

        updated_content = self._update_section(content, "Recent Activity", new_activities)
        self._write_dashboard(updated_content)

        logger.info(f"Added activity: {activity_description}")

    def add_warning(self, warning_message: str, warning_id: str = None) -> None:
        """
        Add a warning to the dashboard.

        Args:
            warning_message: Warning message to display
            warning_id: Optional unique ID for the warning (for deduplication)
        """
        content = self._read_dashboard()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build warning entry
        warning_entry = f"⚠️ **{timestamp}**: {warning_message}"

        if warning_id:
            warning_entry += f" (ID: {warning_id})"

        # Extract current warnings section
        warnings_pattern = r'## Warnings\n(.*?)(?=\n## |\n---|\Z)'
        match = re.search(warnings_pattern, content, re.DOTALL)

        if match:
            current_warnings = match.group(1).strip()

            # Remove "No warnings" message if present
            if "No warnings" in current_warnings:
                current_warnings = ""

            # Check for duplicate warning_id
            if warning_id and warning_id in current_warnings:
                logger.debug(f"Warning {warning_id} already exists, skipping")
                return

            # Add new warning
            if current_warnings:
                new_warnings = f"{warning_entry}\n{current_warnings}"
            else:
                new_warnings = warning_entry
        else:
            new_warnings = warning_entry

        updated_content = self._update_section(content, "Warnings", new_warnings)
        self._write_dashboard(updated_content)

        logger.info(f"Added warning: {warning_message[:50]}...")

    def clear_warnings(self) -> None:
        """Clear all warnings from the dashboard."""
        content = self._read_dashboard()

        warnings_content = "No warnings."

        updated_content = self._update_section(content, "Warnings", warnings_content)
        self._write_dashboard(updated_content)

        logger.info("Cleared all warnings")

    def update_system_health(self, status: str, details: str = None) -> None:
        """
        Update system health status.

        Args:
            status: Health status ("operational", "degraded", "error")
            details: Optional details about the status
        """
        content = self._read_dashboard()

        # Map status to emoji
        status_emoji = {
            'operational': '✅',
            'degraded': '⚠️',
            'error': '❌'
        }

        emoji = status_emoji.get(status.lower(), '❓')

        health_content = f"{emoji} System {status}"

        if details:
            health_content += f"\n\n{details}"

        updated_content = self._update_section(content, "System Health", health_content)
        self._write_dashboard(updated_content)

        logger.info(f"Updated system health: {status}")

    def get_dashboard_summary(self) -> dict:
        """
        Get a summary of current dashboard state.

        Returns:
            Dictionary with dashboard summary information
        """
        content = self._read_dashboard()

        # Extract pending count
        pending_match = re.search(r'\*\*Pending Items\*\*:\s*(\d+)', content)
        pending_count = int(pending_match.group(1)) if pending_match else 0

        # Count warnings
        warnings_section = re.search(r'## Warnings\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        warning_count = 0
        if warnings_section:
            warnings_text = warnings_section.group(1)
            if "No warnings" not in warnings_text:
                warning_count = warnings_text.count('⚠️')

        # Count recent activities
        activity_section = re.search(r'## Recent Activity\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        activity_count = 0
        if activity_section:
            activities_text = activity_section.group(1)
            if "No activity yet" not in activities_text:
                activity_count = activities_text.count('- **')

        return {
            'pending_count': pending_count,
            'warning_count': warning_count,
            'activity_count': activity_count,
            'dashboard_path': str(self.dashboard_path)
        }


def update_dashboard_after_triage(
    vault_path: str | Path,
    pending_count: int,
    processed_items: list,
    warnings: list = None
) -> None:
    """
    Update dashboard after triage workflow completes.

    Args:
        vault_path: Path to the Obsidian vault root
        pending_count: Current count of pending items
        processed_items: List of processed item names
        warnings: Optional list of warning messages
    """
    updater = DashboardUpdater(vault_path)

    # Update pending count
    updater.update_pending_count(pending_count)

    # Add activity for each processed item
    for item_name in processed_items:
        updater.add_recent_activity(
            "Processed action item",
            item_reference=item_name
        )

    # Add warnings if any
    if warnings:
        for warning in warnings:
            updater.add_warning(warning)

    # Update system health
    if warnings:
        updater.update_system_health("degraded", f"{len(warnings)} warning(s) require attention")
    else:
        updater.update_system_health("operational")

    logger.info("Dashboard updated after triage")

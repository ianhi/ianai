"""
Patch Handler Module
Applies diffs/patches to files with validation and rollback capabilities.
Part of the file operations toolkit.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import shutil
from file_diff import FileDiff, DiffGenerator


@dataclass
class PatchResult:
    """Result of applying a patch."""

    success: bool
    file_path: str
    original_content: str
    new_content: str
    backup_path: Optional[str] = None
    error_message: Optional[str] = None


class PatchHandler:
    """Applies patches/diffs to files with safety checks."""

    def __init__(self, create_backups: bool = True, backup_dir: str = ".backups"):
        """
        Initialize patch handler.

        Args:
            create_backups: Whether to create backups before patching
            backup_dir: Directory to store backups
        """
        self.create_backups = create_backups
        self.backup_dir = backup_dir

        if create_backups:
            Path(backup_dir).mkdir(exist_ok=True)

    def _create_backup(self, file_path: str) -> Optional[str]:
        """
        Create a backup of file.

        Args:
            file_path: Path to file

        Returns:
            Path to backup file, or None if creation failed
        """
        try:
            file_path = Path(file_path)
            backup_path = Path(self.backup_dir) / f"{file_path.name}.bak"
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
            return None

    def apply_diff(self, file_path: str, file_diff: FileDiff) -> PatchResult:
        """
        Apply a diff to a file.

        Args:
            file_path: Path to file to patch
            file_diff: FileDiff object containing the patch

        Returns:
            PatchResult with outcome
        """
        try:
            # Read original file
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Create backup if requested
            backup_path = None
            if self.create_backups:
                backup_path = self._create_backup(file_path)

            # Reconstruct file from diff
            new_content = self._apply_diff_lines(original_content, file_diff)

            # Write new content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return PatchResult(
                success=True,
                file_path=file_path,
                original_content=original_content,
                new_content=new_content,
                backup_path=backup_path,
            )

        except Exception as e:
            return PatchResult(
                success=False,
                file_path=file_path,
                original_content="",
                new_content="",
                error_message=str(e),
            )

    def _apply_diff_lines(self, original_content: str, file_diff: FileDiff) -> str:
        """
        Apply diff lines to original content.

        Args:
            original_content: Original file content as string
            file_diff: FileDiff object

        Returns:
            Modified content
        """
        lines = original_content.split("\n")
        result = []

        # Build a mapping of old line numbers to content
        for diff_line in file_diff.lines:
            if diff_line.line_type == "+":
                result.append(diff_line.content)
            elif diff_line.line_type == " ":
                result.append(diff_line.content)
            # Skip '-' lines as they should be removed

        return "\n".join(result)

    def rollback(self, patch_result: PatchResult) -> bool:
        """
        Rollback a patch using backup.

        Args:
            patch_result: PatchResult from apply_diff

        Returns:
            True if rollback successful, False otherwise
        """
        if not patch_result.backup_path:
            print("No backup available for rollback")
            return False

        try:
            backup_path = Path(patch_result.backup_path)
            file_path = Path(patch_result.file_path)

            if not backup_path.exists():
                print(f"Backup file not found: {backup_path}")
                return False

            shutil.copy2(backup_path, file_path)
            return True

        except Exception as e:
            print(f"Rollback failed: {e}")
            return False

    def dry_run(self, file_path: str, file_diff: FileDiff) -> Tuple[bool, str]:
        """
        Simulate applying a patch without actually modifying the file.

        Args:
            file_path: Path to file
            file_diff: FileDiff to apply

        Returns:
            Tuple of (success, preview of changes)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            new_content = self._apply_diff_lines(original_content, file_diff)

            # Generate preview
            preview = []
            preview.append(f"Would modify: {file_path}")
            preview.append(f"Changes: +{file_diff.additions} -{file_diff.deletions}")
            preview.append("")
            preview.append("Preview of changes:")
            preview.append("-" * 60)

            diff_gen = DiffGenerator()
            preview_text = diff_gen.format_diff_readable(file_diff)
            preview.append(preview_text)

            return True, "\n".join(preview)

        except Exception as e:
            return False, f"Error during dry run: {str(e)}"

    def validate_patch_applicability(
        self, file_path: str, file_diff: FileDiff
    ) -> Tuple[bool, List[str]]:
        """
        Check if a patch can be safely applied to a file.

        Args:
            file_path: Path to file to patch
            file_diff: Patch to apply

        Returns:
            Tuple of (is_applicable, list of issues)
        """
        issues = []

        # Check file exists
        if not Path(file_path).exists():
            issues.append(f"File does not exist: {file_path}")
            return False, issues

        # Check if file is binary
        if file_diff.is_binary:
            issues.append("Cannot apply patch to binary file")
            return False, issues

        # Try dry run for deeper validation
        success, preview = self.dry_run(file_path, file_diff)
        if not success:
            issues.append(f"Dry run failed: {preview}")
            return False, issues

        return True, issues

"""
Diff/Merge API Module
High-level API that integrates all diff and merge functionality.
Designed to be used by the AI assistant's tool functions.
Part of the file operations toolkit.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import asdict
import json

from file_diff import DiffGenerator, FileDiff
from dir_diff import DirectoryDiffer, DirectoryDiff
from file_merge import ThreeWayMerger, MergeResult, MergeConflict
from patch_handler import PatchHandler, PatchResult


class DiffMergeAPI:
    """High-level API for diff and merge operations."""

    def __init__(self, create_backups: bool = True, backup_dir: str = ".backups"):
        """
        Initialize the API.

        Args:
            create_backups: Whether to create backups when applying patches
            backup_dir: Directory for storing backups
        """
        self.diff_generator = DiffGenerator(context_lines=3)
        self.directory_differ = DirectoryDiffer(diff_generator=self.diff_generator)
        self.merger = ThreeWayMerger()
        self.patch_handler = PatchHandler(
            create_backups=create_backups, backup_dir=backup_dir
        )

    # ============ FILE DIFF OPERATIONS ============

    def diff_files(self, file_old: str, file_new: str) -> Dict:
        """
        Compare two files and return diff.

        Args:
            file_old: Path to original file
            file_new: Path to new file

        Returns:
            Dictionary with diff information
        """
        file_diff = self.diff_generator.diff_files(file_old, file_new)

        return {
            "file_old": file_diff.file_path_old,
            "file_new": file_diff.file_path_new,
            "additions": file_diff.additions,
            "deletions": file_diff.deletions,
            "total_changes": file_diff.additions + file_diff.deletions,
            "is_binary": file_diff.is_binary,
            "diff_lines": [
                {
                    "type": line.line_type,
                    "content": line.content.rstrip("\n"),
                    "line_old": line.line_number_old,
                    "line_new": line.line_number_new,
                }
                for line in file_diff.lines
            ],
        }

    def get_file_diff_summary(self, file_old: str, file_new: str) -> Dict:
        """
        Get a summary of differences between two files (without full diff).

        Args:
            file_old: Path to original file
            file_new: Path to new file

        Returns:
            Dictionary with summary statistics
        """
        file_diff = self.diff_generator.diff_files(file_old, file_new)
        return self.diff_generator.get_diff_stats(file_diff)

    def format_diff_readable(self, file_old: str, file_new: str) -> str:
        """
        Get human-readable diff output.

        Args:
            file_old: Path to original file
            file_new: Path to new file

        Returns:
            Formatted diff string
        """
        file_diff = self.diff_generator.diff_files(file_old, file_new)
        return self.diff_generator.format_diff_readable(file_diff)

    # ============ DIRECTORY DIFF OPERATIONS ============

    def diff_directories(
        self, dir_old: str, dir_new: str, extensions_filter: Optional[List[str]] = None
    ) -> Dict:
        """
        Compare two directories.

        Args:
            dir_old: Path to original directory
            dir_new: Path to new directory
            extensions_filter: Optional list of file extensions to include (e.g., ['.py', '.txt'])

        Returns:
            Dictionary with directory diff information
        """
        if extensions_filter:
            differ = DirectoryDiffer(
                diff_generator=self.diff_generator, extensions_filter=extensions_filter
            )
        else:
            differ = self.directory_differ

        dir_diff = differ.diff_directories(dir_old, dir_new)
        summary = dir_diff.get_summary()

        return {
            "dir_old": dir_diff.dir_old,
            "dir_new": dir_diff.dir_new,
            "summary": summary,
            "added_files": dir_diff.get_added_files(),
            "deleted_files": dir_diff.get_deleted_files(),
            "modified_files": dir_diff.get_modified_files(),
            "entries": [
                {
                    "file_path": entry.file_path,
                    "status": entry.status,
                    "changes": {
                        "additions": entry.diff.additions,
                        "deletions": entry.diff.deletions,
                    }
                    if entry.diff
                    else None,
                }
                for entry in dir_diff.entries
            ],
        }

    def format_directory_diff_readable(
        self,
        dir_old: str,
        dir_new: str,
        include_file_diffs: bool = False,
        extensions_filter: Optional[List[str]] = None,
    ) -> str:
        """
        Get human-readable directory diff output.

        Args:
            dir_old: Path to original directory
            dir_new: Path to new directory
            include_file_diffs: Whether to include detailed diffs for each file
            extensions_filter: Optional list of file extensions to include

        Returns:
            Formatted directory diff string
        """
        if extensions_filter:
            differ = DirectoryDiffer(
                diff_generator=self.diff_generator, extensions_filter=extensions_filter
            )
        else:
            differ = self.directory_differ

        dir_diff = differ.diff_directories(dir_old, dir_new)
        return differ.format_directory_diff_readable(
            dir_diff, include_diffs=include_file_diffs
        )

    # ============ MERGE OPERATIONS ============

    def merge_files(
        self, base_file: str, branch_a_file: str, branch_b_file: str
    ) -> Dict:
        """
        Perform three-way merge on three files.

        Args:
            base_file: Path to base file
            branch_a_file: Path to branch A file
            branch_b_file: Path to branch B file

        Returns:
            Dictionary with merge result
        """
        merge_result = self.merger.merge_files(base_file, branch_a_file, branch_b_file)

        return {
            "success": not merge_result.has_conflicts,
            "has_conflicts": merge_result.has_conflicts,
            "num_conflicts": len(merge_result.conflicts),
            "conflict_summary": merge_result.get_conflict_summary(),
            "conflicts": [
                {
                    "type": conflict.conflict_type.value,
                    "line_number": conflict.line_number,
                    "base": conflict.base_content.rstrip("\n"),
                    "branch_a": conflict.branch_a_content.rstrip("\n"),
                    "branch_b": conflict.branch_b_content.rstrip("\n"),
                }
                for conflict in merge_result.conflicts
            ],
        }

    def resolve_merge_conflicts(
        self,
        base_file: str,
        branch_a_file: str,
        branch_b_file: str,
        resolutions: Dict[int, str],
    ) -> Tuple[bool, str]:
        """
        Perform merge and apply conflict resolutions.

        Args:
            base_file: Path to base file
            branch_a_file: Path to branch A file
            branch_b_file: Path to branch B file
            resolutions: Dict mapping conflict index to resolution strategy
                       ('branch_a', 'branch_b', or 'both')

        Returns:
            Tuple of (success, message)
        """
        merge_result = self.merger.merge_files(base_file, branch_a_file, branch_b_file)

        if not merge_result.conflicts:
            return True, "Merge completed with no conflicts"

        # Validate resolutions
        for idx in resolutions.keys():
            if idx >= len(merge_result.conflicts):
                return False, f"Resolution index {idx} out of range"
            if resolutions[idx] not in ["branch_a", "branch_b", "both"]:
                return False, f"Invalid resolution: {resolutions[idx]}"

        # Apply resolutions
        resolved_lines = self.merger.apply_resolutions(merge_result, resolutions)

        return (
            True,
            f"Merge completed with {len(merge_result.conflicts)} conflicts resolved",
        )

    # ============ PATCH/APPLICATION OPERATIONS ============

    def apply_diff_to_file(
        self, file_path: str, file_old: str, file_new: str, dry_run: bool = False
    ) -> Dict:
        """
        Apply diff from file_old→file_new to file_path.

        Args:
            file_path: File to apply patch to
            file_old: Original file for generating diff
            file_new: New file for generating diff
            dry_run: If True, simulate without actual changes

        Returns:
            Dictionary with patch result
        """
        file_diff = self.diff_generator.diff_files(file_old, file_new)

        # Validate patch first
        is_valid, issues = self.patch_handler.validate_patch_applicability(
            file_path, file_diff
        )

        if not is_valid:
            return {
                "success": False,
                "file_path": file_path,
                "error": f"Patch validation failed: {'; '.join(issues)}",
            }

        if dry_run:
            success, preview = self.patch_handler.dry_run(file_path, file_diff)
            return {
                "success": success,
                "file_path": file_path,
                "is_dry_run": True,
                "preview": preview,
            }
        else:
            patch_result = self.patch_handler.apply_diff(file_path, file_diff)
            return {
                "success": patch_result.success,
                "file_path": patch_result.file_path,
                "backup_path": patch_result.backup_path,
                "error": patch_result.error_message,
                "changes": {
                    "additions": file_diff.additions,
                    "deletions": file_diff.deletions,
                },
            }

    def validate_patch(self, file_path: str, file_old: str, file_new: str) -> Dict:
        """
        Check if a patch can be applied to a file.

        Args:
            file_path: File to check
            file_old: Original file for diff
            file_new: New file for diff

        Returns:
            Dictionary with validation result
        """
        file_diff = self.diff_generator.diff_files(file_old, file_new)
        is_valid, issues = self.patch_handler.validate_patch_applicability(
            file_path, file_diff
        )

        return {"file_path": file_path, "is_applicable": is_valid, "issues": issues}

    # ============ UTILITY OPERATIONS ============

    def compare_and_report(self, file_old: str, file_new: str) -> str:
        """
        Generate a comprehensive comparison report.

        Args:
            file_old: Path to original file
            file_new: Path to new file

        Returns:
            Formatted report string
        """
        file_diff = self.diff_generator.diff_files(file_old, file_new)
        return self.diff_generator.format_diff_readable(file_diff)

    def get_change_statistics(self, file_old: str, file_new: str) -> Dict:
        """
        Get detailed change statistics between files.

        Args:
            file_old: Path to original file
            file_new: Path to new file

        Returns:
            Dictionary with statistics
        """
        file_diff = self.diff_generator.diff_files(file_old, file_new)
        stats = self.diff_generator.get_diff_stats(file_diff)

        total = stats["additions"] + stats["deletions"]
        percent_change = (total / (total + 1)) * 100 if total > 0 else 0

        return {
            **stats,
            "total_changes": total,
            "percent_change": f"{percent_change:.1f}%",
        }

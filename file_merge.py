"""
File Merge Module
Provides three-way merge capabilities for resolving conflicting changes.
Part of the file operations toolkit.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import difflib


class MergeConflictType(Enum):
    """Types of merge conflicts."""

    CONTENT_CONFLICT = "content_conflict"
    DELETION_CONFLICT = "deletion_conflict"
    ADDITION_CONFLICT = "addition_conflict"


@dataclass
class MergeConflict:
    """Represents a merge conflict."""

    conflict_type: MergeConflictType
    line_number: int
    base_content: str
    branch_a_content: str
    branch_b_content: str
    resolution: Optional[str] = None


@dataclass
class MergeResult:
    """Result of a three-way merge."""

    merged_lines: List[str]
    conflicts: List[MergeConflict]
    has_conflicts: bool = False

    def get_conflict_summary(self) -> str:
        """Get human-readable summary of conflicts."""
        if not self.conflicts:
            return "No conflicts"
        return f"{len(self.conflicts)} conflict(s) found"


class ThreeWayMerger:
    """Performs three-way merge between files."""

    def __init__(self, context_lines: int = 3):
        """
        Initialize merger.

        Args:
            context_lines: Number of context lines for matching
        """
        self.context_lines = context_lines

    def _read_file_safely(self, file_path: str) -> List[str]:
        """
        Read file safely, returning empty list if not found.

        Args:
            file_path: Path to file

        Returns:
            List of lines from file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.readlines()
        except (FileNotFoundError, UnicodeDecodeError):
            return []

    def merge_files(
        self, base_file: str, branch_a_file: str, branch_b_file: str
    ) -> MergeResult:
        """
        Perform three-way merge on three files.

        Args:
            base_file: Path to base (original) file
            branch_a_file: Path to first branch file
            branch_b_file: Path to second branch file

        Returns:
            MergeResult with merged content and any conflicts
        """
        base_lines = self._read_file_safely(base_file)
        branch_a_lines = self._read_file_safely(branch_a_file)
        branch_b_lines = self._read_file_safely(branch_b_file)

        # Use difflib for smart merging
        matcher_a = difflib.SequenceMatcher(None, base_lines, branch_a_lines)
        matcher_b = difflib.SequenceMatcher(None, base_lines, branch_b_lines)

        merged_lines = []
        conflicts = []

        # Get matching blocks to identify changed regions
        blocks_a = matcher_a.get_matching_blocks()
        blocks_b = matcher_b.get_matching_blocks()

        # Strategy: Merge changes from both branches
        # If both branches modify the same region, it's a conflict
        merged_lines, conflicts = self._merge_matching_blocks(
            base_lines, branch_a_lines, branch_b_lines, blocks_a, blocks_b
        )

        return MergeResult(
            merged_lines=merged_lines,
            conflicts=conflicts,
            has_conflicts=len(conflicts) > 0,
        )

    def _merge_matching_blocks(
        self,
        base: List[str],
        branch_a: List[str],
        branch_b: List[str],
        blocks_a: List,
        blocks_b: List,
    ) -> Tuple[List[str], List[MergeConflict]]:
        """
        Merge files using matching blocks from both branches.

        Args:
            base: Base file lines
            branch_a: Branch A lines
            branch_b: Branch B lines
            blocks_a: Matching blocks between base and A
            blocks_b: Matching blocks between base and B

        Returns:
            Tuple of (merged_lines, conflicts)
        """
        merged = []
        conflicts = []
        processed_base = set()

        # Process each matching block from branch A
        for i, (base_start, a_start, size) in enumerate(
            blocks_a[:-1]
        ):  # Skip final block
            # Add lines changed in A but not in B
            if base_start not in processed_base:
                processed_base.add(base_start)

                # Check if same region was modified in B
                conflict_in_b = any(
                    b_start <= base_start < b_start + b_size
                    for b_start, _, b_size in blocks_b[:-1]
                )

                if conflict_in_b:
                    # Conflict: both branches modified same region
                    a_modified = branch_a[a_start : a_start + size]
                    b_start = next(
                        b_start
                        for b_start, _, b_size in blocks_b[:-1]
                        if b_start <= base_start < b_start + b_size
                    )
                    b_modified = branch_b[b_start : b_start + size]

                    conflicts.append(
                        MergeConflict(
                            conflict_type=MergeConflictType.CONTENT_CONFLICT,
                            line_number=len(merged),
                            base_content="".join(base[base_start : base_start + size]),
                            branch_a_content="".join(a_modified),
                            branch_b_content="".join(b_modified),
                        )
                    )

                    # Add both versions with conflict markers
                    merged.extend(
                        [f"<<<<<<< BRANCH_A\n"]
                        + a_modified
                        + [f"=======\n"]
                        + b_modified
                        + [f">>>>>>> BRANCH_B\n"]
                    )
                else:
                    # No conflict: add A's version
                    merged.extend(branch_a[a_start : a_start + size])

        # Add remaining lines from B that weren't processed
        if len(branch_b) > sum(size for _, _, size in blocks_b[:-1]):
            remaining = branch_b[sum(size for _, _, size in blocks_b[:-1]) :]
            merged.extend(remaining)

        return merged, conflicts

    def resolve_conflict(self, conflict: MergeConflict, resolution: str) -> None:
        """
        Resolve a merge conflict.

        Args:
            conflict: MergeConflict to resolve
            resolution: Either 'branch_a', 'branch_b', or 'both'
        """
        if resolution not in ["branch_a", "branch_b", "both", "custom"]:
            raise ValueError(f"Invalid resolution: {resolution}")

        conflict.resolution = resolution

    def apply_resolutions(
        self, merge_result: MergeResult, resolutions: dict
    ) -> List[str]:
        """
        Apply conflict resolutions to merged content.

        Args:
            merge_result: MergeResult with conflicts
            resolutions: Dict mapping conflict index to resolution ('branch_a', 'branch_b', 'both')

        Returns:
            Merged lines with conflicts resolved
        """
        if not merge_result.conflicts:
            return merge_result.merged_lines

        # Apply resolutions to conflicts
        for idx, resolution in resolutions.items():
            if idx < len(merge_result.conflicts):
                self.resolve_conflict(merge_result.conflicts[idx], resolution)

        # Rebuild merged content with resolutions applied
        return self._rebuild_with_resolutions(
            merge_result.merged_lines, merge_result.conflicts
        )

    def _rebuild_with_resolutions(
        self, merged_lines: List[str], conflicts: List[MergeConflict]
    ) -> List[str]:
        """
        Rebuild merged content with conflict resolutions applied.

        Args:
            merged_lines: Original merged lines with conflict markers
            conflicts: List of conflicts with resolutions

        Returns:
            Cleaned merged lines
        """
        result = []
        i = 0
        conflict_idx = 0

        while i < len(merged_lines):
            line = merged_lines[i]

            if line.startswith("<<<<<<< BRANCH_A"):
                if conflict_idx < len(conflicts):
                    conflict = conflicts[conflict_idx]
                    resolution = conflict.resolution

                    # Skip conflict markers and content
                    i += 1
                    branch_a_lines = []
                    while i < len(merged_lines) and not merged_lines[i].startswith(
                        "======="
                    ):
                        branch_a_lines.append(merged_lines[i])
                        i += 1

                    # Skip separator
                    i += 1
                    branch_b_lines = []
                    while i < len(merged_lines) and not merged_lines[i].startswith(
                        ">>>>>>> BRANCH_B"
                    ):
                        branch_b_lines.append(merged_lines[i])
                        i += 1

                    # Skip end marker
                    i += 1

                    # Apply resolution
                    if resolution == "branch_a":
                        result.extend(branch_a_lines)
                    elif resolution == "branch_b":
                        result.extend(branch_b_lines)
                    elif resolution == "both":
                        result.extend(branch_a_lines)
                        result.extend(branch_b_lines)

                    conflict_idx += 1
                continue

            result.append(line)
            i += 1

        return result

    def write_merged_file(
        self,
        merge_result: MergeResult,
        output_path: str,
        resolutions: Optional[dict] = None,
    ) -> bool:
        """
        Write merged result to file.

        Args:
            merge_result: MergeResult to write
            output_path: Path to write to
            resolutions: Optional conflict resolutions

        Returns:
            True if successful, False otherwise
        """
        try:
            if resolutions:
                content = self.apply_resolutions(merge_result, resolutions)
            else:
                content = merge_result.merged_lines

            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(content)
            return True
        except Exception as e:
            print(f"Error writing merged file: {e}")
            return False

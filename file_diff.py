"""
File Diff Module
Provides unified diff generation between files and directories.
Part of the file operations toolkit.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
import difflib
from pathlib import Path


@dataclass
class DiffLine:
    """Represents a single line in a diff with metadata."""

    line_type: str  # '+', '-', ' ', '?'
    content: str
    line_number_old: Optional[int] = None
    line_number_new: Optional[int] = None


@dataclass
class FileDiff:
    """Represents the complete diff between two files."""

    file_path_old: str
    file_path_new: str
    lines: List[DiffLine]
    additions: int = 0
    deletions: int = 0
    is_binary: bool = False

    def __post_init__(self):
        """Calculate statistics."""
        self.additions = sum(1 for line in self.lines if line.line_type == "+")
        self.deletions = sum(1 for line in self.lines if line.line_type == "-")


class DiffGenerator:
    """Generates unified diffs between files."""

    def __init__(self, context_lines: int = 3):
        """
        Initialize diff generator.

        Args:
            context_lines: Number of context lines to show around changes (default: 3)
        """
        self.context_lines = context_lines

    def _read_file_safely(self, file_path: str) -> Tuple[List[str], bool]:
        """
        Read file, handling binary files gracefully.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (lines, is_binary)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return lines, False
        except UnicodeDecodeError:
            return [], True
        except FileNotFoundError:
            return [], False

    def diff_files(self, file_path_old: str, file_path_new: str) -> FileDiff:
        """
        Generate unified diff between two files.

        Args:
            file_path_old: Path to original file
            file_path_new: Path to new file

        Returns:
            FileDiff object with differences
        """
        lines_old, is_binary_old = self._read_file_safely(file_path_old)
        lines_new, is_binary_new = self._read_file_safely(file_path_new)

        # Handle binary files
        if is_binary_old or is_binary_new:
            return FileDiff(
                file_path_old=file_path_old,
                file_path_new=file_path_new,
                lines=[],
                is_binary=True,
            )

        # Use difflib to generate unified diff
        diff_lines = list(
            difflib.unified_diff(
                lines_old,
                lines_new,
                fromfile=file_path_old,
                tofile=file_path_new,
                n=self.context_lines,
                lineterm="",
            )
        )

        # Parse unified diff into our format
        parsed_lines = self._parse_unified_diff(diff_lines, lines_old, lines_new)

        return FileDiff(
            file_path_old=file_path_old, file_path_new=file_path_new, lines=parsed_lines
        )

    def _parse_unified_diff(
        self, diff_lines: List[str], original_lines: List[str], new_lines: List[str]
    ) -> List[DiffLine]:
        """
        Parse unified diff format into DiffLine objects.

        Args:
            diff_lines: Lines from unified diff
            original_lines: Original file lines
            new_lines: New file lines

        Returns:
            List of DiffLine objects
        """
        result = []
        old_line_num = 0
        new_line_num = 0

        # Skip header lines
        in_header = True

        for line in diff_lines:
            if in_header:
                if line.startswith("---") or line.startswith("+++"):
                    continue
                if line.startswith("@@"):
                    in_header = False
                    continue

            if not line:
                continue

            # Determine line type and extract content
            if line.startswith("-"):
                result.append(
                    DiffLine(
                        line_type="-",
                        content=line[1:],
                        line_number_old=old_line_num + 1,
                        line_number_new=None,
                    )
                )
                old_line_num += 1
            elif line.startswith("+"):
                result.append(
                    DiffLine(
                        line_type="+",
                        content=line[1:],
                        line_number_old=None,
                        line_number_new=new_line_num + 1,
                    )
                )
                new_line_num += 1
            elif line.startswith(" "):
                result.append(
                    DiffLine(
                        line_type=" ",
                        content=line[1:],
                        line_number_old=old_line_num + 1,
                        line_number_new=new_line_num + 1,
                    )
                )
                old_line_num += 1
                new_line_num += 1

        return result

    def format_diff_readable(self, file_diff: FileDiff) -> str:
        """
        Format diff for human-readable output.

        Args:
            file_diff: FileDiff object

        Returns:
            Formatted diff string
        """
        if file_diff.is_binary:
            return f"Binary files differ: {file_diff.file_path_old} vs {file_diff.file_path_new}"

        output = []
        output.append(f"--- {file_diff.file_path_old}")
        output.append(f"+++ {file_diff.file_path_new}")
        output.append(f"Changes: +{file_diff.additions} -{file_diff.deletions}")
        output.append("")

        for line in file_diff.lines:
            if line.line_type == "+":
                output.append(f"+ {line.content}")
            elif line.line_type == "-":
                output.append(f"- {line.content}")
            elif line.line_type == " ":
                output.append(f"  {line.content}")

        return "\n".join(output)

    def get_diff_stats(self, file_diff: FileDiff) -> dict:
        """
        Get statistics about the diff.

        Args:
            file_diff: FileDiff object

        Returns:
            Dictionary with diff statistics
        """
        return {
            "file_old": file_diff.file_path_old,
            "file_new": file_diff.file_path_new,
            "additions": file_diff.additions,
            "deletions": file_diff.deletions,
            "total_changes": file_diff.additions + file_diff.deletions,
            "is_binary": file_diff.is_binary,
        }

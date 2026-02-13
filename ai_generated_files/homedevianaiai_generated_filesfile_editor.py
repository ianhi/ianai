"""File editor tool for replacing code blocks by line numbers."""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple
import difflib


class FileEditor:
    """A tool for editing files by replacing code blocks at specific line ranges."""

    def __init__(self, file_path: str):
        """Initialize the file editor with a target file path."""
        self.file_path = Path(file_path)

    def replace_lines(
        self, start_line: int, end_line: int, new_content: str
    ) -> Tuple[bool, str]:
        """
        Replace lines in a file from start_line to end_line (inclusive) with new_content.

        Args:
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            new_content: New content to replace the lines with

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Read the original file
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Validate line numbers
            if (
                start_line < 1
                or end_line < 1
                or start_line > len(lines)
                or end_line > len(lines)
            ):
                return False, f"Line numbers out of range. File has {len(lines)} lines."

            if start_line > end_line:
                return False, "Start line must be less than or equal to end line."

            # Prepare new content - ensure it ends with newline
            if not new_content.endswith("\n"):
                new_content += "\n"

            # Replace the specified lines
            new_lines = lines[: start_line - 1] + [new_content] + lines[end_line:]

            # Write back to file
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            return (
                True,
                f"Successfully replaced lines {start_line}-{end_line} with new content.",
            )

        except Exception as e:
            return False, f"Error replacing lines: {str(e)}"

    def run_ruff(self) -> Tuple[bool, str]:
        """Run ruff on the edited file and return the results."""
        try:
            # Run ruff on the file
            result = subprocess.run(
                ["ruff", "check", str(self.file_path)],
                capture_output=True,
                text=True,
                cwd=self.file_path.parent,
            )

            if result.returncode == 0:
                return True, "No issues found by ruff."
            else:
                return False, result.stdout + result.stderr

        except FileNotFoundError:
            return (
                False,
                "Ruff is not installed. Please install it with 'pip install ruff'.",
            )
        except Exception as e:
            return False, f"Error running ruff: {str(e)}"

    def get_diff(self) -> str:
        """Get a formatted diff showing the changes made to the file."""
        # This would require storing the original content or using git
        # For now, we'll show what was changed via a simple approach
        return "Diff generation requires additional implementation for precise line tracking."

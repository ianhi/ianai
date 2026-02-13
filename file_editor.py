"""
File Editor Tool for AI Coding Agent
Provides functionality to edit files by line numbers and validate changes with Ruff.
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional
from datetime import datetime
import json


import subprocess
import tempfile
import difflib
from pathlib import Path
from typing import List, Tuple, Optional


class FileEditor:
    """A tool for editing files by line numbers and validating with Ruff."""

    def __init__(self):
        """Initialize the file editor."""
        pass

    def replace_lines(
        self, file_path: str, start_line: int, end_line: int, new_content: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Replace lines in a file by specifying start and end line numbers.

        Args:
            file_path: Path to the file to edit
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            new_content: New content to insert

        Returns:
            Tuple of (success: bool, message: str, diff: Optional[str])
        """
        try:
            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Validate line numbers
            if (
                start_line < 1
                or end_line < 1
                or start_line > len(lines)
                or end_line > len(lines)
            ):
                return (
                    False,
                    f"Line numbers out of range. File has {len(lines)} lines.",
                    None,
                )

            if start_line > end_line:
                return False, "Start line cannot be greater than end line.", None

            # Store original content for diff
            original_lines = lines[:]

            # Replace lines
            lines[start_line - 1 : end_line] = (
                [new_content + "\n"] if new_content else []
            )

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            # Generate diff
            diff = self._generate_diff(original_lines, lines, file_path)

            return (
                True,
                f"Successfully replaced lines {start_line}-{end_line} in {file_path}",
                diff,
            )

        except Exception as e:
            return False, f"Failed to edit file: {str(e)}", None

    def _generate_diff(
        self, old_lines: List[str], new_lines: List[str], file_path: str
    ) -> str:
        """
        Generate a diff between old and new content.

        Args:
            old_lines: Original lines
            new_lines: New lines
            file_path: Path to the file

        Returns:
            Formatted diff string
        """
        # Use difflib to generate unified diff
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )

        # Format the diff
        diff_lines = list(diff)
        if not diff_lines:
            return "No changes made."

        # Add some formatting to make it more readable
        formatted_diff = "```diff\n"
        formatted_diff += "\n".join(diff_lines)
        formatted_diff += "\n```"

        return formatted_diff

    def run_ruff_validation(self, file_path: str) -> Tuple[bool, str]:
        """
        Run Ruff on the file to validate the changes.

        Args:
            file_path: Path to the file to validate

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Run ruff check on the file
            result = subprocess.run(
                ["ruff", "check", file_path], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return True, "Ruff validation passed successfully."
            else:
                return (
                    False,
                    f"Ruff validation failed:\n{result.stdout}\n{result.stderr}",
                )

        except subprocess.TimeoutExpired:
            return False, "Ruff validation timed out."
        except FileNotFoundError:
            return (
                False,
                "Ruff is not installed. Please install it with 'pip install ruff'.",
            )
        except Exception as e:
            return False, f"Error running Ruff: {str(e)}"


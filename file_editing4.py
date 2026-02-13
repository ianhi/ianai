"""
Enhanced File Editor with Bulk Operations Support
Integrates modular line operations with the existing FileEditor interface.
"""

import os
import difflib
from typing import List, Dict, Any, Union, Optional

from line_operations import (
    LineOperation,
    InsertLineOperation,
    RemoveLineOperation,
    ChangeLineOperation,
    ReplacePatternOperation,
    LineRange,
    insert_lines,
    remove_lines,
    change_lines,
    replace_in_lines,
)
from bulk_editor import BulkEditor


class FileEditor:
    """
    Enhanced file editor with support for both single and bulk operations.
    Maintains backward compatibility with the original interface.
    """

    def __init__(self):
        """Initialize the FileEditor."""
        pass

    def _generate_diff(self, old_content: str, new_content: str, file_path: str) -> str:
        """
        Generate a unified diff between old and new content.

        Args:
            old_content: Original file content
            new_content: New file content
            file_path: Path to the file (for diff header)

        Returns:
            Unified diff string
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )

        return "".join(diff)

    def edit_file(self, file_path: str, content: str, mode: str = "w") -> Dict[str, Any]:
        """
        Edit a file at the specified path by writing content to it.

        Args:
            file_path: Relative path to the file to edit
            content: Content to write to the file
            mode: File opening mode ('w' for overwrite, 'a' for append)

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            # Read old content if file exists
            old_content = ""
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    old_content = file.read()

            # Create directories if they don't exist
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # Determine new content based on mode
            if mode == "a" and old_content:
                new_content = old_content + content
            else:
                new_content = content

            # Write the file
            with open(file_path, mode, encoding="utf-8") as file:
                file.write(content)

            # Generate diff
            diff = self._generate_diff(old_content, new_content, file_path)

            return {
                "message": f"Successfully edited {file_path}",
                "diff": diff,
                "success": True,
            }
        except Exception as e:
            return {
                "message": f"Error editing file: {str(e)}",
                "diff": "",
                "success": False,
            }

    def read_file(self, file_path: str) -> str:
        """
        Read content from a file at the specified path.

        Args:
            file_path: Relative path to the file to read

        Returns:
            File content or error message
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def append_to_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Append content to a file at the specified path.

        Args:
            file_path: Relative path to the file to append to
            content: Content to append to the file

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        return self.edit_file(file_path, content, mode="a")

    def insert_line(self, file_path: str, line_number: int, content: str) -> Dict[str, Any]:
        """
        Insert a line into a file at the specified line number.

        Args:
            file_path: Relative path to the file
            line_number: Line number where to insert (0-indexed)
            content: Content to insert

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            # Read all lines from the file
            old_content = self.read_file(file_path)
            if old_content.startswith("Error"):
                return {"message": old_content, "diff": "", "success": False}

            lines = old_content.splitlines(keepends=True)

            # Ensure line_number is valid
            if line_number < 0:
                line_number = 0
            elif line_number > len(lines):
                line_number = len(lines)

            # Insert the line
            lines.insert(line_number, content + "\n")
            new_content = "".join(lines)

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            # Generate diff
            diff = self._generate_diff(old_content, new_content, file_path)

            return {
                "message": f"Successfully inserted line at {line_number} in {file_path}",
                "diff": diff,
                "success": True,
            }
        except Exception as e:
            return {
                "message": f"Error inserting line: {str(e)}",
                "diff": "",
                "success": False,
            }

    def remove_line(self, file_path: str, line_number: int) -> Dict[str, Any]:
        """
        Remove a line from a file at the specified line number.

        Args:
            file_path: Relative path to the file
            line_number: Line number to remove (0-indexed)

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            # Read all lines from the file
            old_content = self.read_file(file_path)
            if old_content.startswith("Error"):
                return {"message": old_content, "diff": "", "success": False}

            lines = old_content.splitlines(keepends=True)

            # Check if line_number is valid
            if line_number < 0 or line_number >= len(lines):
                return {
                    "message": f"Error: Line number {line_number} is out of range",
                    "diff": "",
                    "success": False,
                }

            # Remove the line
            lines.pop(line_number)
            new_content = "".join(lines)

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            # Generate diff
            diff = self._generate_diff(old_content, new_content, file_path)

            return {
                "message": f"Successfully removed line {line_number} from {file_path}",
                "diff": diff,
                "success": True,
            }
        except Exception as e:
            return {
                "message": f"Error removing line: {str(e)}",
                "diff": "",
                "success": False,
            }

    def change_line(self, file_path: str, line_number: int, new_content: str) -> Dict[str, Any]:
        """
        Change the content of a specific line in a file.

        Args:
            file_path: Relative path to the file
            line_number: Line number to change (0-indexed)
            new_content: New content for the line

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            # Read all lines from the file
            old_content = self.read_file(file_path)
            if old_content.startswith("Error"):
                return {"message": old_content, "diff": "", "success": False}

            lines = old_content.splitlines(keepends=True)

            # Check if line_number is valid
            if line_number < 0 or line_number >= len(lines):
                return {
                    "message": f"Error: Line number {line_number} is out of range",
                    "diff": "",
                    "success": False,
                }

            # Change the line
            lines[line_number] = new_content + "\n"
            new_content_full = "".join(lines)

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content_full)

            # Generate diff
            diff = self._generate_diff(old_content, new_content_full, file_path)

            return {
                "message": f"Successfully changed line {line_number} in {file_path}",
                "diff": diff,
                "success": True,
            }
        except Exception as e:
            return {
                "message": f"Error changing line: {str(e)}",
                "diff": "",
                "success": False,
            }

    # NEW BULK OPERATIONS METHODS

    def insert_lines(
        self, file_path: str, line_number: int, content: Union[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Insert multiple lines into a file at the specified line number.

        Args:
            file_path: Relative path to the file
            line_number: Line number where to insert (0-indexed)
            content: Single string with newlines or list of lines to insert

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            editor = BulkEditor()
            editor.load_file(file_path)
            editor.insert(line_number, content)
            result = editor.apply()
            return result
        except Exception as e:
            return {
                "message": f"Error inserting lines: {str(e)}",
                "diff": "",
                "success": False,
            }

    def remove_lines(
        self, file_path: str, start_line: int, count: int = 1
    ) -> Dict[str, Any]:
        """
        Remove multiple lines from a file.

        Args:
            file_path: Relative path to the file
            start_line: First line number to remove (0-indexed)
            count: Number of lines to remove

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            editor = BulkEditor()
            editor.load_file(file_path)
            editor.remove(start_line, count)
            result = editor.apply()
            return result
        except Exception as e:
            return {
                "message": f"Error removing lines: {str(e)}",
                "diff": "",
                "success": False,
            }

    def change_lines(
        self, file_path: str, start_line: int, new_content: Union[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Change multiple lines in a file.

        Args:
            file_path: Relative path to the file
            start_line: First line number to change (0-indexed)
            new_content: New content (single string or list of lines)

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            editor = BulkEditor()
            editor.load_file(file_path)
            editor.change(start_line, new_content)
            result = editor.apply()
            return result
        except Exception as e:
            return {
                "message": f"Error changing lines: {str(e)}",
                "diff": "",
                "success": False,
            }

    def replace_in_file(
        self,
        file_path: str,
        pattern: str,
        replacement: str,
        regex: bool = False,
        max_replacements: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Replace text pattern in a file.

        Args:
            file_path: Relative path to the file
            pattern: Text pattern to find
            replacement: Replacement text
            regex: If True, pattern is a regular expression
            max_replacements: Maximum number of replacements (None = unlimited)

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            editor = BulkEditor()
            editor.load_file(file_path)
            editor.replace(pattern, replacement, regex=regex, max_replacements=max_replacements)
            result = editor.apply()
            return result
        except Exception as e:
            return {
                "message": f"Error replacing text: {str(e)}",
                "diff": "",
                "success": False,
            }

    def bulk_edit(
        self,
        file_path: str,
        operations: List[Dict[str, Any]],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Apply multiple operations to a file at once.

        Args:
            file_path: Relative path to the file
            operations: List of operation dictionaries with 'type' and parameters
            dry_run: If True, preview changes without writing

        Returns:
            Dictionary with 'message', 'diff', and 'success' keys

        Example operations:
            [
                {"type": "insert", "line_number": 0, "content": "New first line"},
                {"type": "remove", "line_number": 5, "count": 2},
                {"type": "change", "line_number": 10, "content": "Changed line"},
                {"type": "replace", "pattern": "old", "replacement": "new"},
            ]
        """
        try:
            editor = BulkEditor()
            editor.load_file(file_path)

            # Parse and add operations
            for op_dict in operations:
                op_type = op_dict.get("type", "").lower()

                if op_type == "insert":
                    editor.insert(
                        op_dict["line_number"],
                        op_dict["content"],
                    )
                elif op_type == "remove":
                    editor.remove(
                        op_dict["line_number"],
                        op_dict.get("count", 1),
                    )
                elif op_type == "change":
                    editor.change(
                        op_dict["line_number"],
                        op_dict["content"],
                    )
                elif op_type == "replace":
                    editor.replace(
                        op_dict["pattern"],
                        op_dict["replacement"],
                        regex=op_dict.get("regex", False),
                        max_replacements=op_dict.get("max_replacements"),
                    )
                else:
                    return {
                        "message": f"Unknown operation type: {op_type}",
                        "success": False,
                    }

            result = editor.apply(dry_run=dry_run)
            return result

        except Exception as e:
            return {
                "message": f"Error in bulk edit: {str(e)}",
                "diff": "",
                "success": False,
            }

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Expose available tools for the AI agent.

        Returns:
            List of tool definitions in OpenAI function format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Edit a file at the specified path by writing content to it",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file to edit",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file",
                            },
                            "mode": {
                                "type": "string",
                                "description": "File opening mode ('w' for overwrite, 'a' for append)",
                                "default": "w",
                            },
                        },
                        "required": ["file_path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "insert_line",
                    "description": "Insert a single line into a file at the specified line number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number where to insert (0-indexed)",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to insert",
                            },
                        },
                        "required": ["file_path", "line_number", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "insert_lines",
                    "description": "Insert multiple lines into a file at the specified line number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number where to insert (0-indexed)",
                            },
                            "content": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of lines to insert, or a single string with newlines",
                            },
                        },
                        "required": ["file_path", "line_number", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_line",
                    "description": "Remove a single line from a file at the specified line number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number to remove (0-indexed)",
                            },
                        },
                        "required": ["file_path", "line_number"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_lines",
                    "description": "Remove multiple consecutive lines from a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "start_line": {
                                "type": "integer",
                                "description": "First line number to remove (0-indexed)",
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of lines to remove",
                                "default": 1,
                            },
                        },
                        "required": ["file_path", "start_line"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "change_line",
                    "description": "Change the content of a single line in a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number to change (0-indexed)",
                            },
                            "new_content": {
                                "type": "string",
                                "description": "New content for the line",
                            },
                        },
                        "required": ["file_path", "line_number", "new_content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "change_lines",
                    "description": "Change multiple lines in a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "start_line": {
                                "type": "integer",
                                "description": "First line number to change (0-indexed)",
                            },
                            "new_content": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "New content (list of lines or single string)",
                            },
                        },
                        "required": ["file_path", "start_line", "new_content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "replace_in_file",
                    "description": "Replace text pattern in a file (supports regex)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "pattern": {
                                "type": "string",
                                "description": "Text pattern to find",
                            },
                            "replacement": {
                                "type": "string",
                                "description": "Replacement text",
                            },
                            "regex": {
                                "type": "boolean",
                                "description": "If true, pattern is a regular expression",
                                "default": False,
                            },
                            "max_replacements": {
                                "type": "integer",
                                "description": "Maximum number of replacements (null = unlimited)",
                            },
                        },
                        "required": ["file_path", "pattern", "replacement"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "bulk_edit",
                    "description": "Apply multiple editing operations to a file at once for efficiency",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "operations": {
                                "type": "array",
                                "description": "List of operations to apply",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["insert", "remove", "change", "replace"],
                                            "description": "Type of operation",
                                        },
                                        "line_number": {
                                            "type": "integer",
                                            "description": "Line number (for insert, remove, change)",
                                        },
                                        "content": {
                                            "description": "Content (for insert, change)",
                                        },
                                        "count": {
                                            "type": "integer",
                                            "description": "Number of lines (for remove)",
                                        },
                                        "pattern": {
                                            "type": "string",
                                            "description": "Pattern to find (for replace)",
                                        },
                                        "replacement": {
                                            "type": "string",
                                            "description": "Replacement text (for replace)",
                                        },
                                    },
                                },
                            },
                            "dry_run": {
                                "type": "boolean",
                                "description": "If true, preview changes without writing",
                                "default": False,
                            },
                        },
                        "required": ["file_path", "operations"],
                    },
                },
            },
        ]


# Example usage
if __name__ == "__main__":
    editor = FileEditor()

    # Create a test file
    print("=== Creating test file ===")
    result = editor.edit_file("test_bulk.txt", "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
    print(result["message"])

    # Test insert_lines
    print("\n=== Inserting multiple lines ===")
    result = editor.insert_lines("test_bulk.txt", 2, ["Inserted A", "Inserted B", "Inserted C"])
    print(result["message"])
    if result.get("diff"):
        print("Diff:", result["diff"])

    # Test remove_lines
    print("\n=== Removing multiple lines ===")
    result = editor.remove_lines("test_bulk.txt", 3, count=2)
    print(result["message"])
    if result.get("diff"):
        print("Diff:", result["diff"])

    # Test bulk_edit
    print("\n=== Bulk edit with multiple operations ===")
    operations = [
        {"type": "insert", "line_number": 0, "content": "=== Header ==="},
        {"type": "replace", "pattern": "Line", "replacement": "Row"},
        {"type": "insert", "line_number": 100, "content": "=== Footer ==="},  # Will insert at end
    ]
    result = editor.bulk_edit("test_bulk.txt", operations)
    print(result["message"])
    if result.get("diff"):
        print("Diff:", result["diff"])

    # Show final content
    print("\n=== Final content ===")
    content = editor.read_file("test_bulk.txt")
    print(content)

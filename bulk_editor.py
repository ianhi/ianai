"""
Bulk Editor Module - Composable bulk operations on files
Provides high-level interface for applying multiple line operations efficiently.
"""

import os
import difflib
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from line_operations import (
    LineOperation,
    InsertLineOperation,
    RemoveLineOperation,
    ChangeLineOperation,
    ReplacePatternOperation,
    LineRange,
)


class BulkEditor:
    """
    High-level editor for performing bulk operations on files.
    Supports composing multiple operations and applying them efficiently.
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize a bulk editor.

        Args:
            file_path: Optional path to a file to edit
        """
        self.file_path = file_path
        self.operations: List[LineOperation] = []
        self.original_content: Optional[str] = None
        self.current_lines: Optional[List[str]] = None

    def load_file(self, file_path: str) -> "BulkEditor":
        """
        Load a file for editing.

        Args:
            file_path: Path to the file to load

        Returns:
            Self for method chaining
        """
        self.file_path = file_path
        
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                self.original_content = f.read()
                self.current_lines = self.original_content.splitlines(keepends=True)
        else:
            self.original_content = ""
            self.current_lines = []
        
        return self

    def add_operation(self, operation: LineOperation) -> "BulkEditor":
        """
        Add an operation to the queue.

        Args:
            operation: LineOperation to add

        Returns:
            Self for method chaining
        """
        self.operations.append(operation)
        return self

    def add_operations(self, operations: List[LineOperation]) -> "BulkEditor":
        """
        Add multiple operations to the queue.

        Args:
            operations: List of LineOperations to add

        Returns:
            Self for method chaining
        """
        self.operations.extend(operations)
        return self

    def insert(
        self, line_number: int, content: Union[str, List[str]], **kwargs
    ) -> "BulkEditor":
        """
        Add an insert operation.

        Args:
            line_number: Position to insert at
            content: Content to insert
            **kwargs: Additional arguments for InsertLineOperation

        Returns:
            Self for method chaining
        """
        self.operations.append(InsertLineOperation(line_number, content, **kwargs))
        return self

    def remove(
        self, line_number: int, count: int = 1, **kwargs
    ) -> "BulkEditor":
        """
        Add a remove operation.

        Args:
            line_number: Line to start removing from
            count: Number of lines to remove
            **kwargs: Additional arguments for RemoveLineOperation

        Returns:
            Self for method chaining
        """
        self.operations.append(RemoveLineOperation(line_number, count=count, **kwargs))
        return self

    def change(
        self, line_number: int, new_content: Union[str, List[str]], **kwargs
    ) -> "BulkEditor":
        """
        Add a change operation.

        Args:
            line_number: Line to change
            new_content: New content
            **kwargs: Additional arguments for ChangeLineOperation

        Returns:
            Self for method chaining
        """
        self.operations.append(ChangeLineOperation(line_number, new_content, **kwargs))
        return self

    def replace(
        self, pattern: str, replacement: str, **kwargs
    ) -> "BulkEditor":
        """
        Add a replace pattern operation.

        Args:
            pattern: Pattern to find
            replacement: Replacement text
            **kwargs: Additional arguments for ReplacePatternOperation

        Returns:
            Self for method chaining
        """
        self.operations.append(ReplacePatternOperation(pattern, replacement, **kwargs))
        return self

    def clear_operations(self) -> "BulkEditor":
        """
        Clear all queued operations.

        Returns:
            Self for method chaining
        """
        self.operations.clear()
        return self

    def validate_operations(self) -> Dict[str, Any]:
        """
        Validate all queued operations.

        Returns:
            Dictionary with validation results
        """
        if self.current_lines is None:
            return {
                "valid": False,
                "error": "No file loaded. Call load_file() first.",
            }

        line_count = len(self.current_lines)
        invalid_ops = []

        for i, op in enumerate(self.operations):
            if not op.validate(line_count):
                invalid_ops.append(
                    {"index": i, "operation": op.describe(), "error": "Invalid line range"}
                )

        if invalid_ops:
            return {
                "valid": False,
                "invalid_operations": invalid_ops,
                "total_operations": len(self.operations),
            }

        return {
            "valid": True,
            "total_operations": len(self.operations),
        }

    def sort_operations(self, reverse: bool = False) -> "BulkEditor":
        """
        Sort operations by priority and line number.
        
        For operations that affect line numbers (insert/remove), sorting helps
        apply them in the correct order (usually bottom-up for removes, top-down for inserts).

        Args:
            reverse: If True, sort in reverse order (useful for bottom-up operations)

        Returns:
            Self for method chaining
        """
        self.operations.sort(reverse=reverse)
        return self

    def apply(
        self, dry_run: bool = False, optimize: bool = True
    ) -> Dict[str, Any]:
        """
        Apply all queued operations to the file.

        Args:
            dry_run: If True, don't write to file, just return what would change
            optimize: If True, automatically optimize operation order

        Returns:
            Dictionary with operation results including diff
        """
        if self.current_lines is None:
            return {
                "success": False,
                "error": "No file loaded. Call load_file() first.",
            }

        # Validate operations
        validation = self.validate_operations()
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Operation validation failed",
                "validation": validation,
            }

        # Optimize operation order if requested
        if optimize:
            self._optimize_operation_order()

        # Apply operations sequentially
        result_lines = self.current_lines.copy()
        applied_operations = []

        try:
            for op in self.operations:
                result_lines = op.apply(result_lines)
                applied_operations.append(op.describe())

            # Generate new content
            new_content = "".join(result_lines)

            # Generate diff
            diff = self._generate_diff(self.original_content or "", new_content)

            result = {
                "success": True,
                "file_path": self.file_path,
                "operations_applied": len(applied_operations),
                "operations": applied_operations,
                "diff": diff,
                "dry_run": dry_run,
            }

            # Write to file if not dry run
            if not dry_run and self.file_path:
                # Create directory if needed
                dir_path = os.path.dirname(self.file_path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)

                with open(self.file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                result["message"] = f"Successfully applied {len(applied_operations)} operations to {self.file_path}"
                
                # Update current state
                self.original_content = new_content
                self.current_lines = result_lines
            else:
                result["message"] = f"Dry run: {len(applied_operations)} operations would be applied"
                result["new_content"] = new_content

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Error applying operations: {str(e)}",
                "operations_applied": len(applied_operations),
            }

    def _optimize_operation_order(self):
        """
        Optimize the order of operations to avoid conflicts.
        
        Strategy:
        - Process operations from bottom to top for removes and changes
        - This prevents line number shifts from affecting subsequent operations
        - Replaces can be done in any order as they don't affect line numbers
        """
        from line_operations import OperationType
        
        # Separate operations by type
        inserts = []
        removes = []
        changes = []
        replaces = []
        
        for op in self.operations:
            op_type = op.get_type()
            if op_type == OperationType.INSERT:
                inserts.append(op)
            elif op_type == OperationType.REMOVE:
                removes.append(op)
            elif op_type == OperationType.CHANGE:
                changes.append(op)
            elif op_type == OperationType.REPLACE:
                replaces.append(op)
        
        # Sort by line number (descending for removes/changes to work bottom-up)
        def get_line_number(op):
            if hasattr(op, 'line_number'):
                return op.line_number
            elif hasattr(op, 'range'):
                return op.range.start
            return 0
        
        # Apply in order: replaces (any order), removes (bottom-up), changes (bottom-up), inserts (bottom-up)
        self.operations = (
            replaces +
            sorted(removes, key=get_line_number, reverse=True) +
            sorted(changes, key=get_line_number, reverse=True) +
            sorted(inserts, key=get_line_number, reverse=True)
        )

    def _generate_diff(self, old_content: str, new_content: str) -> str:
        """
        Generate a unified diff between old and new content.

        Args:
            old_content: Original content
            new_content: New content

        Returns:
            Unified diff string
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{self.file_path or 'file'}",
            tofile=f"b/{self.file_path or 'file'}",
            lineterm="",
        )

        return "".join(diff)

    def preview(self) -> Dict[str, Any]:
        """
        Preview changes without applying them.

        Returns:
            Dictionary with preview information
        """
        return self.apply(dry_run=True)

    def reset(self) -> "BulkEditor":
        """
        Reset to original file state and clear operations.

        Returns:
            Self for method chaining
        """
        if self.file_path:
            self.load_file(self.file_path)
        self.operations.clear()
        return self


# Convenience function for one-off bulk edits
def bulk_edit(
    file_path: str, operations: List[LineOperation], dry_run: bool = False
) -> Dict[str, Any]:
    """
    Apply multiple operations to a file in one call.

    Args:
        file_path: Path to the file to edit
        operations: List of operations to apply
        dry_run: If True, preview changes without writing

    Returns:
        Dictionary with operation results
    """
    editor = BulkEditor()
    editor.load_file(file_path)
    editor.add_operations(operations)
    return editor.apply(dry_run=dry_run)

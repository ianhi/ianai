"""
Line Operations Module - Modular and composable line editing operations
Provides a clean abstraction for performing single and bulk line operations on files.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass
from enum import Enum


class OperationType(Enum):
    """Enum for different types of line operations."""

    INSERT = "insert"
    REMOVE = "remove"
    CHANGE = "change"
    REPLACE = "replace"


@dataclass
class LineRange:
    """Represents a range of lines in a file."""

    start: int  # 0-indexed, inclusive
    end: Optional[int] = None  # 0-indexed, exclusive (None means single line)

    def __post_init__(self):
        """Validate line range."""
        if self.start < 0:
            raise ValueError("Line range start must be non-negative")
        if self.end is not None and self.end <= self.start:
            raise ValueError("Line range end must be greater than start")

    @property
    def is_single_line(self) -> bool:
        """Check if this range represents a single line."""
        return self.end is None

    @property
    def length(self) -> int:
        """Get the number of lines in this range."""
        if self.is_single_line:
            return 1
        return self.end - self.start

    def contains(self, line_number: int) -> bool:
        """Check if a line number is within this range."""
        if self.is_single_line:
            return line_number == self.start
        return self.start <= line_number < self.end


class LineOperation(ABC):
    """
    Abstract base class for line operations.
    All line operations should inherit from this class.
    """

    def __init__(self, priority: int = 0):
        """
        Initialize a line operation.

        Args:
            priority: Priority for operation ordering (lower = higher priority)
        """
        self.priority = priority

    @abstractmethod
    def apply(self, lines: List[str]) -> List[str]:
        """
        Apply the operation to a list of lines.

        Args:
            lines: List of lines (with newlines preserved)

        Returns:
            Modified list of lines
        """
        pass

    @abstractmethod
    def get_type(self) -> OperationType:
        """Get the type of this operation."""
        pass

    @abstractmethod
    def validate(self, line_count: int) -> bool:
        """
        Validate that this operation can be applied to a file with given line count.

        Args:
            line_count: Number of lines in the file

        Returns:
            True if operation is valid, False otherwise
        """
        pass

    @abstractmethod
    def describe(self) -> str:
        """Get a human-readable description of this operation."""
        pass

    def __lt__(self, other):
        """Compare operations by priority for sorting."""
        return self.priority < other.priority


class InsertLineOperation(LineOperation):
    """Operation to insert one or more lines at a specific position."""

    def __init__(
        self,
        line_number: int,
        content: Union[str, List[str]],
        priority: int = 0,
        preserve_newlines: bool = True,
    ):
        """
        Initialize an insert operation.

        Args:
            line_number: Position to insert at (0-indexed)
            content: Single line or list of lines to insert
            priority: Priority for operation ordering
            preserve_newlines: If True, ensure lines end with newline
        """
        super().__init__(priority)
        self.line_number = line_number
        self.content = [content] if isinstance(content, str) else content
        self.preserve_newlines = preserve_newlines

    def apply(self, lines: List[str]) -> List[str]:
        """Insert content at specified line number."""
        # Ensure line_number is valid
        insert_pos = max(0, min(self.line_number, len(lines)))

        # Prepare content with proper newlines
        content_to_insert = []
        for line in self.content:
            if self.preserve_newlines and not line.endswith("\n"):
                content_to_insert.append(line + "\n")
            else:
                content_to_insert.append(line)

        # Insert the lines
        result = lines[:insert_pos] + content_to_insert + lines[insert_pos:]
        return result

    def validate(self, line_count: int) -> bool:
        """Validate insert operation."""
        # Insert can happen anywhere from 0 to line_count (inclusive)
        return 0 <= self.line_number <= line_count

    def get_type(self) -> OperationType:
        """Get operation type."""
        return OperationType.INSERT

    def describe(self) -> str:
        """Describe the operation."""
        num_lines = len(self.content)
        return f"Insert {num_lines} line(s) at position {self.line_number}"


class RemoveLineOperation(LineOperation):
    """Operation to remove one or more lines."""

    def __init__(
        self, line_range: Union[int, LineRange], count: Optional[int] = None, priority: int = 0
    ):
        """
        Initialize a remove operation.

        Args:
            line_range: Line number or LineRange to remove
            count: Number of lines to remove (if line_range is int)
            priority: Priority for operation ordering
        """
        super().__init__(priority)
        if isinstance(line_range, int):
            if count is not None and count > 1:
                self.range = LineRange(line_range, line_range + count)
            else:
                self.range = LineRange(line_range)
        else:
            self.range = line_range

    def apply(self, lines: List[str]) -> List[str]:
        """Remove lines in specified range."""
        if self.range.is_single_line:
            # Remove single line
            if 0 <= self.range.start < len(lines):
                return lines[: self.range.start] + lines[self.range.start + 1 :]
            return lines
        else:
            # Remove range of lines
            start = max(0, self.range.start)
            end = min(len(lines), self.range.end)
            return lines[:start] + lines[end:]

    def validate(self, line_count: int) -> bool:
        """Validate remove operation."""
        if self.range.is_single_line:
            return 0 <= self.range.start < line_count
        return 0 <= self.range.start < line_count and self.range.end <= line_count

    def get_type(self) -> OperationType:
        """Get operation type."""
        return OperationType.REMOVE

    def describe(self) -> str:
        """Describe the operation."""
        if self.range.is_single_line:
            return f"Remove line {self.range.start}"
        return f"Remove lines {self.range.start} to {self.range.end - 1}"


class ChangeLineOperation(LineOperation):
    """Operation to change one or more lines."""

    def __init__(
        self,
        line_range: Union[int, LineRange],
        new_content: Union[str, List[str]],
        priority: int = 0,
        preserve_newlines: bool = True,
    ):
        """
        Initialize a change operation.

        Args:
            line_range: Line number or LineRange to change
            new_content: New content (single line or list)
            priority: Priority for operation ordering
            preserve_newlines: If True, ensure lines end with newline
        """
        super().__init__(priority)
        if isinstance(line_range, int):
            self.range = LineRange(line_range)
        else:
            self.range = line_range

        self.new_content = (
            [new_content] if isinstance(new_content, str) else new_content
        )
        self.preserve_newlines = preserve_newlines

    def apply(self, lines: List[str]) -> List[str]:
        """Change lines in specified range to new content."""
        # Prepare new content with proper newlines
        content_to_insert = []
        for line in self.new_content:
            if self.preserve_newlines and not line.endswith("\n"):
                content_to_insert.append(line + "\n")
            else:
                content_to_insert.append(line)

        if self.range.is_single_line:
            # Change single line
            if 0 <= self.range.start < len(lines):
                result = lines[: self.range.start] + content_to_insert + lines[self.range.start + 1 :]
                return result
            return lines
        else:
            # Change range of lines
            start = max(0, self.range.start)
            end = min(len(lines), self.range.end)
            return lines[:start] + content_to_insert + lines[end:]

    def validate(self, line_count: int) -> bool:
        """Validate change operation."""
        if self.range.is_single_line:
            return 0 <= self.range.start < line_count
        return 0 <= self.range.start < line_count and self.range.end <= line_count

    def get_type(self) -> OperationType:
        """Get operation type."""
        return OperationType.CHANGE

    def describe(self) -> str:
        """Describe the operation."""
        num_new_lines = len(self.new_content)
        if self.range.is_single_line:
            return f"Change line {self.range.start} to {num_new_lines} line(s)"
        return f"Change lines {self.range.start} to {self.range.end - 1} to {num_new_lines} line(s)"


class ReplacePatternOperation(LineOperation):
    """Operation to replace text pattern in lines."""

    def __init__(
        self,
        pattern: str,
        replacement: str,
        line_range: Optional[LineRange] = None,
        max_replacements: Optional[int] = None,
        regex: bool = False,
        priority: int = 0,
    ):
        """
        Initialize a replace operation.

        Args:
            pattern: Text pattern to find
            replacement: Replacement text
            line_range: Optional range to limit replacement to
            max_replacements: Maximum number of replacements (None = unlimited)
            regex: If True, pattern is a regular expression
            priority: Priority for operation ordering
        """
        super().__init__(priority)
        self.pattern = pattern
        self.replacement = replacement
        self.line_range = line_range
        self.max_replacements = max_replacements
        self.regex = regex

    def apply(self, lines: List[str]) -> List[str]:
        """Replace pattern in lines."""
        import re

        result = []
        replacements_made = 0

        for i, line in enumerate(lines):
            # Check if this line is in range
            if self.line_range and not self.line_range.contains(i):
                result.append(line)
                continue

            # Check if we've hit the max replacements
            if (
                self.max_replacements is not None
                and replacements_made >= self.max_replacements
            ):
                result.append(line)
                continue

            # Perform replacement
            if self.regex:
                if self.max_replacements is not None:
                    remaining = self.max_replacements - replacements_made
                    new_line, count = re.subn(
                        self.pattern, self.replacement, line, count=remaining
                    )
                    replacements_made += count
                else:
                    new_line = re.sub(self.pattern, self.replacement, line)
            else:
                if self.max_replacements is not None:
                    remaining = self.max_replacements - replacements_made
                    new_line = line.replace(self.pattern, self.replacement, remaining)
                    replacements_made += line.count(self.pattern)
                else:
                    new_line = line.replace(self.pattern, self.replacement)

            result.append(new_line)

        return result

    def validate(self, line_count: int) -> bool:
        """Validate replace operation."""
        if self.line_range is None:
            return True
        return (
            0 <= self.line_range.start < line_count
            and (self.line_range.is_single_line or self.line_range.end <= line_count)
        )

    def get_type(self) -> OperationType:
        """Get operation type."""
        return OperationType.REPLACE

    def describe(self) -> str:
        """Describe the operation."""
        range_desc = (
            f" in lines {self.line_range.start}-{self.line_range.end - 1}"
            if self.line_range and not self.line_range.is_single_line
            else f" in line {self.line_range.start}"
            if self.line_range
            else ""
        )
        return f"Replace '{self.pattern}' with '{self.replacement}'{range_desc}"


# Convenience functions for creating operations
def insert_lines(line_number: int, content: Union[str, List[str]], **kwargs) -> InsertLineOperation:
    """Create an insert operation."""
    return InsertLineOperation(line_number, content, **kwargs)


def remove_lines(line_number: int, count: int = 1, **kwargs) -> RemoveLineOperation:
    """Create a remove operation."""
    return RemoveLineOperation(line_number, count=count, **kwargs)


def change_lines(line_number: int, new_content: Union[str, List[str]], **kwargs) -> ChangeLineOperation:
    """Create a change operation for a single line."""
    return ChangeLineOperation(line_number, new_content, **kwargs)


def replace_in_lines(pattern: str, replacement: str, **kwargs) -> ReplacePatternOperation:
    """Create a replace pattern operation."""
    return ReplacePatternOperation(pattern, replacement, **kwargs)

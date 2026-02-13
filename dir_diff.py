"""
Directory Diff Module
Provides diff generation between directories, showing file additions/deletions/modifications.
Part of the file operations toolkit.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from file_diff import DiffGenerator, FileDiff


@dataclass
class DirectoryDiffEntry:
    """Represents a file entry in a directory diff."""

    file_path: str
    status: str  # 'added', 'deleted', 'modified', 'unchanged'
    old_path: Optional[str] = None  # For renamed files
    diff: Optional[FileDiff] = None  # For modified files


@dataclass
class DirectoryDiff:
    """Represents the complete diff between two directories."""

    dir_old: str
    dir_new: str
    entries: List[DirectoryDiffEntry] = field(default_factory=list)

    def get_added_files(self) -> List[str]:
        return [e.file_path for e in self.entries if e.status == "added"]

    def get_deleted_files(self) -> List[str]:
        return [e.file_path for e in self.entries if e.status == "deleted"]

    def get_modified_files(self) -> List[str]:
        return [e.file_path for e in self.entries if e.status == "modified"]

    def get_summary(self) -> Dict[str, int]:
        return {
            "added": len(self.get_added_files()),
            "deleted": len(self.get_deleted_files()),
            "modified": len(self.get_modified_files()),
            "total_files": len(self.entries),
        }


class DirectoryDiffer:
    """Compares two directories and generates diffs."""

    def __init__(
        self,
        diff_generator: Optional[DiffGenerator] = None,
        extensions_filter: Optional[List[str]] = None,
    ):
        """
        Initialize directory differ.

        Args:
            diff_generator: DiffGenerator instance (creates new if None)
            extensions_filter: Only compare files with these extensions (e.g., ['.py', '.txt'])
        """
        self.diff_generator = diff_generator or DiffGenerator()
        self.extensions_filter = extensions_filter

    def _get_relative_paths(self, directory: str) -> Set[str]:
        """
        Get all file paths in directory relative to the directory.

        Args:
            directory: Directory path

        Returns:
            Set of relative file paths
        """
        base_path = Path(directory)
        if not base_path.exists():
            return set()

        relative_paths = set()
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(base_path))

                # Apply extension filter if provided
                if self.extensions_filter:
                    if file_path.suffix not in self.extensions_filter:
                        continue

                relative_paths.add(rel_path)

        return relative_paths

    def diff_directories(self, dir_old: str, dir_new: str) -> DirectoryDiff:
        """
        Generate diff between two directories.

        Args:
            dir_old: Path to original directory
            dir_new: Path to new directory

        Returns:
            DirectoryDiff object
        """
        files_old = self._get_relative_paths(dir_old)
        files_new = self._get_relative_paths(dir_new)

        dir_diff = DirectoryDiff(dir_old=dir_old, dir_new=dir_new)

        # Find deleted files
        for file_path in files_old - files_new:
            dir_diff.entries.append(
                DirectoryDiffEntry(file_path=file_path, status="deleted")
            )

        # Find added files
        for file_path in files_new - files_old:
            dir_diff.entries.append(
                DirectoryDiffEntry(file_path=file_path, status="added")
            )

        # Find modified files and generate diffs
        for file_path in files_old & files_new:
            old_full_path = str(Path(dir_old) / file_path)
            new_full_path = str(Path(dir_new) / file_path)

            file_diff = self.diff_generator.diff_files(old_full_path, new_full_path)

            # Only mark as modified if there are actual changes
            if file_diff.additions > 0 or file_diff.deletions > 0:
                dir_diff.entries.append(
                    DirectoryDiffEntry(
                        file_path=file_path, status="modified", diff=file_diff
                    )
                )
            else:
                dir_diff.entries.append(
                    DirectoryDiffEntry(
                        file_path=file_path, status="unchanged", diff=file_diff
                    )
                )

        return dir_diff

    def format_directory_diff_readable(
        self, dir_diff: DirectoryDiff, include_diffs: bool = False
    ) -> str:
        """
        Format directory diff for human-readable output.

        Args:
            dir_diff: DirectoryDiff object
            include_diffs: Whether to include detailed file diffs

        Returns:
            Formatted directory diff string
        """
        output = []
        output.append(f"Directory Diff: {dir_diff.dir_old} → {dir_diff.dir_new}")
        output.append("=" * 80)

        summary = dir_diff.get_summary()
        output.append(
            f"Summary: +{summary['added']} -{summary['deleted']} "
            f"Δ{summary['modified']} ({summary['total_files']} total)"
        )
        output.append("")

        # Added files
        if added := dir_diff.get_added_files():
            output.append("ADDED FILES:")
            for file_path in sorted(added):
                output.append(f"  + {file_path}")
            output.append("")

        # Deleted files
        if deleted := dir_diff.get_deleted_files():
            output.append("DELETED FILES:")
            for file_path in sorted(deleted):
                output.append(f"  - {file_path}")
            output.append("")

        # Modified files
        if modified := dir_diff.get_modified_files():
            output.append("MODIFIED FILES:")
            for file_path in sorted(modified):
                entry = next(e for e in dir_diff.entries if e.file_path == file_path)
                output.append(f"  Δ {file_path}")
                if entry.diff:
                    stats = self.diff_generator.get_diff_stats(entry.diff)
                    output.append(f"    +{stats['additions']} -{stats['deletions']}")

                    if include_diffs:
                        output.append("    " + "-" * 70)
                        diff_text = self.diff_generator.format_diff_readable(entry.diff)
                        for line in diff_text.split("\n"):
                            output.append(f"    {line}")
                        output.append("")
            output.append("")

        return "\n".join(output)

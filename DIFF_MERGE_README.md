# Diff/Merge Module Documentation

A comprehensive, modular toolkit for file and directory diffing, merging, and patch application. Designed for use by AI assistants and automated systems.

## Overview

The diff/merge module provides five main components:

1. **file_diff.py** - File diffing with unified diff format
2. **dir_diff.py** - Directory-level comparison and analysis
3. **file_merge.py** - Three-way merge with conflict detection
4. **patch_handler.py** - Safe patch application with validation and rollback
5. **diff_merge_api.py** - High-level API integrating all components

## Architecture

```
diff_merge_api.py (High-level API)
    ├── file_diff.py (File diffing)
    ├── dir_diff.py (Directory diffing)
    ├── file_merge.py (Three-way merge)
    └── patch_handler.py (Patch application)
```

All modules are independent and can be used separately, following the modular design principle.

## Quick Start

### Basic File Diff

```python
from diff_merge_api import DiffMergeAPI

api = DiffMergeAPI()

# Compare two files
diff_result = api.diff_files("original.py", "modified.py")
print(f"Changes: +{diff_result['additions']} -{diff_result['deletions']}")

# Get human-readable output
print(api.format_diff_readable("original.py", "modified.py"))
```

### Directory Comparison

```python
# Compare entire directories
dir_result = api.diff_directories("project_v1/", "project_v2/")
print(f"Added: {dir_result['summary']['added']} files")
print(f"Modified: {dir_result['summary']['modified']} files")
print(f"Deleted: {dir_result['summary']['deleted']} files")

# Filter by file type
result = api.diff_directories("src/", "src_new/", extensions_filter=['.py', '.txt'])
```

### Three-Way Merge

```python
# Merge files with conflict detection
merge_result = api.merge_files("base.txt", "version_a.txt", "version_b.txt")

if merge_result['has_conflicts']:
    print(f"Found {merge_result['num_conflicts']} conflicts")
    for i, conflict in enumerate(merge_result['conflicts']):
        print(f"Conflict {i}: {conflict['type']}")
```

### Applying Patches

```python
# Apply a patch with validation
result = api.apply_diff_to_file(
    "target.py",
    "original.py",
    "modified.py",
    dry_run=True  # Preview changes first
)

if result['success']:
    print(f"Backup created at: {result['backup_path']}")
    # Actually apply the patch
    api.apply_diff_to_file("target.py", "original.py", "modified.py")
```

## Module Details

### file_diff.py - File Diffing

Generates unified diffs between two files.

**Key Classes:**
- `DiffGenerator` - Main diff generation engine
- `FileDiff` - Data class representing a diff result
- `DiffLine` - Individual line in a diff

**Key Methods:**

```python
diff_gen = DiffGenerator(context_lines=3)

# Generate diff
file_diff = diff_gen.diff_files("old.txt", "new.txt")

# Get statistics
stats = diff_gen.get_diff_stats(file_diff)
# Returns: {
#     'file_old': str,
#     'file_new': str,
#     'additions': int,
#     'deletions': int,
#     'total_changes': int,
#     'is_binary': bool
# }

# Format for display
readable = diff_gen.format_diff_readable(file_diff)
```

**Features:**
- Handles binary files gracefully
- UTF-8 encoding with fallback handling
- Configurable context lines
- Statistical analysis of changes

### dir_diff.py - Directory Diffing

Compares entire directories and identifies file-level changes.

**Key Classes:**
- `DirectoryDiffer` - Main directory comparison engine
- `DirectoryDiff` - Complete directory diff result
- `DirectoryDiffEntry` - Individual file change entry

**Key Methods:**

```python
differ = DirectoryDiffer(
    diff_generator=diff_gen,
    extensions_filter=['.py', '.txt']  # Optional
)

# Generate directory diff
dir_diff = differ.diff_directories("/path/old", "/path/new")

# Get categorized files
added = dir_diff.get_added_files()
deleted = dir_diff.get_deleted_files()
modified = dir_diff.get_modified_files()

# Get summary
summary = dir_diff.get_summary()
# Returns: {
#     'added': int,
#     'deleted': int,
#     'modified': int,
#     'total_files': int
# }

# Format for display
readable = differ.format_directory_diff_readable(
    dir_diff,
    include_diffs=True  # Show file-level diffs
)
```

**Features:**
- File filtering by extension
- Recursive directory traversal
- File addition/deletion/modification detection
- Detailed statistics per file

### file_merge.py - Three-Way Merge

Performs three-way merge with conflict detection and resolution.

**Key Classes:**
- `ThreeWayMerger` - Main merge engine
- `MergeResult` - Merge result with conflicts
- `MergeConflict` - Individual conflict representation
- `MergeConflictType` - Enum of conflict types

**Key Methods:**

```python
merger = ThreeWayMerger()

# Perform merge
result = merger.merge_files("base.txt", "branch_a.txt", "branch_b.txt")

# Check for conflicts
if result.has_conflicts:
    for conflict in result.conflicts:
        print(f"Type: {conflict.conflict_type}")
        print(f"Base: {conflict.base_content}")
        print(f"Branch A: {conflict.branch_a_content}")
        print(f"Branch B: {conflict.branch_b_content}")

# Resolve conflicts
resolutions = {
    0: 'branch_a',  # Use branch A's version
    1: 'branch_b',  # Use branch B's version
    2: 'both'       # Use both versions
}
resolved = merger.apply_resolutions(result, resolutions)

# Write merged file
merger.write_merged_file(result, "output.txt", resolutions)
```

**Features:**
- Automatic conflict detection
- Multiple resolution strategies
- Three-way merge using sequence matching
- Write merged results to file

### patch_handler.py - Patch Application

Safely applies patches/diffs to files with validation and rollback.

**Key Classes:**
- `PatchHandler` - Main patch application engine
- `PatchResult` - Result of patch application

**Key Methods:**

```python
handler = PatchHandler(
    create_backups=True,
    backup_dir=".backups"
)

# Validate patch before applying
is_valid, issues = handler.validate_patch_applicability("target.py", diff)
if not is_valid:
    print(f"Cannot apply patch: {issues}")

# Dry run to preview changes
success, preview = handler.dry_run("target.py", diff)
print(preview)

# Apply patch
result = handler.apply_diff("target.py", diff)
if result.success:
    print(f"Backup at: {result.backup_path}")

# Rollback if needed
handler.rollback(result)
```

**Features:**
- Patch validation before application
- Dry-run capability for previewing changes
- Automatic backup creation
- Rollback capability
- Error handling and reporting

### diff_merge_api.py - High-Level API

Integrated API combining all components for common workflows.

**Key Methods:**

#### File Operations

```python
api = DiffMergeAPI()

# Compare files
diff = api.diff_files("old.py", "new.py")

# Get summary without full diff
summary = api.get_file_diff_summary("old.py", "new.py")

# Get formatted readable diff
text = api.format_diff_readable("old.py", "new.py")

# Get detailed statistics
stats = api.get_change_statistics("old.py", "new.py")
```

#### Directory Operations

```python
# Compare directories
dir_diff = api.diff_directories("dir1/", "dir2/")

# Compare with file type filter
result = api.diff_directories("dir1/", "dir2/", 
                              extensions_filter=['.py'])

# Get readable output
text = api.format_directory_diff_readable(
    "dir1/", "dir2/",
    include_file_diffs=True
)
```

#### Merge Operations

```python
# Perform merge
result = api.merge_files("base.txt", "a.txt", "b.txt")

# Resolve conflicts
success, msg = api.resolve_merge_conflicts(
    "base.txt", "a.txt", "b.txt",
    resolutions={0: 'branch_a', 1: 'branch_b'}
)
```

#### Patch Operations

```python
# Validate patch
validation = api.validate_patch("target.py", "old.py", "new.py")

# Apply patch with dry run
result = api.apply_diff_to_file(
    "target.py", "old.py", "new.py",
    dry_run=True
)

# Actually apply
result = api.apply_diff_to_file(
    "target.py", "old.py", "new.py"
)
```

## Data Structures

### FileDiff

```python
@dataclass
class FileDiff:
    file_path_old: str
    file_path_new: str
    lines: List[DiffLine]
    additions: int
    deletions: int
    is_binary: bool
```

### MergeResult

```python
@dataclass
class MergeResult:
    merged_lines: List[str]
    conflicts: List[MergeConflict]
    has_conflicts: bool
```

### PatchResult

```python
@dataclass
class PatchResult:
    success: bool
    file_path: str
    original_content: str
    new_content: str
    backup_path: Optional[str]
    error_message: Optional[str]
```

## Error Handling

All modules gracefully handle:
- Missing files
- Binary files
- Permission errors
- Encoding issues
- Merge conflicts
- Invalid inputs

Example:
```python
try:
    diff = api.diff_files("old.py", "new.py")
except Exception as e:
    print(f"Error: {e}")
    # Module handles gracefully, won't crash
```

## Performance Considerations

- **Large files**: Uses streaming where possible
- **Large directories**: Can be optimized with extension filters
- **Context lines**: Reduce for faster diffs on small changes

```python
# Use fewer context lines for performance
diff_gen = DiffGenerator(context_lines=1)
```

## Testing

Run the test suite:

```bash
python -m pytest test_diff_merge.py -v
```

Or using unittest:

```bash
python -m unittest test_diff_merge.py
```

## Integration with AI Tools

The API is designed for easy integration:

```python
# In your tool definition
def diff_files_tool(old_path: str, new_path: str) -> dict:
    api = DiffMergeAPI()
    return api.diff_files(old_path, new_path)

def apply_patch_tool(target: str, old: str, new: str) -> dict:
    api = DiffMergeAPI()
    return api.apply_diff_to_file(target, old, new)
```

## Future Enhancements

Potential additions:
- Ignore patterns (like .gitignore)
- Binary file support with hashing
- Semantic diff for code (AST-aware)
- Parallel directory processing
- Streaming for very large files
- Patch file format support (unified patch format)
- Syntax highlighting in output

## License

Part of the file operations toolkit.

## Author

AI-Generated with manual refinement for modularity and maintainability.

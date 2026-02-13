# Diff/Merge Toolkit - Quick Reference

## Import

```python
from diff_merge_api import DiffMergeAPI
api = DiffMergeAPI()
```

## File Diffing

### Compare two files
```python
diff = api.diff_files("old.py", "new.py")
# Returns: {
#   'additions': int,
#   'deletions': int,
#   'total_changes': int,
#   'is_binary': bool,
#   'diff_lines': [...]
# }
```

### Get summary only
```python
summary = api.get_file_diff_summary("old.py", "new.py")
# Returns: {'additions': int, 'deletions': int, ...}
```

### Get readable output
```python
text = api.format_diff_readable("old.py", "new.py")
# Returns: formatted diff string
```

### Get statistics
```python
stats = api.get_change_statistics("old.py", "new.py")
# Returns: {'additions': int, 'percent_change': '25.0%', ...}
```

## Directory Diffing

### Compare directories
```python
result = api.diff_directories("dir1/", "dir2/")
# Returns: {
#   'summary': {'added': int, 'deleted': int, 'modified': int},
#   'added_files': [...],
#   'deleted_files': [...],
#   'modified_files': [...]
# }
```

### Filter by file type
```python
result = api.diff_directories(
    "dir1/", "dir2/",
    extensions_filter=['.py', '.txt']
)
```

### Get readable output
```python
text = api.format_directory_diff_readable(
    "dir1/", "dir2/",
    include_file_diffs=True
)
```

## Merging

### Three-way merge
```python
result = api.merge_files("base.txt", "a.txt", "b.txt")
# Returns: {
#   'success': bool,
#   'has_conflicts': bool,
#   'num_conflicts': int,
#   'conflicts': [...]
# }
```

### Resolve conflicts
```python
success, msg = api.resolve_merge_conflicts(
    "base.txt", "a.txt", "b.txt",
    resolutions={
        0: 'branch_a',  # Use first option
        1: 'branch_b',  # Use second option
        2: 'both'       # Keep both
    }
)
```

## Patching

### Validate patch
```python
validation = api.validate_patch("target.py", "old.py", "new.py")
# Returns: {'is_applicable': bool, 'issues': [...]}
```

### Dry run
```python
result = api.apply_diff_to_file(
    "target.py", "old.py", "new.py",
    dry_run=True
)
# Returns: {'success': bool, 'preview': str}
```

### Apply patch
```python
result = api.apply_diff_to_file(
    "target.py", "old.py", "new.py"
)
# Returns: {
#   'success': bool,
#   'backup_path': str,
#   'changes': {'additions': int, 'deletions': int}
# }
```

## Common Patterns

### Check if files are identical
```python
diff = api.get_file_diff_summary(file1, file2)
is_identical = diff['total_changes'] == 0
```

### Find heavily modified files
```python
result = api.diff_directories(dir1, dir2)
for entry in result['entries']:
    if entry['status'] == 'modified':
        changes = entry['changes']['additions'] + entry['changes']['deletions']
        print(f"{entry['file_path']}: {changes} lines changed")
```

### Safe patch application
```python
# 1. Validate
if not api.validate_patch(target, old, new)['is_applicable']:
    print("Cannot apply")
    exit()

# 2. Preview
preview = api.apply_diff_to_file(target, old, new, dry_run=True)
print(preview['preview'])

# 3. Apply
result = api.apply_diff_to_file(target, old, new)
if result['success']:
    print(f"Backup: {result['backup_path']}")
```

### Handle merge conflicts
```python
result = api.merge_files(base, a, b)

if result['has_conflicts']:
    for i, conflict in enumerate(result['conflicts']):
        print(f"Conflict {i}: {conflict['type']}")
        print(f"  Base: {conflict['base']}")
        print(f"  A:    {conflict['branch_a']}")
        print(f"  B:    {conflict['branch_b']}")
```

## Low-Level API

### If you need more control, use individual modules:

```python
from file_diff import DiffGenerator
from dir_diff import DirectoryDiffer
from file_merge import ThreeWayMerger
from patch_handler import PatchHandler

# Use each independently
diff_gen = DiffGenerator(context_lines=5)
file_diff = diff_gen.diff_files("old.py", "new.py")

merger = ThreeWayMerger()
result = merger.merge_files("base.txt", "a.txt", "b.txt")

handler = PatchHandler(create_backups=True, backup_dir=".bak")
patch_result = handler.apply_diff("target.py", file_diff)
```

## Return Value Types

### diff_files() result
```python
{
    'file_old': str,
    'file_new': str,
    'additions': int,
    'deletions': int,
    'total_changes': int,
    'is_binary': bool,
    'diff_lines': [
        {
            'type': '+' | '-' | ' ',
            'content': str,
            'line_old': int | None,
            'line_new': int | None
        }
    ]
}
```

### diff_directories() result
```python
{
    'dir_old': str,
    'dir_new': str,
    'summary': {
        'added': int,
        'deleted': int,
        'modified': int,
        'total_files': int
    },
    'added_files': [str],
    'deleted_files': [str],
    'modified_files': [str],
    'entries': [
        {
            'file_path': str,
            'status': 'added' | 'deleted' | 'modified' | 'unchanged',
            'changes': {'additions': int, 'deletions': int} | None
        }
    ]
}
```

### merge_files() result
```python
{
    'success': bool,
    'has_conflicts': bool,
    'num_conflicts': int,
    'conflict_summary': str,
    'conflicts': [
        {
            'type': str,
            'line_number': int,
            'base': str,
            'branch_a': str,
            'branch_b': str
        }
    ]
}
```

### apply_diff_to_file() result
```python
{
    'success': bool,
    'file_path': str,
    'backup_path': str | None,
    'error': str | None,
    'changes': {'additions': int, 'deletions': int} | None
}
```

## Error Handling

```python
try:
    diff = api.diff_files("file1", "file2")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. **For large directories, filter by extension:**
   ```python
   api.diff_directories(dir1, dir2, extensions_filter=['.py'])
   ```

2. **Use summary instead of full diff:**
   ```python
   summary = api.get_file_diff_summary(old, new)  # Fast
   ```

3. **Always dry-run before patching:**
   ```python
   api.apply_diff_to_file(target, old, new, dry_run=True)
   ```

## Configuration

```python
# Custom backup directory
api = DiffMergeAPI(backup_dir=".my_backups")

# Disable backups (not recommended)
api = DiffMergeAPI(create_backups=False)

# More context lines in diff
from file_diff import DiffGenerator
diff_gen = DiffGenerator(context_lines=5)
api.diff_generator = diff_gen
```

## Common Issues

### File is binary
```python
diff = api.get_file_diff_summary("file1", "file2")
if diff['is_binary']:
    print("Cannot diff binary files")
```

### Encoding issues
The API handles UTF-8 with fallback automatically.

### Merge has conflicts
```python
if result['has_conflicts']:
    # Define resolutions
    resolutions = {i: 'branch_a' for i in range(result['num_conflicts'])}
    api.resolve_merge_conflicts(base, a, b, resolutions)
```

### Patch won't apply
```python
validation = api.validate_patch(target, old, new)
if not validation['is_applicable']:
    for issue in validation['issues']:
        print(f"Issue: {issue}")
```

## Files in Toolkit

| File | Purpose | Size |
|------|---------|------|
| `file_diff.py` | File diffing | ~180 lines |
| `dir_diff.py` | Directory diffing | ~160 lines |
| `file_merge.py` | Three-way merge | ~260 lines |
| `patch_handler.py` | Patch application | ~180 lines |
| `diff_merge_api.py` | Unified API | ~320 lines |
| `test_diff_merge.py` | Tests | ~350 lines |
| `DIFF_MERGE_README.md` | Full documentation | ~400 lines |
| `DIFF_MERGE_ARCHITECTURE.md` | Design details | ~350 lines |
| `DIFF_MERGE_USAGE_GUIDE.md` | Practical examples | ~450 lines |

## Next Steps

1. **Copy files** to your project
2. **Import API**: `from diff_merge_api import DiffMergeAPI`
3. **Create instance**: `api = DiffMergeAPI()`
4. **Start using**: `api.diff_files(...)`

See `DIFF_MERGE_README.md` and `DIFF_MERGE_USAGE_GUIDE.md` for detailed documentation.

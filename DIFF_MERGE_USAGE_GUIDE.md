# Diff/Merge Module - Practical Usage Guide

A practical guide with real-world examples of using the diff/merge toolkit.

## Installation & Setup

No installation needed - uses only Python stdlib. Just import:

```python
from diff_merge_api import DiffMergeAPI

api = DiffMergeAPI()
```

## Common Use Cases

### 1. Code Review - Comparing Versions

**Scenario**: You want to see what changed between two versions of a file.

```python
from diff_merge_api import DiffMergeAPI

api = DiffMergeAPI()

# Get the diff
diff = api.diff_files("version_1.0.py", "version_1.1.py")

# Print summary
print(f"Lines added: {diff['additions']}")
print(f"Lines deleted: {diff['deletions']}")
print(f"Total changes: {diff['total_changes']}")

# Print detailed diff
print(api.format_diff_readable("version_1.0.py", "version_1.1.py"))
```

**Output Example**:
```
--- version_1.0.py
+++ version_1.1.py
Changes: +5 -2

  def process_data(data):
-     result = []
-     for item in data:
+     result = None
+     if data:
+         result = []
+         for item in data:
+             result.append(item)
      return result
```

### 2. Project Migration - Directory Comparison

**Scenario**: You refactored a project and want to see what changed overall.

```python
# Compare the whole project
result = api.diff_directories("old_project/", "new_project/")

# Print summary
summary = result['summary']
print(f"Added files: {summary['added']}")
print(f"Deleted files: {summary['deleted']}")
print(f"Modified files: {summary['modified']}")

# List specific changes
print("\nAdded files:")
for file in result['added_files']:
    print(f"  + {file}")

print("\nDeleted files:")
for file in result['deleted_files']:
    print(f"  - {file}")

print("\nModified files:")
for file in result['modified_files']:
    print(f"  Δ {file}")

# Get detailed diff for each modified file
print("\nDetailed changes:")
print(api.format_directory_diff_readable(
    "old_project/", 
    "new_project/",
    include_file_diffs=True
))
```

### 3. Selective Directory Comparison

**Scenario**: You only care about Python files, not generated files or assets.

```python
# Filter to only Python and config files
result = api.diff_directories(
    "src_v1/",
    "src_v2/",
    extensions_filter=['.py', '.yaml', '.json', '.txt']
)

# Now result only includes these file types
for entry in result['entries']:
    print(f"{entry['status']}: {entry['file_path']}")
```

### 4. Merging Parallel Changes

**Scenario**: Two team members modified the same base file independently. Merge their changes.

```python
# Base version (original)
base_file = "config_base.py"

# Developer A's changes
dev_a_file = "config_a.py"

# Developer B's changes
dev_b_file = "config_b.py"

# Perform three-way merge
result = api.merge_files(base_file, dev_a_file, dev_b_file)

if result['success']:
    print("Merge completed without conflicts!")
    print("File is ready to use")
else:
    print(f"Found {result['num_conflicts']} conflicts:")
    for i, conflict in enumerate(result['conflicts']):
        print(f"\nConflict {i+1} at line {conflict['line_number']}:")
        print(f"  Base:     {conflict['base']}")
        print(f"  Dev A:    {conflict['branch_a']}")
        print(f"  Dev B:    {conflict['branch_b']}")
```

### 5. Resolving Merge Conflicts

**Scenario**: After detecting conflicts, you need to resolve them programmatically.

```python
# Perform merge (we know there are conflicts)
merge_result = api.merge_files(base, a, b)

# Define resolutions
resolutions = {
    0: 'branch_a',    # Use first conflict from branch A
    1: 'branch_b',    # Use second conflict from branch B
    2: 'both'         # Keep both versions for third conflict
}

# Apply resolutions
success, message = api.resolve_merge_conflicts(
    base, a, b,
    resolutions=resolutions
)

if success:
    print(f"Merge resolved: {message}")
    # The merged file is now available
else:
    print(f"Error: {message}")
```

### 6. Safe Patch Application

**Scenario**: You have a patch you want to apply, but want to be careful.

```python
# First, validate that the patch can be applied
validation = api.validate_patch(
    "target_file.py",
    "original_file.py",
    "modified_file.py"
)

if not validation['is_applicable']:
    print("Cannot apply patch:")
    for issue in validation['issues']:
        print(f"  - {issue}")
else:
    print("Patch looks good, trying dry run...")
    
    # Dry run to see what would happen
    dry_result = api.apply_diff_to_file(
        "target_file.py",
        "original_file.py",
        "modified_file.py",
        dry_run=True
    )
    
    if dry_result['success']:
        print("Preview of changes:")
        print(dry_result['preview'])
        
        # If happy, actually apply it
        print("\nApplying patch for real...")
        real_result = api.apply_diff_to_file(
            "target_file.py",
            "original_file.py",
            "modified_file.py"
        )
        
        if real_result['success']:
            print(f"✓ Patch applied successfully!")
            print(f"✓ Backup created at: {real_result['backup_path']}")
        else:
            print(f"✗ Error: {real_result['error']}")
```

### 7. Change Statistics & Analysis

**Scenario**: You want detailed statistics about changes.

```python
# Get comprehensive statistics
stats = api.get_change_statistics("old.py", "new.py")

print(f"File: {stats['file_old']} → {stats['file_new']}")
print(f"Additions:    {stats['additions']:3d} lines")
print(f"Deletions:    {stats['deletions']:3d} lines")
print(f"Total change: {stats['total_changes']:3d} lines ({stats['percent_change']})")

# Categorize changes
if stats['percent_change'] < 10:
    print("→ Minimal changes")
elif stats['percent_change'] < 30:
    print("→ Moderate changes")
else:
    print("→ Major refactoring")
```

### 8. Batch Directory Processing

**Scenario**: Process multiple directories and generate a report.

```python
import os
from diff_merge_api import DiffMergeAPI

api = DiffMergeAPI()

# Compare multiple project versions
versions = [
    ("projects/v1.0", "projects/v1.1"),
    ("projects/v1.1", "projects/v1.2"),
    ("projects/v1.2", "projects/v2.0"),
]

print("PROJECT EVOLUTION REPORT")
print("=" * 60)

total_added = 0
total_deleted = 0

for old_dir, new_dir in versions:
    result = api.diff_directories(old_dir, new_dir)
    summary = result['summary']
    
    total_added += summary['added']
    total_deleted += summary['deleted']
    
    print(f"\n{old_dir} → {new_dir}")
    print(f"  Added:    {summary['added']:3d}")
    print(f"  Deleted:  {summary['deleted']:3d}")
    print(f"  Modified: {summary['modified']:3d}")

print("\n" + "=" * 60)
print(f"Total files added:   {total_added}")
print(f"Total files deleted: {total_deleted}")
```

### 9. Finding All Changes in a Large Codebase

**Scenario**: Find what changed in just Python files across a project.

```python
# Only look at Python files
result = api.diff_directories(
    "codebase_v1/",
    "codebase_v2/",
    extensions_filter=['.py']
)

# Find heavily modified files
print("MOST MODIFIED FILES:")
print("-" * 50)

modified = result['entries']
modified.sort(
    key=lambda e: (e['changes']['additions'] + e['changes']['deletions']) 
    if e['changes'] else 0,
    reverse=True
)

for entry in modified[:10]:  # Top 10
    if entry['status'] == 'modified' and entry['changes']:
        total = entry['changes']['additions'] + entry['changes']['deletions']
        print(f"{entry['file_path']}")
        print(f"  +{entry['changes']['additions']} -{entry['changes']['deletions']} (total: {total})")
```

### 10. Automated Testing - Verify No Unwanted Changes

**Scenario**: Ensure a refactoring only changed specific files.

```python
expected_changes = {
    'test_utils.py',
    'utils.py',
    'helpers.py'
}

result = api.diff_directories("src/", "src_refactored/")

modified_files = set(result['modified_files'])
unexpected = modified_files - expected_changes

if unexpected:
    print(f"⚠ WARNING: Unexpected files were modified:")
    for file in unexpected:
        print(f"  - {file}")
else:
    print("✓ Only expected files were modified")

# Also check no files were accidentally deleted
deleted = result['deleted_files']
if deleted:
    print(f"⚠ WARNING: Files were deleted:")
    for file in deleted:
        print(f"  - {file}")
else:
    print("✓ No files deleted")
```

## Advanced Examples

### Custom Diff Output

```python
def generate_html_diff(file_old, file_new):
    """Generate HTML-formatted diff."""
    api = DiffMergeAPI()
    diff_result = api.diff_files(file_old, file_new)
    
    html = ['<table class="diff">']
    
    for line in diff_result['diff_lines']:
        if line['type'] == '+':
            html.append(f'<tr class="added"><td>+{line["content"]}</td></tr>')
        elif line['type'] == '-':
            html.append(f'<tr class="deleted"><td>-{line["content"]}</td></tr>')
        else:
            html.append(f'<tr class="context"><td> {line["content"]}</td></tr>')
    
    html.append('</table>')
    return '\n'.join(html)
```

### Conflict Resolution Helper

```python
def interactive_merge_resolve(base, a, b):
    """Interactively resolve merge conflicts."""
    api = DiffMergeAPI()
    result = api.merge_files(base, a, b)
    
    if not result['has_conflicts']:
        return True
    
    resolutions = {}
    
    for i, conflict in enumerate(result['conflicts']):
        print(f"\nConflict {i+1}/{len(result['conflicts'])}")
        print(f"Base:     {conflict['base']}")
        print(f"Branch A: {conflict['branch_a']}")
        print(f"Branch B: {conflict['branch_b']}")
        
        choice = input("Use (a)ranch_a, (b)ranch_b, or (both)? ").strip().lower()
        
        if choice in ['a', 'branch_a']:
            resolutions[i] = 'branch_a'
        elif choice in ['b', 'branch_b']:
            resolutions[i] = 'branch_b'
        else:
            resolutions[i] = 'both'
    
    success, msg = api.resolve_merge_conflicts(base, a, b, resolutions)
    return success
```

### Change Impact Analysis

```python
def analyze_change_impact(old_file, new_file):
    """Analyze what kind of changes were made."""
    api = DiffMergeAPI()
    stats = api.get_change_statistics(old_file, new_file)
    
    additions = stats['additions']
    deletions = stats['deletions']
    
    if additions == 0 and deletions == 0:
        return "NO_CHANGES"
    elif additions > deletions * 3:
        return "FEATURE_ADDITION"
    elif deletions > additions * 3:
        return "CODE_REMOVAL"
    elif abs(additions - deletions) < 5:
        return "REFACTORING"
    else:
        return "MODIFICATION"

# Usage
impact = analyze_change_impact("old.py", "new.py")
print(f"Change type: {impact}")
```

## Error Handling Patterns

### Graceful Degradation

```python
try:
    diff = api.diff_files("file1.py", "file2.py")
except Exception as e:
    print(f"Could not create diff: {e}")
    # Provide fallback
    print("Files exist" if os.path.exists("file1.py") else "File missing")
```

### Validation Before Action

```python
# Always validate first
validation = api.validate_patch("target.py", "old.py", "new.py")

if validation['is_applicable']:
    result = api.apply_diff_to_file("target.py", "old.py", "new.py")
else:
    print("Cannot apply patch - validation failed")
    for issue in validation['issues']:
        print(f"  Issue: {issue}")
```

## Performance Tips

1. **Filter by extension** for large directories:
   ```python
   api.diff_directories("dir1/", "dir2/", extensions_filter=['.py'])
   ```

2. **Use summaries** instead of full diffs for large files:
   ```python
   summary = api.get_file_diff_summary(old, new)  # Fast
   # vs
   full = api.diff_files(old, new)  # More detailed
   ```

3. **Dry run before applying** to catch issues:
   ```python
   result = api.apply_diff_to_file(target, old, new, dry_run=True)
   ```

## Summary

The diff/merge toolkit provides:
- ✓ Safe file comparisons
- ✓ Directory-level analysis
- ✓ Three-way merge with conflict detection
- ✓ Safe patch application with backups
- ✓ Comprehensive statistics and reporting
- ✓ Flexible configuration and extension

Use it to automate code reviews, migrations, merges, and patch management!

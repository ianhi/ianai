# Diff/Merge Toolkit - Complete Index

A comprehensive file diffing, merging, and patching toolkit for AI-assisted development.

## 📚 Documentation Structure

### Quick Start
- **[DIFF_MERGE_QUICK_REFERENCE.md](DIFF_MERGE_QUICK_REFERENCE.md)** ⭐ START HERE
  - One-page reference
  - Common patterns
  - API cheat sheet
  - Return value types

### Learning Guides
- **[DIFF_MERGE_README.md](DIFF_MERGE_README.md)**
  - Complete API documentation
  - All classes and methods
  - Feature overview
  - Quick start examples

- **[DIFF_MERGE_USAGE_GUIDE.md](DIFF_MERGE_USAGE_GUIDE.md)**
  - 10+ real-world examples
  - Common use cases
  - Advanced patterns
  - Error handling

### Technical Deep Dive
- **[DIFF_MERGE_ARCHITECTURE.md](DIFF_MERGE_ARCHITECTURE.md)**
  - Design principles
  - Module dependencies
  - Data flow diagrams
  - Extension points
  - Future roadmap

### Implementation
- **[DIFF_MERGE_IMPLEMENTATION_SUMMARY.md](DIFF_MERGE_IMPLEMENTATION_SUMMARY.md)**
  - What was built
  - Files created
  - Key features
  - Testing approach
  - Deployment guide

## 📦 Core Modules

### 1. file_diff.py - File Diffing
```python
from file_diff import DiffGenerator

diff_gen = DiffGenerator()
file_diff = diff_gen.diff_files("old.py", "new.py")
```
- Generate unified diffs
- Compare files line-by-line
- Handle binary files
- Get statistics

### 2. dir_diff.py - Directory Diffing
```python
from dir_diff import DirectoryDiffer

differ = DirectoryDiffer()
dir_diff = differ.diff_directories("dir1/", "dir2/")
```
- Compare entire directories
- Detect added/deleted/modified files
- Filter by file type
- Get summary statistics

### 3. file_merge.py - Three-Way Merge
```python
from file_merge import ThreeWayMerger

merger = ThreeWayMerger()
result = merger.merge_files("base.txt", "a.txt", "b.txt")
```
- Perform three-way merge
- Detect conflicts
- Multiple resolution strategies
- Write merged files

### 4. patch_handler.py - Patch Application
```python
from patch_handler import PatchHandler

handler = PatchHandler()
result = handler.apply_diff("target.py", file_diff)
```
- Apply patches safely
- Validate before applying
- Create backups
- Enable rollback

### 5. diff_merge_api.py - Unified API ⭐ USE THIS
```python
from diff_merge_api import DiffMergeAPI

api = DiffMergeAPI()
diff = api.diff_files("old.py", "new.py")
```
- High-level integration
- Simple, intuitive API
- All features accessible
- JSON-ready responses

## 🎯 Common Tasks

### Compare Two Files
```python
from diff_merge_api import DiffMergeAPI
api = DiffMergeAPI()

diff = api.diff_files("old.py", "new.py")
print(f"Changes: +{diff['additions']} -{diff['deletions']}")
```
See: DIFF_MERGE_QUICK_REFERENCE.md → File Diffing

### Compare Directories
```python
result = api.diff_directories("dir1/", "dir2/")
print(f"Added: {len(result['added_files'])} files")
```
See: DIFF_MERGE_USAGE_GUIDE.md → Code Review example

### Merge Parallel Changes
```python
result = api.merge_files("base.txt", "a.txt", "b.txt")
if result['has_conflicts']:
    # Resolve conflicts
    pass
```
See: DIFF_MERGE_USAGE_GUIDE.md → Merging example

### Apply a Patch Safely
```python
# Validate first
if api.validate_patch(target, old, new)['is_applicable']:
    # Preview
    preview = api.apply_diff_to_file(target, old, new, dry_run=True)
    # Apply
    result = api.apply_diff_to_file(target, old, new)
```
See: DIFF_MERGE_USAGE_GUIDE.md → Safe Patch Application

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│   diff_merge_api.py (High-Level API)   │
│  Simple, integrated interface           │
└─────────────────────────────────────────┘
          ↓           ↓            ↓
    ┌─────────┐  ┌──────────┐  ┌────────┐
    │ file_   │  │   dir_   │  │ file_  │
    │ diff.py │  │ diff.py  │  │merge.py│
    └─────────┘  └──────────┘  └────────┘
                      ↓
                ┌──────────────┐
                │patch_handler │
                │    .py       │
                └──────────────┘
```

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Core modules | 5 |
| Total lines of code | ~1,000 |
| Test cases | 30+ |
| Documentation pages | 7 |
| Documentation lines | ~2,000 |
| External dependencies | 0 |
| Python version | 3.6+ |

## ✅ Features

### File Diffing
- ✓ Unified diff format
- ✓ Line-by-line comparison
- ✓ Statistics (additions/deletions)
- ✓ Binary file handling
- ✓ UTF-8 with encoding fallback

### Directory Diffing
- ✓ Recursive scanning
- ✓ File categorization
- ✓ Extension filtering
- ✓ Summary statistics
- ✓ Detailed per-file changes

### Three-Way Merge
- ✓ Conflict detection
- ✓ Multiple strategies
- ✓ Conflict markers
- ✓ Resolution support
- ✓ File writing

### Patch Application
- ✓ Pre-application validation
- ✓ Dry-run preview
- ✓ Automatic backup
- ✓ Rollback capability
- ✓ Error handling

### High-Level API
- ✓ Unified interface
- ✓ Simple method names
- ✓ Flexible parameters
- ✓ JSON-ready responses
- ✓ AI tool ready

## 🚀 Getting Started

### 1. Copy Files
```bash
cp file_diff.py dir_diff.py file_merge.py \
   patch_handler.py diff_merge_api.py /your/project/
```

### 2. Import API
```python
from diff_merge_api import DiffMergeAPI
api = DiffMergeAPI()
```

### 3. Start Using
```python
# Compare files
diff = api.diff_files("old.py", "new.py")

# Compare directories
result = api.diff_directories("dir1/", "dir2/")

# Merge files
merge = api.merge_files("base.txt", "a.txt", "b.txt")

# Apply patches
api.apply_diff_to_file("target.py", "old.py", "new.py")
```

### 4. Read Documentation
- Quick reference: [DIFF_MERGE_QUICK_REFERENCE.md](DIFF_MERGE_QUICK_REFERENCE.md)
- Full guide: [DIFF_MERGE_README.md](DIFF_MERGE_README.md)
- Examples: [DIFF_MERGE_USAGE_GUIDE.md](DIFF_MERGE_USAGE_GUIDE.md)

## 🧪 Testing

```bash
# Run all tests
python -m unittest test_diff_merge.py -v

# Run specific test class
python -m unittest test_diff_merge.TestDiffGenerator -v

# Run specific test
python -m unittest test_diff_merge.TestDiffGenerator.test_diff_identical_files -v
```

## 📚 Documentation Map

| Need | Document |
|------|----------|
| Quick answers | DIFF_MERGE_QUICK_REFERENCE.md |
| How to use | DIFF_MERGE_README.md |
| Real examples | DIFF_MERGE_USAGE_GUIDE.md |
| Design details | DIFF_MERGE_ARCHITECTURE.md |
| What's included | DIFF_MERGE_IMPLEMENTATION_SUMMARY.md |
| API overview | This file (INDEX) |

## 🔍 Use Cases

### Development
- ✓ Code review automation
- ✓ Change tracking
- ✓ Refactoring validation
- ✓ Merge conflict resolution

### DevOps
- ✓ Configuration drift detection
- ✓ Deployment validation
- ✓ Log file comparison
- ✓ Environment sync

### AI Assistance
- ✓ File modification proposals
- ✓ Change analysis
- ✓ Automated merging
- ✓ Code review support

### Quality Assurance
- ✓ Regression testing
- ✓ Change impact analysis
- ✓ Test file comparison
- ✓ Artifact validation

## 💡 Key Concepts

### Diff
A comparison showing what changed between two files. Shows additions (+), deletions (-), and context.

### Directory Diff
A high-level comparison showing which files were added, deleted, or modified between directories.

### Three-Way Merge
Merging three versions: base (original), branch A, and branch B. Automatically detects conflicts.

### Patch
A set of changes that can be applied to a file. Includes validation and backup.

### Conflict
When merging, a conflict occurs when both branches modify the same lines differently.

## 🔧 Integration Examples

### As a Tool Function
```python
def diff_files_tool(old: str, new: str) -> dict:
    """Tool for comparing files."""
    api = DiffMergeAPI()
    return api.diff_files(old, new)
```

### In a Pipeline
```python
def process_changes(old_dir, new_dir):
    api = DiffMergeAPI()
    changes = api.diff_directories(old_dir, new_dir)
    for file in changes['modified_files']:
        # Process each modified file
        pass
```

### With Error Handling
```python
try:
    result = api.diff_files("old.py", "new.py")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error: {e}")
```

## 📋 API Reference

### Diff Methods
- `diff_files(old, new)` → dict
- `get_file_diff_summary(old, new)` → dict
- `format_diff_readable(old, new)` → str
- `get_change_statistics(old, new)` → dict

### Directory Diff Methods
- `diff_directories(dir_old, dir_new, extensions_filter)` → dict
- `format_directory_diff_readable(dir_old, dir_new, include_file_diffs)` → str

### Merge Methods
- `merge_files(base, a, b)` → dict
- `resolve_merge_conflicts(base, a, b, resolutions)` → tuple

### Patch Methods
- `validate_patch(file, old, new)` → dict
- `apply_diff_to_file(file, old, new, dry_run)` → dict

See DIFF_MERGE_QUICK_REFERENCE.md for complete reference.

## 🎓 Learning Path

1. **Start here**: DIFF_MERGE_QUICK_REFERENCE.md (5 min)
2. **Run examples**: DIFF_MERGE_USAGE_GUIDE.md (15 min)
3. **Understand API**: DIFF_MERGE_README.md (20 min)
4. **Deep dive**: DIFF_MERGE_ARCHITECTURE.md (30 min)
5. **Explore code**: Review source files with docstrings (30 min)

## 🐛 Troubleshooting

**Files won't diff?**
- Check files exist
- Check file encoding (UTF-8 supported)
- Binary files will show as binary

**Merge has conflicts?**
- Define resolutions: `{'branch_a'/'branch_b'/'both'}`
- Use interactive resolution helper

**Patch won't apply?**
- Validate first: `api.validate_patch(target, old, new)`
- Try dry-run: `api.apply_diff_to_file(..., dry_run=True)`
- Check backup: In `.backups/` directory

**Performance issues?**
- Filter by extension for directories
- Use summary instead of full diff
- Consider modular approach for huge files

## 📞 Support

- **Quick questions**: See DIFF_MERGE_QUICK_REFERENCE.md
- **How-to**: See DIFF_MERGE_USAGE_GUIDE.md  
- **Technical**: See DIFF_MERGE_ARCHITECTURE.md
- **Examples**: See test_diff_merge.py

## 📝 License

Part of the file operations toolkit.

---

**Ready to use? Start with [DIFF_MERGE_QUICK_REFERENCE.md](DIFF_MERGE_QUICK_REFERENCE.md) →**

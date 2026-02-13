# Diff/Merge Module Architecture

## Design Principles

This module was built following key software engineering principles:

### 1. **Modularity**
Each component is independent and can be used separately:
- `file_diff.py` - Standalone file comparison
- `dir_diff.py` - Standalone directory comparison
- `file_merge.py` - Standalone merge functionality
- `patch_handler.py` - Standalone patch application
- `diff_merge_api.py` - Integration layer (high-level API)

This allows for:
- Easy testing of individual components
- Replacement of components without affecting others
- Reuse in different contexts
- Clear separation of concerns

### 2. **Maintainability**
- **Single Responsibility**: Each class has one primary purpose
- **Clear Interfaces**: Public methods are well-defined
- **Documentation**: Comprehensive docstrings and type hints
- **Error Handling**: Graceful degradation and informative errors
- **Configuration**: Customizable through constructor parameters

### 3. **Extensibility**
The architecture allows easy extensions:
```python
# Custom diff generator with special logic
class CustomDiffGenerator(DiffGenerator):
    def diff_files(self, file_old, file_new):
        # Custom implementation
        pass

# Use in directory differ
differ = DirectoryDiffer(diff_generator=CustomDiffGenerator())
```

### 4. **Safety**
- Backup creation before modifications
- Dry-run capability for previewing changes
- Validation before applying patches
- Rollback functionality

## Module Dependencies

```
difflib (Python stdlib)
pathlib (Python stdlib)
dataclasses (Python stdlib)
enum (Python stdlib)
shutil (Python stdlib)
typing (Python stdlib)
```

No external dependencies - uses only Python standard library.

## Component Details

### file_diff.py
**Purpose**: Generate unified diffs between files
**Size**: ~180 lines
**Key Classes**:
- `DiffLine` - Represents a single diff line
- `FileDiff` - Complete diff result
- `DiffGenerator` - Core diffing engine

**Dependencies**: difflib, pathlib
**Used by**: dir_diff.py, patch_handler.py, diff_merge_api.py

### dir_diff.py
**Purpose**: Compare entire directories
**Size**: ~160 lines
**Key Classes**:
- `DirectoryDiffEntry` - Single file change
- `DirectoryDiff` - Complete directory diff
- `DirectoryDiffer` - Main comparison engine

**Dependencies**: file_diff.py, pathlib
**Used by**: diff_merge_api.py

### file_merge.py
**Purpose**: Three-way merge with conflict detection
**Size**: ~260 lines
**Key Classes**:
- `MergeConflict` - Conflict representation
- `MergeResult` - Merge result
- `ThreeWayMerger` - Merge engine

**Dependencies**: difflib
**Used by**: diff_merge_api.py

### patch_handler.py
**Purpose**: Apply patches safely
**Size**: ~180 lines
**Key Classes**:
- `PatchResult` - Patch application result
- `PatchHandler` - Patch application engine

**Dependencies**: file_diff.py, pathlib, shutil
**Used by**: diff_merge_api.py

### diff_merge_api.py
**Purpose**: High-level integrated API
**Size**: ~320 lines
**Key Classes**:
- `DiffMergeAPI` - Main API class

**Dependencies**: All other modules
**Used by**: External applications, AI tools

## Class Hierarchy

```
DiffMergeAPI (API layer)
├── DiffGenerator
├── DirectoryDiffer
├── ThreeWayMerger
└── PatchHandler

DiffGenerator (file_diff.py)
├── DiffLine
└── FileDiff

DirectoryDiffer (dir_diff.py)
├── DirectoryDiff
├── DirectoryDiffEntry
└── [uses] DiffGenerator

ThreeWayMerger (file_merge.py)
├── MergeResult
└── MergeConflict

PatchHandler (patch_handler.py)
└── PatchResult
```

## Data Flow

### Simple File Diff
```
File A ─→ DiffGenerator.diff_files() ─→ FileDiff object
File B ─→ (uses difflib)            ↓
                              DiffLine[]
```

### Directory Diff
```
Dir A ─→ DirectoryDiffer.diff_directories() ─→ DirectoryDiff
Dir B ─→ (scans files)                    ├── added files
        ─→ DiffGenerator.diff_files()     ├── deleted files
                                         ├── modified files
                                         └── DirectoryDiffEntry[]
```

### Three-Way Merge
```
Base ──→ ThreeWayMerger.merge_files() ──→ MergeResult
Branch A → (uses difflib)              ├── merged_lines[]
Branch B → (analyzes changes)          └── conflicts[]
```

### Patch Application
```
Target ──→ PatchHandler.apply_diff() ──→ PatchResult
Original ─→ DiffGenerator.diff_files() ├── success: bool
Modified ─→ validate & backup        ├── backup_path: str
           └── apply changes         └── error_message: str
```

## Extension Points

### Custom Diff Generator
```python
class SemanticDiffGenerator(DiffGenerator):
    """Diff that understands code structure."""
    def _parse_unified_diff(self, diff_lines, original, new):
        # Parse with AST awareness
        pass

differ = DirectoryDiffer(diff_generator=SemanticDiffGenerator())
```

### Custom Merge Strategy
```python
class SmartMerger(ThreeWayMerger):
    """Merge with special conflict resolution."""
    def _merge_matching_blocks(self, base, a, b, blocks_a, blocks_b):
        # Custom merge logic
        pass

api = DiffMergeAPI()
api.merger = SmartMerger()
```

### Custom Patch Handler
```python
class ConservativePatchHandler(PatchHandler):
    """Only applies patches with high confidence."""
    def validate_patch_applicability(self, file_path, diff):
        # Stricter validation
        pass
```

## Testing Strategy

**Unit Tests** (test_diff_merge.py):
- `TestDiffGenerator` - File diff tests
- `TestDirectoryDiffer` - Directory diff tests
- `TestThreeWayMerger` - Merge tests
- `TestPatchHandler` - Patch application tests
- `TestDiffMergeAPI` - API integration tests

**Test Approach**:
- Temporary files/directories for isolation
- Comprehensive cleanup
- Edge case coverage (binary files, missing files, etc.)

## Performance Characteristics

| Operation | Time Complexity | Space Complexity | Notes |
|-----------|-----------------|-----------------|-------|
| Diff small files | O(n+m) | O(n+m) | Uses difflib |
| Diff large files | O(n+m) | O(n+m) | Memory-efficient |
| Dir scan | O(n) | O(n) | n = file count |
| Three-way merge | O(n+m+k) | O(n+m+k) | n,m,k = sizes |
| Patch application | O(n) | O(n) | n = file size |

## Security Considerations

1. **File Operations**:
   - Validates file paths
   - Checks file existence before processing
   - Handles permission errors gracefully

2. **Backup Management**:
   - Creates backups with unique names
   - Stores in designated directory
   - Automatic cleanup (or manual)

3. **Input Validation**:
   - Encoding detection
   - Binary file detection
   - Size limit awareness (future)

4. **Error Handling**:
   - No arbitrary code execution
   - Safe exception handling
   - Informative error messages

## Configuration Options

```python
# DiffGenerator
DiffGenerator(context_lines=3)

# DirectoryDiffer
DirectoryDiffer(
    diff_generator=None,
    extensions_filter=['.py', '.txt']
)

# PatchHandler
PatchHandler(
    create_backups=True,
    backup_dir=".backups"
)

# ThreeWayMerger
ThreeWayMerger(context_lines=3)

# DiffMergeAPI
DiffMergeAPI(
    create_backups=True,
    backup_dir=".backups"
)
```

## Future Architecture Improvements

### Phase 1: Enhancements
- Ignore pattern support (.gitignore)
- Binary file handling with checksums
- Streaming for very large files
- Progress callbacks for long operations

### Phase 2: Advanced Features
- Semantic diff for code (AST-aware)
- Syntax highlighting in output
- Unified patch format (.patch file) support
- Conflict resolution strategies (auto-merge patterns)

### Phase 3: Performance
- Parallel directory scanning
- Caching of diff results
- Incremental diff tracking
- Database backend for statistics

### Phase 4: Integration
- Git integration layer
- Language-specific diff modes
- IDE plugin architecture
- REST API wrapper

## Maintenance Guidelines

### Adding New Functionality
1. Determine which module it belongs to
2. Add method to appropriate class
3. Add docstring with type hints
4. Update tests
5. Update README

### Modifying Existing Code
1. Don't break the public API
2. Maintain backward compatibility
3. Update documentation
4. Add/update tests
5. Consider extension points

### Code Review Checklist
- [ ] Single responsibility maintained
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Error handling appropriate
- [ ] Tests comprehensive
- [ ] No external dependencies added
- [ ] Documentation updated

## Summary

This architecture provides:
- **Clear separation of concerns** through modular design
- **Easy testing** with independent components
- **Extensibility** through composition and inheritance
- **Safety** through validation and backup mechanisms
- **Maintainability** through documentation and standards
- **Performance** through efficient algorithms
- **Reliability** through comprehensive error handling

The design prioritizes **maintainability and extensibility** over feature complexity, making it ideal for long-term use and future enhancements.

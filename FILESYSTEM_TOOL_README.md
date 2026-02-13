# Filesystem Tool - Safe File Operations for AI Agents

A comprehensive, safe filesystem tool that provides move, rename, delete, copy, and other file management operations with built-in safety features.

## Features

✅ **Safe Operations** - Built-in validation and safety checks
✅ **Path Validation** - Prevents operations outside allowed directories
✅ **System Protection** - Blocks operations on critical system files
✅ **Comprehensive Error Handling** - Detailed error messages
✅ **Both Class and Function APIs** - Use whichever is more convenient
✅ **CLI Interface** - Can be used from command line
✅ **Human-Readable Output** - JSON responses with clear status

## Installation

No external dependencies required - uses Python standard library only.

```bash
# Just copy the file to your project
cp filesystem_tool.py your_project/
```

## Quick Start

### Using Standalone Functions

```python
from filesystem_tool import move_file, rename_file, delete_file, copy_file, create_dir

# Move a file
result = move_file("old/path/file.txt", "new/path/file.txt")
print(result)  # {'success': True, 'message': '...', ...}

# Rename a file
result = rename_file("file.txt", "new_name.txt")

# Copy a file
result = copy_file("source.txt", "destination.txt")

# Delete a file (requires confirm=True for safety)
result = delete_file("unwanted.txt", confirm=True)

# Create a directory
result = create_dir("new/nested/directory", parents=True)
```

### Using the Class API

```python
from filesystem_tool import FilesystemTool

# Initialize the tool
fs = FilesystemTool(safe_mode=True)

# Perform operations
result = fs.move("source.txt", "dest.txt")
result = fs.rename("old_name.txt", "new_name.txt")
result = fs.copy("file.txt", "file_backup.txt")
result = fs.delete("temp.txt", confirm=True)
```

## API Reference

### Core Operations

#### move(src, dst, overwrite=False)
Move a file or directory from src to dst.

```python
fs.move("old/location/file.txt", "new/location/file.txt")
fs.move("old_folder", "new_folder", overwrite=True)
```

**Parameters:**
- `src` (str): Source path
- `dst` (str): Destination path
- `overwrite` (bool): Overwrite if destination exists

**Returns:** Dict with `success`, `message`, `src`, `dst`

---

#### rename(old_path, new_name, overwrite=False)
Rename a file or directory (stays in same parent directory).

```python
fs.rename("old_name.txt", "new_name.txt")
```

**Parameters:**
- `old_path` (str): Current path
- `new_name` (str): New name (just the name, not full path)
- `overwrite` (bool): Overwrite if destination exists

**Returns:** Dict with `success`, `message`, `src`, `dst`

---

#### delete(path, recursive=False, confirm=True)
Delete a file or directory.

```python
# Delete a file
fs.delete("file.txt", confirm=True)

# Delete a directory and its contents
fs.delete("folder", recursive=True, confirm=True)
```

**Parameters:**
- `path` (str): Path to delete
- `recursive` (bool): Delete directories and their contents
- `confirm` (bool): Safety flag - must be True to actually delete

**Returns:** Dict with `success`, `message`, `path`, `was_directory`

---

#### copy(src, dst, overwrite=False)
Copy a file or directory from src to dst.

```python
# Copy a file
fs.copy("original.txt", "copy.txt")

# Copy a directory
fs.copy("source_folder", "backup_folder")
```

**Parameters:**
- `src` (str): Source path
- `dst` (str): Destination path
- `overwrite` (bool): Overwrite if destination exists

**Returns:** Dict with `success`, `message`, `src`, `dst`

---

#### create_directory(path, parents=True, exist_ok=True)
Create a new directory.

```python
# Create nested directories
fs.create_directory("path/to/new/folder", parents=True)
```

**Parameters:**
- `path` (str): Directory path to create
- `parents` (bool): Create parent directories as needed
- `exist_ok` (bool): Don't error if directory already exists

**Returns:** Dict with `success`, `message`, `path`

---

### Information & Search

#### get_info(path)
Get detailed information about a file or directory.

```python
result = fs.get_info("myfile.txt")
# Returns: path, name, parent, is_file, is_directory, size_bytes, 
#          modified_time, created_time, permissions, etc.
```

**Returns:** Dict with comprehensive file/directory information

---

#### search(pattern, directory='.', recursive=True)
Search for files matching a glob pattern.

```python
# Find all Python files
result = fs.search("*.py", recursive=True)

# Find all test files in specific directory
result = fs.search("test_*.py", directory="tests", recursive=False)
```

**Parameters:**
- `pattern` (str): Glob pattern (e.g., '*.py', 'test_*')
- `directory` (str): Directory to search in
- `recursive` (bool): Search in subdirectories

**Returns:** Dict with `match_count` and `matches` list

---

#### exists(path)
Check if a path exists.

```python
result = fs.exists("myfile.txt")
# Returns: {'success': True, 'exists': True, 'is_file': True, ...}
```

**Returns:** Dict with `exists`, `is_file`, `is_directory`

---

#### get_size(path, human_readable=True)
Get the size of a file or directory.

```python
result = fs.get_size("large_file.dat")
# Returns: {'success': True, 'size_bytes': 1048576, 'size_human': '1.00 MB'}

result = fs.get_size("my_folder")  # Gets total size of all files in folder
```

**Parameters:**
- `path` (str): Path to measure
- `human_readable` (bool): Format size in KB, MB, GB, etc.

**Returns:** Dict with `size_bytes` and optionally `size_human`

---

## Safety Features

### Safe Mode (Default: ON)

When `safe_mode=True` (default):

1. **Path Containment**: Operations are restricted to the base path
2. **System File Protection**: Blocks operations on system directories like `/etc/`, `/sys/`, `C:\Windows\`, etc.
3. **Path Validation**: Resolves and validates all paths before operations

```python
# Safe mode enabled (default)
fs = FilesystemTool(base_path="/home/user/project", safe_mode=True)

# This will be blocked
fs.delete("/etc/passwd", confirm=True)  # Raises ValueError
```

### Confirmation Required for Deletion

All delete operations require `confirm=True`:

```python
# This will fail with error
fs.delete("file.txt", confirm=False)

# This works
fs.delete("file.txt", confirm=True)
```

### Overwrite Protection

By default, operations won't overwrite existing files:

```python
# Will fail if destination exists
fs.copy("source.txt", "existing.txt")

# Explicitly allow overwrite
fs.copy("source.txt", "existing.txt", overwrite=True)
```

## Command Line Interface

The tool can be used directly from the command line:

```bash
# Move a file
python filesystem_tool.py move old.txt new.txt

# Rename a file
python filesystem_tool.py rename file.txt newname.txt

# Copy with overwrite
python filesystem_tool.py copy source.txt dest.txt --overwrite

# Delete a file
python filesystem_tool.py delete unwanted.txt --confirm

# Delete a directory
python filesystem_tool.py delete old_folder --recursive --confirm

# Create directory
python filesystem_tool.py mkdir new/nested/folder

# Get file info
python filesystem_tool.py info myfile.txt

# Search for files
python filesystem_tool.py search "*.py" src/

# Check if file exists
python filesystem_tool.py exists myfile.txt

# Get file/directory size
python filesystem_tool.py size large_folder/
```

## Return Format

All operations return a dictionary with a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "path": "/full/path/to/file",
  ... additional operation-specific data ...
}
```

### Error Response
```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

## Examples

### Example 1: Organize Files by Extension

```python
from filesystem_tool import FilesystemTool

fs = FilesystemTool()

# Search for all image files
images = fs.search("*.jpg", recursive=True)

# Create an images directory
fs.create_directory("organized/images")

# Move all images to the new directory
for match in images['matches']:
    source = match['path']
    filename = match['name']
    fs.move(source, f"organized/images/{filename}")
```

### Example 2: Backup Important Files

```python
from filesystem_tool import FilesystemTool

fs = FilesystemTool()

# Create backup directory
fs.create_directory("backups/2024-01-15")

# Find all Python files
python_files = fs.search("*.py", recursive=True)

# Copy each to backup
for match in python_files['matches']:
    if match['is_file']:
        source = match['path']
        dest = f"backups/2024-01-15/{match['name']}"
        fs.copy(source, dest)
```

### Example 3: Clean Up Temporary Files

```python
from filesystem_tool import FilesystemTool

fs = FilesystemTool()

# Find all .tmp files
temp_files = fs.search("*.tmp", recursive=True)

# Delete each one
for match in temp_files['matches']:
    if match['is_file']:
        result = fs.delete(match['path'], confirm=True)
        if result['success']:
            print(f"Deleted: {match['name']}")
```

### Example 4: Get Disk Usage Report

```python
from filesystem_tool import FilesystemTool

fs = FilesystemTool()

# Get info about current directory
info = fs.get_info(".")

print(f"Directory: {info['path']}")
print(f"Total items: {info['item_count']}")

# Get size of each subdirectory
for item in info['items']:
    size_info = fs.get_size(item)
    print(f"{item}: {size_info.get('size_human', 'N/A')}")
```

## Testing

Run the comprehensive test suite:

```bash
python test_filesystem_tool.py
```

The test suite demonstrates all operations including:
- Creating directories and files
- Moving, copying, and renaming
- Searching and getting information
- Safe deletion with confirmations
- Error handling and safety features

## Error Handling

The tool provides detailed error messages:

```python
result = fs.move("nonexistent.txt", "destination.txt")
if not result['success']:
    print(f"Error: {result['error']}")
    # Error: Source path does not exist: nonexistent.txt
```

Common error scenarios:
- Source file doesn't exist
- Destination already exists (without overwrite flag)
- Insufficient permissions
- Path outside safe base directory
- Attempting to delete without confirmation
- System path protection

## Best Practices

1. **Always check the result**: Every operation returns a dict with `success` field
2. **Use safe_mode**: Keep safe_mode enabled unless you have a specific reason
3. **Be explicit with overwrite**: Default is False for safety
4. **Confirm deletions**: Always use `confirm=True` for delete operations
5. **Handle errors gracefully**: Check `result['success']` before proceeding
6. **Use relative paths**: Easier to maintain and more portable

## License

This tool is provided as-is for safe filesystem operations. Feel free to modify and adapt to your needs.

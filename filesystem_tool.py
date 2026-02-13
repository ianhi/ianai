"""
Filesystem Tool - Safe file operations for AI agents
Provides move, rename, delete, copy, and other file management operations
"""

import os
import shutil
import glob
from pathlib import Path
from typing import Dict, List, Optional, Union
import json


class FilesystemTool:
    """
    A safe filesystem tool for AI agents to perform file operations.
    All operations include validation and error handling.
    """
    
    def __init__(self, base_path: Optional[str] = None, safe_mode: bool = True):
        """
        Initialize the filesystem tool.
        
        Args:
            base_path: Optional base directory to restrict operations to
            safe_mode: If True, prevents operations outside base_path and on system files
        """
        self.base_path = Path(base_path).resolve() if base_path else Path.cwd()
        self.safe_mode = safe_mode
        
    def _validate_path(self, path: Union[str, Path]) -> Path:
        """
        Validate that a path is safe to operate on.
        
        Args:
            path: Path to validate
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If path is unsafe
        """
        path = Path(path).resolve()
        
        if self.safe_mode:
            # Check if path is within base_path
            try:
                path.relative_to(self.base_path)
            except ValueError:
                raise ValueError(f"Path {path} is outside the allowed base path {self.base_path}")
            
            # Prevent operations on critical system files
            dangerous_patterns = [
                '/etc/', '/sys/', '/proc/', '/dev/', '/boot/',
                'C:\\Windows\\', 'C:\\Program Files\\', 'C:\\System32\\'
            ]
            path_str = str(path)
            if any(pattern in path_str for pattern in dangerous_patterns):
                raise ValueError(f"Operations on system paths are not allowed: {path}")
        
        return path
    
    def move(self, src: str, dst: str, overwrite: bool = False) -> Dict[str, any]:
        """
        Move a file or directory from src to dst.
        
        Args:
            src: Source path
            dst: Destination path
            overwrite: If True, overwrite destination if it exists
            
        Returns:
            Dictionary with operation status
        """
        try:
            src_path = self._validate_path(src)
            dst_path = self._validate_path(dst)
            
            if not src_path.exists():
                return {
                    'success': False,
                    'error': f'Source path does not exist: {src}'
                }
            
            if dst_path.exists() and not overwrite:
                return {
                    'success': False,
                    'error': f'Destination already exists: {dst}. Use overwrite=True to replace.'
                }
            
            # If destination exists and overwrite is True, remove it first
            if dst_path.exists() and overwrite:
                if dst_path.is_dir():
                    shutil.rmtree(dst_path)
                else:
                    dst_path.unlink()
            
            # Perform the move
            shutil.move(str(src_path), str(dst_path))
            
            return {
                'success': True,
                'message': f'Moved {src} to {dst}',
                'src': str(src_path),
                'dst': str(dst_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error moving file: {str(e)}'
            }
    
    def rename(self, old_path: str, new_name: str, overwrite: bool = False) -> Dict[str, any]:
        """
        Rename a file or directory (stays in same parent directory).
        
        Args:
            old_path: Current path
            new_name: New name (not full path, just the name)
            overwrite: If True, overwrite destination if it exists
            
        Returns:
            Dictionary with operation status
        """
        try:
            old = self._validate_path(old_path)
            
            if not old.exists():
                return {
                    'success': False,
                    'error': f'Path does not exist: {old_path}'
                }
            
            # Create new path in same parent directory
            new = old.parent / new_name
            new = self._validate_path(new)
            
            if new.exists() and not overwrite:
                return {
                    'success': False,
                    'error': f'Destination already exists: {new}. Use overwrite=True to replace.'
                }
            
            # Use move to rename
            return self.move(str(old), str(new), overwrite=overwrite)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error renaming: {str(e)}'
            }
    
    def delete(self, path: str, recursive: bool = False, confirm: bool = True) -> Dict[str, any]:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
            recursive: If True, delete directories and their contents
            confirm: Safety flag that must be True to actually delete
            
        Returns:
            Dictionary with operation status
        """
        try:
            if not confirm:
                return {
                    'success': False,
                    'error': 'Delete operation requires confirm=True for safety'
                }
            
            target = self._validate_path(path)
            
            if not target.exists():
                return {
                    'success': False,
                    'error': f'Path does not exist: {path}'
                }
            
            is_dir = target.is_dir()
            
            if is_dir and not recursive:
                return {
                    'success': False,
                    'error': f'Path is a directory. Use recursive=True to delete directories: {path}'
                }
            
            # Perform deletion
            if is_dir:
                shutil.rmtree(target)
                msg = f'Deleted directory and contents: {path}'
            else:
                target.unlink()
                msg = f'Deleted file: {path}'
            
            return {
                'success': True,
                'message': msg,
                'path': str(target),
                'was_directory': is_dir
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error deleting: {str(e)}'
            }
    
    def copy(self, src: str, dst: str, overwrite: bool = False) -> Dict[str, any]:
        """
        Copy a file or directory from src to dst.
        
        Args:
            src: Source path
            dst: Destination path
            overwrite: If True, overwrite destination if it exists
            
        Returns:
            Dictionary with operation status
        """
        try:
            src_path = self._validate_path(src)
            dst_path = self._validate_path(dst)
            
            if not src_path.exists():
                return {
                    'success': False,
                    'error': f'Source path does not exist: {src}'
                }
            
            if dst_path.exists() and not overwrite:
                return {
                    'success': False,
                    'error': f'Destination already exists: {dst}. Use overwrite=True to replace.'
                }
            
            # If destination exists and overwrite is True, remove it first
            if dst_path.exists() and overwrite:
                if dst_path.is_dir():
                    shutil.rmtree(dst_path)
                else:
                    dst_path.unlink()
            
            # Perform the copy
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
                msg = f'Copied directory {src} to {dst}'
            else:
                shutil.copy2(src_path, dst_path)
                msg = f'Copied file {src} to {dst}'
            
            return {
                'success': True,
                'message': msg,
                'src': str(src_path),
                'dst': str(dst_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error copying: {str(e)}'
            }
    
    def create_directory(self, path: str, parents: bool = True, exist_ok: bool = True) -> Dict[str, any]:
        """
        Create a new directory.
        
        Args:
            path: Directory path to create
            parents: If True, create parent directories as needed
            exist_ok: If True, don't error if directory already exists
            
        Returns:
            Dictionary with operation status
        """
        try:
            dir_path = self._validate_path(path)
            
            dir_path.mkdir(parents=parents, exist_ok=exist_ok)
            
            return {
                'success': True,
                'message': f'Created directory: {path}',
                'path': str(dir_path)
            }
            
        except FileExistsError:
            return {
                'success': False,
                'error': f'Directory already exists: {path}. Use exist_ok=True to ignore.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating directory: {str(e)}'
            }
    
    def get_info(self, path: str) -> Dict[str, any]:
        """
        Get information about a file or directory.
        
        Args:
            path: Path to examine
            
        Returns:
            Dictionary with file/directory information
        """
        try:
            target = self._validate_path(path)
            
            if not target.exists():
                return {
                    'success': False,
                    'error': f'Path does not exist: {path}'
                }
            
            stat = target.stat()
            is_dir = target.is_dir()
            
            info = {
                'success': True,
                'path': str(target),
                'name': target.name,
                'parent': str(target.parent),
                'exists': True,
                'is_file': target.is_file(),
                'is_directory': is_dir,
                'is_symlink': target.is_symlink(),
                'size_bytes': stat.st_size,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'permissions': oct(stat.st_mode)[-3:]
            }
            
            # Add file extension for files
            if target.is_file():
                info['extension'] = target.suffix
            
            # Add item count for directories
            if is_dir:
                try:
                    items = list(target.iterdir())
                    info['item_count'] = len(items)
                    info['items'] = [item.name for item in items]
                except PermissionError:
                    info['item_count'] = 'Permission denied'
            
            return info
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting info: {str(e)}'
            }
    
    def search(self, pattern: str, directory: str = '.', recursive: bool = True) -> Dict[str, any]:
        """
        Search for files matching a pattern.
        
        Args:
            pattern: Glob pattern to search for (e.g., '*.py', 'test_*')
            directory: Directory to search in
            recursive: If True, search recursively in subdirectories
            
        Returns:
            Dictionary with list of matching files
        """
        try:
            search_dir = self._validate_path(directory)
            
            if not search_dir.exists():
                return {
                    'success': False,
                    'error': f'Directory does not exist: {directory}'
                }
            
            if not search_dir.is_dir():
                return {
                    'success': False,
                    'error': f'Path is not a directory: {directory}'
                }
            
            # Perform search
            if recursive:
                matches = list(search_dir.rglob(pattern))
            else:
                matches = list(search_dir.glob(pattern))
            
            # Convert to relative paths for easier reading
            results = []
            for match in matches:
                try:
                    rel_path = match.relative_to(self.base_path)
                except ValueError:
                    rel_path = match
                
                results.append({
                    'path': str(match),
                    'relative_path': str(rel_path),
                    'name': match.name,
                    'is_file': match.is_file(),
                    'is_directory': match.is_dir()
                })
            
            return {
                'success': True,
                'pattern': pattern,
                'directory': str(search_dir),
                'recursive': recursive,
                'match_count': len(results),
                'matches': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error searching: {str(e)}'
            }
    
    def exists(self, path: str) -> Dict[str, any]:
        """
        Check if a path exists.
        
        Args:
            path: Path to check
            
        Returns:
            Dictionary with existence status
        """
        try:
            target = self._validate_path(path)
            exists = target.exists()
            
            result = {
                'success': True,
                'path': str(target),
                'exists': exists
            }
            
            if exists:
                result['is_file'] = target.is_file()
                result['is_directory'] = target.is_dir()
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error checking existence: {str(e)}'
            }
    
    def get_size(self, path: str, human_readable: bool = True) -> Dict[str, any]:
        """
        Get the size of a file or directory.
        
        Args:
            path: Path to measure
            human_readable: If True, format size in KB, MB, GB, etc.
            
        Returns:
            Dictionary with size information
        """
        try:
            target = self._validate_path(path)
            
            if not target.exists():
                return {
                    'success': False,
                    'error': f'Path does not exist: {path}'
                }
            
            # Calculate size
            if target.is_file():
                size_bytes = target.stat().st_size
            else:
                # Sum all files in directory
                size_bytes = sum(f.stat().st_size for f in target.rglob('*') if f.is_file())
            
            result = {
                'success': True,
                'path': str(target),
                'size_bytes': size_bytes
            }
            
            if human_readable:
                result['size_human'] = self._format_size(size_bytes)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting size: {str(e)}'
            }
    
    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Format bytes into human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"


# Standalone functions for easy use
def move_file(src: str, dst: str, overwrite: bool = False, safe_mode: bool = True) -> Dict[str, any]:
    """Move a file or directory."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.move(src, dst, overwrite)


def rename_file(path: str, new_name: str, overwrite: bool = False, safe_mode: bool = True) -> Dict[str, any]:
    """Rename a file or directory."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.rename(path, new_name, overwrite)


def delete_file(path: str, recursive: bool = False, confirm: bool = True, safe_mode: bool = True) -> Dict[str, any]:
    """Delete a file or directory."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.delete(path, recursive, confirm)


def copy_file(src: str, dst: str, overwrite: bool = False, safe_mode: bool = True) -> Dict[str, any]:
    """Copy a file or directory."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.copy(src, dst, overwrite)


def create_dir(path: str, parents: bool = True, exist_ok: bool = True, safe_mode: bool = True) -> Dict[str, any]:
    """Create a directory."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.create_directory(path, parents, exist_ok)


def file_info(path: str, safe_mode: bool = True) -> Dict[str, any]:
    """Get file or directory information."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.get_info(path)


def search_files(pattern: str, directory: str = '.', recursive: bool = True, safe_mode: bool = True) -> Dict[str, any]:
    """Search for files matching a pattern."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.search(pattern, directory, recursive)


def file_exists(path: str, safe_mode: bool = True) -> Dict[str, any]:
    """Check if a file or directory exists."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.exists(path)


def get_file_size(path: str, human_readable: bool = True, safe_mode: bool = True) -> Dict[str, any]:
    """Get file or directory size."""
    fs = FilesystemTool(safe_mode=safe_mode)
    return fs.get_size(path, human_readable)


# CLI interface for testing
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Filesystem Tool - Safe file operations")
        print("\nUsage:")
        print("  python filesystem_tool.py <command> [args...]")
        print("\nCommands:")
        print("  move <src> <dst> [--overwrite]           - Move file/directory")
        print("  rename <path> <new_name> [--overwrite]   - Rename file/directory")
        print("  delete <path> [--recursive] [--confirm]  - Delete file/directory")
        print("  copy <src> <dst> [--overwrite]           - Copy file/directory")
        print("  mkdir <path>                             - Create directory")
        print("  info <path>                              - Get file/directory info")
        print("  search <pattern> [dir] [--no-recursive]  - Search for files")
        print("  exists <path>                            - Check if path exists")
        print("  size <path>                              - Get file/directory size")
        sys.exit(1)
    
    command = sys.argv[1]
    fs = FilesystemTool()
    
    try:
        if command == 'move':
            result = fs.move(sys.argv[2], sys.argv[3], '--overwrite' in sys.argv)
        elif command == 'rename':
            result = fs.rename(sys.argv[2], sys.argv[3], '--overwrite' in sys.argv)
        elif command == 'delete':
            result = fs.delete(sys.argv[2], '--recursive' in sys.argv, '--confirm' in sys.argv)
        elif command == 'copy':
            result = fs.copy(sys.argv[2], sys.argv[3], '--overwrite' in sys.argv)
        elif command == 'mkdir':
            result = fs.create_directory(sys.argv[2])
        elif command == 'info':
            result = fs.get_info(sys.argv[2])
        elif command == 'search':
            dir_arg = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else '.'
            result = fs.search(sys.argv[2], dir_arg, '--no-recursive' not in sys.argv)
        elif command == 'exists':
            result = fs.exists(sys.argv[2])
        elif command == 'size':
            result = fs.get_size(sys.argv[2])
        else:
            result = {'success': False, 'error': f'Unknown command: {command}'}
        
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get('success') else 1)
        
    except IndexError:
        print(f"Error: Insufficient arguments for command '{command}'")
        sys.exit(1)
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}, indent=2))
        sys.exit(1)

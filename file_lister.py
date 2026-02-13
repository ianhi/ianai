import os


class FileLister:
    def __init__(self):
        """Initialize the FileLister."""
        pass

    def list_files(self, directory=".", pattern=None, recursive=False, show_hidden=False):
        """
        List files and directories at the specified path.

        Args:
            directory (str): Directory path to list (default: current directory)
            pattern (str): Optional pattern to filter files (e.g., "*.py", "*.txt")
            recursive (bool): Whether to list files recursively in subdirectories
            show_hidden (bool): Whether to show hidden files (starting with .)

        Returns:
            str: Formatted list of files and directories or error message
        """
        try:
            if not os.path.exists(directory):
                return f"Error: Directory '{directory}' does not exist"

            if not os.path.isdir(directory):
                return f"Error: '{directory}' is not a directory"

            files_list = []
            dirs_list = []

            if recursive:
                # Walk through directory tree
                for root, dirs, files in os.walk(directory):
                    # Filter hidden directories if needed
                    if not show_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        files = [f for f in files if not f.startswith('.')]
                    
                    # Apply pattern filter if specified
                    if pattern:
                        files = [f for f in files if self._match_pattern(f, pattern)]
                    
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), directory)
                        file_size = os.path.getsize(os.path.join(root, file))
                        files_list.append((rel_path, file_size))
                    
                    for dir_name in dirs:
                        rel_path = os.path.relpath(os.path.join(root, dir_name), directory)
                        dirs_list.append(rel_path)
            else:
                # List only direct contents
                items = os.listdir(directory)
                
                # Filter hidden items if needed
                if not show_hidden:
                    items = [item for item in items if not item.startswith('.')]
                
                for item in items:
                    full_path = os.path.join(directory, item)
                    
                    if os.path.isdir(full_path):
                        dirs_list.append(item)
                    else:
                        # Apply pattern filter if specified
                        if pattern and not self._match_pattern(item, pattern):
                            continue
                        
                        file_size = os.path.getsize(full_path)
                        files_list.append((item, file_size))

            # Format the output
            result = f"Contents of '{directory}':\n"
            result += "=" * 50 + "\n\n"
            
            if dirs_list:
                result += "Directories:\n"
                for dir_name in sorted(dirs_list):
                    result += f"  📁 {dir_name}/\n"
                result += "\n"
            
            if files_list:
                result += "Files:\n"
                for file_name, file_size in sorted(files_list):
                    size_str = self._format_size(file_size)
                    result += f"  📄 {file_name} ({size_str})\n"
            
            if not dirs_list and not files_list:
                result += "  (empty or no matching files)\n"
            
            result += "\n" + "=" * 50 + "\n"
            result += f"Total: {len(dirs_list)} directories, {len(files_list)} files"
            
            return result

        except Exception as e:
            return f"Error listing files: {str(e)}"

    def _match_pattern(self, filename, pattern):
        """
        Simple pattern matching for filenames.
        Supports * as wildcard.

        Args:
            filename (str): Name of the file
            pattern (str): Pattern to match (e.g., "*.py", "test_*")

        Returns:
            bool: True if filename matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)

    def _format_size(self, size_bytes):
        """
        Format file size in human-readable format.

        Args:
            size_bytes (int): Size in bytes

        Returns:
            str: Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def get_tools(self):
        """
        Expose available tools for the AI agent.

        Returns:
            dict: Dictionary with tool definitions
        """
        return {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files and directories at the specified path. Can filter by pattern and list recursively.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list (default: current directory '.')",
                            "default": ".",
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Optional pattern to filter files (e.g., '*.py', '*.txt', 'test_*'). Use wildcards (*) to match multiple characters.",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to list files recursively in subdirectories",
                            "default": False,
                        },
                        "show_hidden": {
                            "type": "boolean",
                            "description": "Whether to show hidden files (starting with .)",
                            "default": False,
                        },
                    },
                    "required": [],
                },
            },
        }


# Example usage
if __name__ == "__main__":
    lister = FileLister()

    # List current directory
    print("=== Current Directory ===")
    result = lister.list_files()
    print(result)

    print("\n=== Python Files Only ===")
    result = lister.list_files(pattern="*.py")
    print(result)

    print("\n=== Recursive Listing ===")
    result = lister.list_files(recursive=True)
    print(result)

    print("\n=== With Hidden Files ===")
    result = lister.list_files(show_hidden=True)
    print(result)

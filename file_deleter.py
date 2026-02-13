import os


class FileDeleter:
    def __init__(self):
        """Initialize the FileDeleter."""
        pass

    def delete_file(self, file_path):
        """
        Delete a file at the specified path.

        Args:
            file_path (str): Path to the file to delete

        Returns:
            str: Success message or error message
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found"
            
            if not os.path.isfile(file_path):
                return f"Error: '{file_path}' is not a file (use delete_directory for directories)"
            
            os.remove(file_path)
            return f"Successfully deleted {file_path}"
        except PermissionError:
            return f"Error: Permission denied to delete '{file_path}'"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    def delete_files(self, file_paths):
        """
        Delete multiple files at once.

        Args:
            file_paths (list): List of file paths to delete

        Returns:
            str: Summary of deletion results
        """
        results = []
        success_count = 0
        error_count = 0
        
        for file_path in file_paths:
            result = self.delete_file(file_path)
            if result.startswith("Successfully"):
                success_count += 1
            else:
                error_count += 1
            results.append(result)
        
        summary = f"\n".join(results)
        summary += f"\n\nSummary: {success_count} deleted, {error_count} failed"
        return summary

    def get_tools(self):
        """
        Expose available tools for the AI agent.

        Returns:
            list: List of tool dictionaries with proper schema format.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file at the specified path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to delete",
                            }
                        },
                        "required": ["file_path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_files",
                    "description": "Delete multiple files at once",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of file paths to delete",
                            }
                        },
                        "required": ["file_paths"],
                    },
                },
            },
        ]

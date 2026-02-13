import os
import shutil


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

            if os.path.isfile(file_path):
                os.remove(file_path)
                return f"Successfully deleted file: {file_path}"
            else:
                return f"Error: '{file_path}' is not a file"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    def delete_directory(self, directory_path, recursive=False):
        """
        Delete a directory at the specified path.

        Args:
            directory_path (str): Path to the directory to delete
            recursive (bool): If True, delete directory and all contents. If False, only delete if empty.

        Returns:
            str: Success message or error message
        """
        try:
            if not os.path.exists(directory_path):
                return f"Error: Directory '{directory_path}' not found"

            if not os.path.isdir(directory_path):
                return f"Error: '{directory_path}' is not a directory"

            if recursive:
                shutil.rmtree(directory_path)
                return f"Successfully deleted directory and all contents: {directory_path}"
            else:
                os.rmdir(directory_path)
                return f"Successfully deleted empty directory: {directory_path}"
        except OSError as e:
            if "Directory not empty" in str(e):
                return f"Error: Directory '{directory_path}' is not empty. Use recursive=True to delete non-empty directories."
            return f"Error deleting directory: {str(e)}"
        except Exception as e:
            return f"Error deleting directory: {str(e)}"

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
                    "name": "delete_directory",
                    "description": "Delete a directory at the specified path. Use recursive=True to delete non-empty directories.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Path to the directory to delete",
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "If True, delete directory and all contents. If False, only delete if empty.",
                                "default": False,
                            },
                        },
                        "required": ["directory_path"],
                    },
                },
            },
        ]

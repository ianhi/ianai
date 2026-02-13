import os


class FileEditor:
    def __init__(self):
        """Initialize the FileEditor."""
        pass

    def edit_file(self, file_path, content, mode="w"):
        """
        Edit a file at the specified path by writing content to it.

        Args:
            file_path (str): Relative path to the file to edit
            content (str): Content to write to the file
            mode (str): File opening mode ('w' for overwrite, 'a' for append)

        Returns:
            str: Success message or error message
        """
        try:
            # Create directories if they don't exist
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            with open(file_path, mode, encoding="utf-8") as file:
                file.write(content)
            return f"Successfully edited {file_path}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    def read_file(self, file_path):
        """
        Read content from a file at the specified path.

        Args:
            file_path (str): Relative path to the file to read

        Returns:
            str: File content or error message
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def append_to_file(self, file_path, content):
        """
        Append content to a file at the specified path.

        Args:
            file_path (str): Relative path to the file to append to
            content (str): Content to append to the file

        Returns:
            str: Success message or error message
        """
        return self.edit_file(file_path, content, mode="a")

    def get_tools(self):
        """
        Expose available tools for the AI agent.

        Returns:
            dict: Dictionary with tool definitions for edit_file
        """
        return {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "Edit a file at the specified path by writing content to it",
                "parameters": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to the file to edit",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file",
                    },
                    "mode": {
                        "type": "string",
                        "description": "File opening mode ('w' for overwrite, 'a' for append)",
                        "default": "w",
                    },
                },
            },
        }


# For completeness, here's the get_tools method for read_file as well
def get_read_file_tool():
    """
    Get the tool definition for reading files.
    
    Returns:
        dict: Dictionary with tool definition for read_file
    """
    return {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content from a file at the specified path",
            "parameters": {
                "file_path": {
                    "type": "string",
                    "description": "Relative path to the file to read",
                },
            },
        },
    }


# For completeness, here's the get_tools method for append_to_file as well
def get_append_to_file_tool():
    """
    Get the tool definition for appending to files.
    
    Returns:
        dict: Dictionary with tool definition for append_to_file
    """
    return {
        "type": "function",
        "function": {
            "name": "append_to_file",
            "description": "Append content to a file at the specified path",
            "parameters": {
                "file_path": {
                    "type": "string",
                    "description": "Relative path to the file to append to",
                },
                "content": {
                    "type": "string",
                    "description": "Content to append to the file",
                },
            },
        },
    }
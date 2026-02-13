import os


class FileWriter:
    def __init__(self):
        """Initialize the FileWriter."""
        pass

    def write_file(self, file_path, content, mode="w"):
        """
        Write content to a file at the specified path.

        Args:
            file_path (str): Relative path to the file to write
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
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"

    def get_tools(self):
        """
        Expose available tools for the AI agent.

        Returns:
            list: List of tool dictionaries with name, description, and function.
        """
        return {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file at the specified path",
                "parameters": {
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to the file to write",
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

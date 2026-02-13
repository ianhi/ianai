class FileReader:
    def __init__(self, file_path=None):
        """Initialize the FileReader with an optional file path."""
        self.file_path = file_path

    def read_file(self, file_path=None):
        """
        Read and return the contents of a file.

        Args:
            file_path (str): Path to the file to read. If None, uses initialized path.

        Returns:
            str: Contents of the file or error message.
        """
        path = file_path or self.file_path
        if not path:
            return "Error: No file path provided"

        try:
            with open(path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: File '{path}' not found"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def get_tools(self):
        """
        Expose available tools for the AI agent.

        Returns:
            dict: Tool dictionary with proper schema format.
        """
        return {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read and return the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read",
                        }
                    },
                    "required": ["file_path"],
                },
            },
        }

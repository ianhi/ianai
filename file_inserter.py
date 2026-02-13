class FileInserter:
    def __init__(self, file_reader):
        """
        Initialize the FileInserter with a FileReader instance.

        Args:
            file_reader (FileReader): Instance of FileReader to use for reading files
        """
        self.file_reader = file_reader

    def insert_file_content(self, user_input):
        """
        Replace file references in user input with file content.
        File references are marked with @ symbol followed by file path.

        Args:
            user_input (str): Input string that may contain @file_path references

        Returns:
            str: Processed string with file contents inserted
        """
        import re

        def replace_file_reference(match):
            file_path = match.group(1)
            file_content = self.file_reader.read_file(file_path)

            # If there's an error reading the file, return the error message
            if file_content.startswith("Error"):
                return f"Error reading file {file_path}: {file_content}"

            # Format the content with filename label, backticks, and filename at the end
            return f"{file_path}\n```\n{file_content}\n```\n{file_path}"

        # Pattern to match @filename
        pattern = r"@([^\s]+)"
        result = re.sub(pattern, replace_file_reference, user_input)
        return result

    def get_tools(self):
        """
        Expose available tools for the AI agent.

        Returns:
            list: List of tool dictionaries with name, description, and function.
        """
        return [
            {
                "name": "insert_file_content",
                "description": "Replace @file_path references with file contents formatted with backticks and filename",
                "parameters": {
                    "user_input": {
                        "type": "string",
                        "description": "Input string containing @file_path references to be replaced with file contents",
                    }
                },
            }
        ]

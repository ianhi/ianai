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

    def insert_line(self, file_path, line_number, content):
        """
        Insert a line into a file at the specified line number.

        Args:
            file_path (str): Relative path to the file
            line_number (int): Line number where to insert (0-indexed)
            content (str): Content to insert

        Returns:
            str: Success message or error message
        """
        try:
            # Read all lines from the file
            lines = self.read_file(file_path).splitlines(keepends=True)

            # Ensure line_number is valid
            if line_number < 0:
                line_number = 0
            elif line_number > len(lines):
                line_number = len(lines)

            # Insert the line
            lines.insert(line_number, content + "\n")

            # Write back to file
            return self.edit_file(file_path, "".join(lines))
        except Exception as e:
            return f"Error inserting line: {str(e)}"

    def remove_line(self, file_path, line_number):
        """
        Remove a line from a file at the specified line number.

        Args:
            file_path (str): Relative path to the file
            line_number (int): Line number to remove (0-indexed)

        Returns:
            str: Success message or error message
        """
        try:
            # Read all lines from the file
            lines = self.read_file(file_path).splitlines(keepends=True)

            # Check if line_number is valid
            if line_number < 0 or line_number >= len(lines):
                return f"Error: Line number {line_number} is out of range"

            # Remove the line
            lines.pop(line_number)

            # Write back to file
            return self.edit_file(file_path, "".join(lines))
        except Exception as e:
            return f"Error removing line: {str(e)}"

    def change_line(self, file_path, line_number, new_content):
        """
        Change the content of a specific line in a file.

        Args:
            file_path (str): Relative path to the file
            line_number (int): Line number to change (0-indexed)
            new_content (str): New content for the line

        Returns:
            str: Success message or error message
        """
        try:
            # Read all lines from the file
            lines = self.read_file(file_path).splitlines(keepends=True)

            # Check if line_number is valid
            if line_number < 0 or line_number >= len(lines):
                return f"Error: Line number {line_number} is out of range"

            # Change the line
            lines[line_number] = new_content + "\n"

            # Write back to file
            return self.edit_file(file_path, "".join(lines))
        except Exception as e:
            return f"Error changing line: {str(e)}"

    def get_tools(self):
        """
        Expose available tools for the AI agent.

        Returns:
            dict: Dictionary with tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Edit a file at the specified path by writing content to it",
                    "parameters": {
                        "type": "object",  # ADD THIS
                        "properties": {  # CHANGE: wrap parameters in "properties"
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
                        "required": ["file_path", "content"],  # ADD THIS
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "insert_line",
                    "description": "Insert a line into a file at the specified line number",
                    "parameters": {
                        "type": "object",  # ADD THIS
                        "properties": {  # CHANGE: wrap parameters in "properties"
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number where to insert (0-indexed)",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to insert",
                            },
                        },
                        "required": ["file_path", "line_number", "content"],  # ADD THIS
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_line",
                    "description": "Remove a line from a file at the specified line number",
                    "parameters": {
                        "type": "object",  # ADD THIS
                        "properties": {  # CHANGE: wrap parameters in "properties"
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number to remove (0-indexed)",
                            },
                        },
                        "required": ["file_path", "line_number"],  # ADD THIS
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "change_line",
                    "description": "Change the content of a specific line in a file",
                    "parameters": {
                        "type": "object",  # ADD THIS
                        "properties": {  # CHANGE: wrap parameters in "properties"
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number to change (0-indexed)",
                            },
                            "new_content": {
                                "type": "string",
                                "description": "New content for the line",
                            },
                        },
                        "required": [
                            "file_path",
                            "line_number",
                            "new_content",
                        ],  # ADD THIS
                    },
                },
            },
        ]


# Example usage
if __name__ == "__main__":
    editor = FileEditor()

    # Create a test file
    result = editor.edit_file("example.txt", "Line 1\nLine 2\nLine 3\nLine 4")
    print(result)

    # Show initial content
    content = editor.read_file("example.txt")
    print(f"Initial content:\n{content}")

    # Insert a line at position 2
    result = editor.insert_line("example.txt", 2, "Inserted line")
    print(result)

    # Show content after insertion
    content = editor.read_file("example.txt")
    print(f"After insertion:\n{content}")

    # Change line 1 (0-indexed)
    result = editor.change_line("example.txt", 1, "Changed line")
    print(result)

    # Show content after changing
    content = editor.read_file("example.txt")
    print(f"After changing:\n{content}")

    # Remove line 0
    result = editor.remove_line("example.txt", 0)
    print(result)

    # Show final content
    content = editor.read_file("example.txt")
    print(f"Final content:\n{content}")


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

    def replace_lines(
        self, file_path: str, start_line: int, end_line: int, new_content: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Replace lines in a file by specifying start and end line numbers.

        Args:
            file_path: Path to the file to edit
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            new_content: New content to insert

        Returns:
            Tuple of (success: bool, message: str, diff: Optional[str])
        """
        try:
            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Validate line numbers
            if (
                start_line < 1
                or end_line < 1
                or start_line > len(lines)
                or end_line > len(lines)
            ):
                return (
                    False,
                    f"Line numbers out of range. File has {len(lines)} lines.",
                    None,
                )

            if start_line > end_line:
                return False, "Start line cannot be greater than end line.", None

            # Store original content for diff
            original_lines = lines[:]

            # Replace lines
            lines[start_line - 1 : end_line] = (
                [new_content + "\n"] if new_content else []
            )

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            # Generate diff
            diff = self._generate_diff(original_lines, lines, file_path)

            return (
                True,
                f"Successfully replaced lines {start_line}-{end_line} in {file_path}",
                diff,
            )

        except Exception as e:
            return False, f"Failed to edit file: {str(e)}", None

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
            dict: Dictionary with tool definitions
        """
        return {
            "type": "function",
            "function": {
                "name": "replace_lines",
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


# Example usage
if __name__ == "__main__":
    editor = FileEditor()

    # Edit a file
    result = editor.edit_file("example.txt", "Hello, World!\nThis is an example file.")
    print(result)

    # Read the file
    content = editor.read_file("example.txt")
    print(f"File content:\n{content}")

    # Append to the file
    result = editor.append_to_file("example.txt", "\nAppended content.")
    print(result)

    # Read the updated file
    content = editor.read_file("example.txt")
    print(f"Updated content:\n{content}")

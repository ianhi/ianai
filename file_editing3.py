import os
import difflib

try:
    from python_validator import PythonValidator, has_ruff  # Try to import PythonValidator
except ImportError:
    PythonValidator = None
    has_ruff = lambda: False  # Define as a function that always returns False


class FileEditor:
    def __init__(self):
        """Initialize the FileEditor."""
        self.python_validator = PythonValidator() if PythonValidator else None

    def _generate_diff(self, old_content, new_content, file_path):
        """
        Generate a unified diff between old and new content.

        Args:
            old_content (str): Original file content
            new_content (str): New file content
            file_path (str): Path to the file (for diff header)

        Returns:
            str: Unified diff string
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )

        return "".join(diff)

    def _validate_and_format_python_content(self, content, file_path):
        """
        Validate and format Python content if it's a Python file.
        
        Args:
            content (str): Content to validate and format
            file_path (str): Path of the file
            
        Returns:
            tuple: (new_content, success_bool, error_message)
        """
        if not file_path.endswith('.py'):
            return content, True, ""  # Not Python, skip validation
            
        if not has_ruff():
            return content, True, ""  # Ruff not available, skip validation
            
        if not self.python_validator:
            return content, True, ""  # No validator, skip
            
        try:
            validated_content, success, error_msg = self.python_validator.validate_and_format_python(content)
            if not success:
                return content, False, f"Python validation failed: {error_msg}"
            return validated_content, success, ""
        except Exception as e:
            return content, False, f"Python validation error: {str(e)}"

    def edit_file(self, file_path, content, mode="w"):
        """
        Edit a file at the specified path by writing content to it.
        If it's a Python file and ruff is available, content is validated and formatted.

        Args:
            file_path (str): Relative path to the file to edit
            content (str): Content to write to the file
            mode (str): File opening mode ('w' for overwrite, 'a' for append)

        Returns:
            dict: Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            # Read old content if file exists
            old_content = ""
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    old_content = file.read()

            # Determine new content based on mode
            if mode == "a" and old_content:
                new_content = old_content + content
            else:
                new_content = content

            # If it's a .py file, validate with ruff before writing
            if file_path.endswith('.py'):
                new_content, validation_success, validation_error = self._validate_and_format_python_content(new_content, file_path)
                
                if not validation_success:
                    return {
                        "message": validation_error,
                        "diff": "",
                        "success": False,
                    }

            # Create directories if they don't exist
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # Write the potentially validated+formatted file
            with open(file_path, mode, encoding="utf-8") as file:
                if mode == 'w':
                    file.write(new_content)

            # For files that were originally just appended to, we need the correct final content 
            final_new_content = new_content  
            if mode == 'a':
                with open(file_path, 'r', encoding='utf-8') as file:
                    final_new_content = file.read()

            # Generate diff if needed
            current_new_content = ""
            with open(file_path, "r", encoding="utf-8") as file:
                current_new_content = file.read()

            diff = self._generate_diff(old_content, current_new_content, file_path)

            return {
                "message": f"Successfully edited {file_path}",
                "diff": diff,
                "success": True,
            }
        except Exception as e:
            return {
                "message": f"Error editing file: {str(e)}",
                "diff": "",
                "success": False,
            }

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
            dict: Dictionary with 'message', 'diff', and 'success' keys
        """
        return self.edit_file(file_path, content, mode="a")

    def insert_line(self, file_path, line_number, content):
        """
        Insert a line into a file at the specified line number.
        If it's a Python file and ruff is available, validates with ruff before writing.

        Args:
            file_path (str): Relative path to the file
            line_number (int): Line number where to insert (0-indexed)
            content (str): Content to insert

        Returns:
            dict: Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            # Read all lines from the file
            old_content = self.read_file(file_path)
            if old_content.startswith("Error"):
                return {"message": old_content, "diff": "", "success": False}

            lines = old_content.splitlines(keepends=True)

            # Ensure line_number is valid
            if line_number < 0:
                line_number = 0
            elif line_number > len(lines):
                line_number = len(lines)

            # Insert the line
            lines.insert(line_number, content + "\n")
            new_content = "".join(lines)

            # If it's a Python file, validate with ruff before writing
            if file_path.endswith('.py'):
                new_content, validation_success, validation_error = self._validate_and_format_python_content(new_content, file_path)
                
                if not validation_success:
                    return {
                        "message": validation_error,
                        "diff": "",
                        "success": False,
                    }

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            # Generate diff
            diff = self._generate_diff(old_content, new_content, file_path)

            return {
                "message": f"Successfully inserted line at {line_number} in {file_path}",
                "diff": diff,
                "success": True,
            }
        except Exception as e:
            return {
                "message": f"Error inserting line: {str(e)}",
                "diff": "",
                "success": False,
            }

    def remove_line(self, file_path, line_number):
        """
        Remove a line from a file at the specified line number.
        If it's a Python file and ruff is available, validates with ruff before writing.

        Args:
            file_path (str): Relative path to the file
            line_number (int): Line number to remove (0-indexed)

        Returns:
            dict: Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            # Read all lines from the file
            old_content = self.read_file(file_path)
            if old_content.startswith("Error"):
                return {"message": old_content, "diff": "", "success": False}

            lines = old_content.splitlines(keepends=True)

            # Check if line_number is valid
            if line_number < 0 or line_number >= len(lines):
                return {
                    "message": f"Error: Line number {line_number} is out of range",
                    "diff": "",
                    "success": False,
                }

            # Remove the line
            lines.pop(line_number)
            new_content = "".join(lines)

            # If it's a Python file, validate with ruff before writing
            if file_path.endswith('.py'):
                new_content, validation_success, validation_error = self._validate_and_format_python_content(new_content, file_path)
                
                if not validation_success:
                    return {
                        "message": validation_error,
                        "diff": "",
                        "success": False,
                    }

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            # Generate diff
            diff = self._generate_diff(old_content, new_content, file_path)

            return {
                "message": f"Successfully removed line {line_number} from {file_path}",
                "diff": diff,
                "success": True,
            }
        except Exception as e:
            return {
                "message": f"Error removing line: {str(e)}",
                "diff": "",
                "success": False,
            }

    def change_line(self, file_path, line_number, new_content_line):
        """
        Change the content of a specific line in a file.
        If it's a Python file and ruff is available, validates with ruff before writing.

        Args:
            file_path (str): Relative path to the file
            line_number (int): Line number to change (0-indexed)
            new_content_line (str): New content for the line

        Returns:
            dict: Dictionary with 'message', 'diff', and 'success' keys
        """
        try:
            # Read all lines from the file
            old_content = self.read_file(file_path)
            if old_content.startswith("Error"):
                return {"message": old_content, "diff": "", "success": False}

            lines = old_content.splitlines(keepends=True)

            # Check if line_number is valid
            if line_number < 0 or line_number >= len(lines):
                return {
                    "message": f"Error: Line number {line_number} is out of range",
                    "diff": "",
                    "success": False,
                }

            # Change the line
            lines[line_number] = new_content_line + "\n"
            new_content_full = "".join(lines)

            # If it's a Python file, validate with ruff before writing
            if file_path.endswith('.py'):
                new_content_full, validation_success, validation_error = self._validate_and_format_python_content(new_content_full, file_path)
                
                if not validation_success:
                    return {
                        "message": validation_error,
                        "diff": "",
                        "success": False,
                    }

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content_full)

            # Generate diff
            diff = self._generate_diff(old_content, new_content_full, file_path)

            return {
                "message": f"Successfully changed line {line_number} in {file_path}",
                "diff": diff,
                "success": True,
            }
        except Exception as e:
            return {
                "message": f"Error changing line: {str(e)}",
                "diff": "",
                "success": False,
            }

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
                        "type": "object",
                        "properties": {
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
                        "required": ["file_path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "insert_line",
                    "description": "Insert a line into a file at the specified line number",
                    "parameters": {
                        "type": "object",
                        "properties": {
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
                        "required": ["file_path", "line_number", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_line",
                    "description": "Remove a line from a file at the specified line number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file",
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number to remove (0-indexed)",
                            },
                        },
                        "required": ["file_path", "line_number"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "change_line",
                    "description": "Change the content of a specific line in a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
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
                        ],
                    },
                },
            },
        ]
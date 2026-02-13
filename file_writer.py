import os

try:
    from python_validator import PythonValidator, has_ruff  # Try to import PythonValidator
except ImportError:
    PythonValidator = None
    has_ruff = lambda: False  # Define as a function that always returns False


class FileWriter:
    def __init__(self):
        """Initialize the FileWriter."""
        self.python_validator = PythonValidator() if PythonValidator else None

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

    def write_file(self, file_path, content, mode="w"):
        """
        Write content to a file at the specified path.
        If it's a Python file and ruff is available, content is validated and formatted.

        Args:
            file_path (str): Relative path to the file to write
            content (str): Content to write to the file
            mode (str): File opening mode ('w' for overwrite, 'a' for append)

        Returns:
            str: Success message or error message
        """
        try:
            # If it's a .py file, validate with ruff before writing
            if file_path.endswith('.py'):
                new_content, validation_success, validation_error = self._validate_and_format_python_content(content, file_path)
                
                if not validation_success:
                    return validation_error

                # Use the validated and formatted content instead of the original
                content = new_content

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
                    "type": "object",
                    "properties": {
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
                    "required": ["file_path", "content"],
                },
            },
        }
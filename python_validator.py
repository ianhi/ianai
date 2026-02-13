import ast
import subprocess
import sys

def has_ruff():
    """Check if ruff is available in the environment using uv."""
    try:
        # Try to run ruff via uv (if uv is managing packages)
        result = subprocess.run([sys.executable, '-m', 'ruff', '--version'], 
                              capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


class PythonValidator:
    """Utility class for validating and formatting Python code with ruff."""
    
    def __init__(self):
        self.available = has_ruff()
    
    def is_valid_syntax(self, code: str) -> tuple[bool, str]:
        """
        Basic Python syntax validation using AST to ensure valid Python syntax.
        
        Args:
            code: Python code string to validate
            
        Returns:
            Tuple containing (valid_boolean, error_message)
        """
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            error_msg = f"Python syntax error: Line {e.lineno}, Column {e.offset}, {e.msg}"
            return False, error_msg
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def format_with_ruff(self, code: str) -> tuple[bool, str, str]:
        """
        Format Python code using ruff formatter via subprocess.
        
        Args:
            code: Python code string to format
            
        Returns:
            Tuple containing (success_boolean, formatted_code_or_original, error_message)
        """
        try:
            result = subprocess.run([
                sys.executable, '-m', 'ruff', 'format', '--stdin-filename', 'temp.py'
            ], input=code, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, result.stdout, ""
            else:
                return False, code, f"Ruff formatting failed: {result.stderr}"
        except Exception as e:
            return False, code, f"Error running ruff formatter: {str(e)}"

    def validate_and_format_python(self, code: str) -> tuple[str, bool, str]:
        """
        Primary method to validate and format Python code with ruff.
        
        Args:
            code: Python code to validate and format
            
        Returns:
            Tuple containing (final_code_or_original_if_invalid, success_boolean, error_message)
        """
        if not self.available:
            return code, True, ""  # If ruff not available skip validation/formatting

        # Validate initial syntax first
        is_initially_valid, initial_error = self.is_valid_syntax(code)
        if not is_initially_valid:
            return code, False, initial_error
        
        # Format the code with ruff
        success, formatted_code, format_error = self.format_with_ruff(code)
        
        if not success:
            return code, False, format_error
        
        # Validate the formatted code's syntax too
        is_post_format_valid, post_format_error = self.is_valid_syntax(formatted_code)
        if not is_post_format_valid:
            return code, False, f"Ruff formatter returned invalid code: {post_format_error}"
        
        return formatted_code, True, ""


# Backward compatibility alias
def is_ruff_available() -> bool:
    """Backward compatibility function."""
    return has_ruff()
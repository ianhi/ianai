#!/usr/bin/env python3
"""
File Editor Tool for Coding Agent
================================

This tool allows replacing code blocks in files by line numbers,
then runs ruff formatting and returns a formatted diff.
"""

import subprocess
import tempfile
import os
from typing import Optional, List, Tuple
import difflib


class FileEditorTool:
    """A tool for editing files by line numbers and validating with ruff."""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def replace_lines(self, file_path: str, start_line: int, end_line: int, new_content: str) -> str:
        """
        Replace lines in a file by line numbers.
        
        Args:
            file_path: Path to the file to edit
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            new_content: New content to replace with
            
        Returns:
            Formatted diff showing the changes made
        """
        # Read original file
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Validate line numbers
        if start_line <= 0 or end_line <= 0 or start_line > len(lines) or end_line > len(lines):
            raise ValueError(f"Line numbers out of range. File has {len(lines)} lines")
        if start_line > end_line:
            raise ValueError("Start line cannot be greater than end line")
            
        # Store original content for diff
        original_lines = lines.copy()
        
        # Replace the specified lines
        lines[start_line-1:end_line] = [line + '\n' for line in new_content.split('\n') if line.strip() or line == '']
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.writelines(lines)
            
        # Create diff
        diff = self._create_diff(original_lines, lines)
        return diff
        
    def run_ruff(self, file_path: str) -> Tuple[bool, str]:
        """
        Run ruff on the file and return results.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            # Run ruff check
            result = subprocess.run(
                ['ruff', 'check', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Ruff check timed out"
        except FileNotFoundError:
            return False, "Ruff not found. Please install ruff using 'pip install ruff'"
        except Exception as e:
            return False, f"Error running ruff: {str(e)}"
            
    def _create_diff(self, old_lines: List[str], new_lines: List[str]) -> str:
        """Create a formatted diff between old and new content."""
        differ = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='original',
            tofile='modified',
            lineterm=''
        )
        
        return '\n'.join(differ)

    def process_changes(self, file_path: str, start_line: int, end_line: int, 
                       new_content: str) -> dict:
        """
        Process file changes, run ruff, and return results.
        
        Args:
            file_path: Path to the file to edit
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            new_content: New content to replace with
            
        Returns:
            Dictionary with diff and ruff results
        """
        try:
            # Replace lines
            diff = self.replace_lines(file_path, start_line, end_line, new_content)
            
            # Run ruff
            ruff_success, ruff_output = self.run_ruff(file_path)
            
            return {
                'diff': diff,
                'ruff_success': ruff_success,
                'ruff_output': ruff_output
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'diff': '',
                'ruff_success': False,
                'ruff_output': ''
            }
            

def main():
    """Main function to demonstrate usage."""
    # Example usage
    editor = FileEditorTool()
    
    # Create a sample Python file for testing
    test_file = os.path.join(editor.temp_dir, 'test_file.py')
    
    with open(test_file, 'w') as f:
        f.write('''def hello_world():
    print("Hello, World!")

def calculate_sum(a, b):
    return a + b
    
def bad_formatting():
    x=1
    y=2
    z=x+y
    return z
''')
    
    print("Testing file editor tool:")
    print("=" * 40)
    
    print(f"Original file contents:")
    with open(test_file, 'r') as f:
        print(f.read())
        
    # Test replacement
    result = editor.process_changes(
        test_file, 
        3, 5,  # Replace lines 3-5
        '''def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b'''
    )
    
    print("Diff of changes:")
    print(result['diff'])
    
    print("\nRuff check results:")
    if result['ruff_success']:
        print("✅ No issues found!")
    else:
        print("❌ Issues found:")
        print(result['ruff_output'])
        
    # Show a more complex example
    print("\n" + "=" * 40)  
    print("Example 2 - Multiple replacements:")
    
    result2 = editor.process_changes(
        test_file,
        6, 9,  # Replace lines 6-9
        '''def bad_formatting():
    x = 1
    y = 2
    z = x + y
    return z'''
    )
    
    print("Diff of changes:")
    print(result2['diff'])
    
    print("\nRuff check results:")
    if result2['ruff_success']:
        print("✅ No issues found!")
    else:
        print("❌ Issues found:")
        print(result2['ruff_output'])


if __name__ == "__main__":
    main()
from __future__ import annotations
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional
from datetime import datetime
import json
from filehandler import FileHandler


class CodeExtractor:
    """Extracts and manages Python code blocks from responses."""

    OUTPUT_DIR = Path("./generated_versions")
    PYTHON_BLOCK_PATTERN = r"```python\n(.*?)\n```"
    CODE_BLOCK_PATTERN = r"```(\w+)?\n(.*?)\n```"

    def __init__(self):
        """Initialize the extractor and create output directory."""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.version_counter = self._get_next_version()

    def _get_next_version(self) -> int:
        """Get the next version number based on existing files."""
        existing_files = list(self.OUTPUT_DIR.glob("main_v*.py"))
        if not existing_files:
            return 1

        versions = []
        for f in existing_files:
            match = re.search(r"main_v(\d+)\.py", f.name)
            if match:
                versions.append(int(match.group(1)))

        return max(versions) + 1 if versions else 1

    def extract_code_blocks(
        self, text: str, language: str = "python"
    ) -> list[tuple[int, str]]:
        """
        Extract code blocks from text by language.
        Returns list of tuples: (block_number, code_content)
        """
        if language.lower() == "python":
            pattern = self.PYTHON_BLOCK_PATTERN
        else:
            pattern = self.CODE_BLOCK_PATTERN

        blocks = re.findall(pattern, text, re.DOTALL)
        return [(i + 1, block) for i, block in enumerate(blocks)]

    def extract_all_code_blocks(self, text: str) -> dict[str, list[tuple[int, str]]]:
        """Extract all code blocks organized by language."""
        matches = re.findall(r"```(\w+)?\n(.*?)\n```", text, re.DOTALL)

        blocks_by_lang = {}
        for lang, code in matches:
            language = lang if lang else "unknown"
            if language not in blocks_by_lang:
                blocks_by_lang[language] = []
            blocks_by_lang[language].append(code)

        return {
            lang: [(i + 1, code) for i, code in enumerate(codes)]
            for lang, codes in blocks_by_lang.items()
        }

    def save_code_block(self, code: str, description: str = "") -> Path:
        """
        Save a code block to a versioned file.
        Returns the path to the saved file.
        """
        filename = f"main_v{self.version_counter}.py"
        file_path = self.OUTPUT_DIR / filename

        # Add header with metadata
        header = self._create_file_header(description)
        full_content = header + code

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_content)

            self.version_counter += 1
            return file_path
        except IOError as e:
            print(f"Error saving file: {e}")
            return None

    @staticmethod
    def _create_file_header(description: str) -> str:
        """Create a file header with metadata."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"# Generated on {timestamp}\n"
        if description:
            header += f"# Description: {description}\n"
        header += "\n"
        return header


class UIFormatter:
    """Handles all UI formatting and display."""

    # Colors and styling
    SEPARATOR_CHAR = "═"
    SEPARATOR_LENGTH = 80

    # ANSI color codes
    COLORS = {
        "user": "\033[94m",  # Blue
        "assistant": "\033[92m",  # Green
        "system": "\033[93m",  # Yellow
        "error": "\033[91m",  # Red
        "success": "\033[95m",  # Magenta
        "reset": "\033[0m",  # Reset
        "bold": "\033[1m",  # Bold
    }

    @staticmethod
    def print_separator(title: str = "", char: str = "═") -> None:
        """Print a formatted separator line with optional title."""
        total_length = UIFormatter.SEPARATOR_LENGTH

        if title:
            title = f" {title} "
            side_length = (total_length - len(title)) // 2
            left_side = char * side_length
            right_side = char * (total_length - len(title) - side_length)
            print(f"{left_side}{title}{right_side}")
        else:
            print(char * total_length)

    @staticmethod
    def print_user_message(message: str, show_raw: bool = False) -> None:
        """Print user message with formatting.

        Args:
            message: The message to display
            show_raw: If True, shows the raw input; if False, shows sanitized version
        """
        UIFormatter.print_separator("YOU", "─")
        print(f"{UIFormatter.COLORS['user']}{message}{UIFormatter.COLORS['reset']}")
        UIFormatter.print_separator()

    @staticmethod
    def print_assistant_message(message: str) -> None:
        """Print assistant message with formatting."""
        UIFormatter.print_separator("ASSISTANT", "─")
        print(
            f"{UIFormatter.COLORS['assistant']}{message}{UIFormatter.COLORS['reset']}"
        )
        UIFormatter.print_separator()

    @staticmethod
    def print_system_message(message: str) -> None:
        """Print system message with formatting."""
        UIFormatter.print_separator("SYSTEM", "─")
        print(f"{UIFormatter.COLORS['system']}{message}{UIFormatter.COLORS['reset']}")
        UIFormatter.print_separator()

    @staticmethod
    def print_error_message(message: str) -> None:
        """Print error message with formatting."""
        print(
            f"{UIFormatter.COLORS['error']}{UIFormatter.COLORS['bold']}ERROR: {message}{UIFormatter.COLORS['reset']}"
        )

    @staticmethod
    def print_success_message(message: str) -> None:
        """Print success message with formatting."""
        print(
            f"{UIFormatter.COLORS['success']}{UIFormatter.COLORS['bold']}✓ {message}{UIFormatter.COLORS['reset']}"
        )

    @staticmethod
    def print_file_contents(contents: str, filename: str = "FILE CONTENTS") -> None:
        """Display file contents in a formatted way."""
        UIFormatter.print_separator(filename, "═")
        print(contents)
        UIFormatter.print_separator()

    @staticmethod
    def get_user_input(prompt: str = "") -> str:
        """Get user input with visual separator."""
        if not prompt:
            prompt = "You"
        print(
            f"\n{UIFormatter.COLORS['user']}{UIFormatter.COLORS['bold']}➜ {prompt}:{UIFormatter.COLORS['reset']} ",
            end="",
        )
        return input().strip()

    @staticmethod
    def print_code_blocks(
        blocks: list[tuple[int, str]], language: str = "python"
    ) -> None:
        """Display extracted code blocks."""
        print(
            f"\n{UIFormatter.COLORS['system']}Found {len(blocks)} {language} code block(s):{UIFormatter.COLORS['reset']}\n"
        )

        for block_num, _ in blocks:
            print(f"  [{block_num}] {language.capitalize()} code block")

    @staticmethod
    def print_write_result(result: dict) -> None:
        """Display write tool result."""
        if result["success"]:
            UIFormatter.print_success_message(result["message"])
            print(f"  Path: {result['file_path']}")
            if "size_bytes" in result:
                print(f"  Size: {result['size_bytes']} bytes")
        else:
            UIFormatter.print_error_message(result["message"])


class UserInterface:
    """Handles user interactions and prompts."""

    def __init__(self):
        self.formatter = UIFormatter()
        self.current_file_path: Optional[Path] = None

    def ask_for_permission(self, file_path: str) -> bool:
        """Ask user for permission to read file."""
        while True:
            response = (
                input(f"Do you want to read the file '{file_path}'? (y/n): ")
                .strip()
                .lower()
            )
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no"):
                return False
            print("Please enter 'y' or 'n'.")

    def get_file_path(self) -> Optional[Path]:
        """Prompt user for a valid file path with validation."""
        while True:
            file_path = input("Enter the path of the file you want to read: ").strip()

            if not file_path:
                self.formatter.print_error_message("File path cannot be empty.")
                continue

            validated_path = FileHandler.validate_path(file_path)
            if validated_path:
                self.current_file_path = validated_path
                return validated_path

    def process_user_input(self, user_input: str) -> tuple[str, Optional[Path]]:
        """
        Process user input to check for file loading with @ syntax.
        Returns tuple of (processed_message, file_path_if_any)

        Examples:
            "@path/to/file.py" -> loads file and returns ("", file_path)
            "question here" -> returns ("question here", None)
            "question @file.py more" -> loads file, returns ("question here more", file_path)
        """
        # Check if input contains @ file reference
        if "@" in user_input:
            # Extract file path from @...
            match = re.search(r"@([^\s]+)", user_input)
            if match:
                file_ref = match.group(1)
                validated_path = FileHandler.validate_path(file_ref)

                if validated_path:
                    self.current_file_path = validated_path
                    # Remove the @file reference from the message
                    processed_message = re.sub(r"@\S+", "", user_input).strip()
                    return (processed_message, validated_path)
                else:
                    self.formatter.print_error_message(
                        f"Could not load file: {file_ref}"
                    )
                    return (user_input, None)

        return (user_input, None)

    def display_file_contents(self, contents: str, filename: str) -> None:
        """Display file contents in a formatted way."""
        self.formatter.print_file_contents(contents, filename)

    def is_exit_command(self, text: str) -> bool:
        """Check if user wants to exit."""
        return text.lower() in ["exit", "quit", "bye", "q"]

    def handle_code_extraction(self, response: str) -> None:
        """Handle code block extraction from response with multiple selection."""
        blocks = self.code_extractor.extract_code_blocks(response)

        if not blocks:
            return

        self.formatter.print_code_blocks(blocks)

        if len(blocks) == 1:
            # Only one block - auto-prompt to save
            choice = (
                input(
                    f"\n{UIFormatter.COLORS['system']}Save this code block to file? (y/n): {UIFormatter.COLORS['reset']}"
                )
                .strip()
                .lower()
            )

            if choice in ("y", "yes"):
                description = input(
                    f"{UIFormatter.COLORS['system']}Brief description (optional): {UIFormatter.COLORS['reset']}"
                ).strip()
                self._save_block(blocks[0], description)
        else:
            # Multiple blocks - let user select multiple
            selected_blocks = []
            print(
                f"\n{UIFormatter.COLORS['system']}Select blocks to save (e.g., '1,2,3' or '1-3' or 'a' for all):{UIFormatter.COLORS['reset']}"
            )

            while True:
                choice = (
                    input(
                        f"{UIFormatter.COLORS['system']}Block numbers (or 's' to skip): {UIFormatter.COLORS['reset']}"
                    )
                    .strip()
                    .lower()
                )

                if choice == "s":
                    break

                if choice == "a":
                    selected_blocks = list(range(len(blocks)))
                    break

                # Parse comma/dash separated numbers
                try:
                    block_indices = []
                    for part in choice.split(","):
                        part = part.strip()
                        if "-" in part:
                            start, end = part.split("-")
                            block_indices.extend(range(int(start) - 1, int(end)))
                        else:
                            block_indices.append(int(part) - 1)

                    # Validate indices
                    if all(0 <= idx < len(blocks) for idx in block_indices):
                        selected_blocks = list(set(block_indices))  # Remove duplicates
                        break
                    else:
                        print(f"Please enter numbers between 1 and {len(blocks)}")
                except (ValueError, AttributeError):
                    print("Invalid input. Use '1,2,3' or '1-3' or 'a' for all")

            # Save selected blocks
            if selected_blocks:
                description = input(
                    f"{UIFormatter.COLORS['system']}Brief description (optional): {UIFormatter.COLORS['reset']}"
                ).strip()

                for idx in sorted(selected_blocks):
                    self._save_block(blocks[idx], f"{description} (block {idx + 1})")

    def _save_block(self, block: tuple[int, str], description: str = "") -> None:
        """Save a code block to file."""
        file_path = self.code_extractor.save_code_block(block[1], description)

        if file_path:
            self.formatter.print_system_message(f"Code block saved to: {file_path}")
        else:
            self.formatter.print_error_message("Failed to save code block")

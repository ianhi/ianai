# Generated on 2026-02-13 04:33:44

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
from writetool import WriteTool


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
        self.code_extractor = CodeExtractor()
        self.write_tool = WriteTool()
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


class OpenAIHandler:
    """Manages OpenAI API interactions."""

    DEFAULT_MODEL = "qwen/qwen3-coder-flash"

    def __init__(self, write_tool: WriteTool):
        """Initialize OpenAI client with API key from environment."""
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set.")

        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)
        self.write_tool = write_tool
        self.tools = self._define_tools()

    def _define_tools(self) -> list:
        """Define available tools for the AI model."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file. The file will be saved in the ai_generated_files directory. Perfect for saving improved code, configurations, documentation, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file to write (e.g., 'improved_code.py', 'config.json'). Can include subdirectories.",
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to write to the file",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of what the file contains or its purpose",
                            },
                            "allow_overwrite": {
                                "type": "boolean",
                                "description": "Whether to overwrite if file already exists (default: false)",
                            },
                        },
                        "required": ["filename", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "append_to_file",
                    "description": "Append content to an existing file. File must exist or use write_file instead.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the existing file to append to",
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to append to the file",
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of what was appended",
                            },
                        },
                        "required": ["filename", "content"],
                    },
                },
            },
        ]

    def analyze_code(self, file_contents: str, file_name: str = "") -> str:
        """Get initial analysis of code from AI."""
        messages = [
            {
                "role": "system",
                "content": "You are an expert coder working as a co-programmer to develop an AI agent. You have access to write_file and append_to_file tools that allow you to save files directly. When you generate code or configuration files, use these tools to save them automatically.",
            },
            {"role": "user", "content": file_contents},
        ]

        return self._send_message(messages)

    def chat(self, messages: list) -> tuple[str, list]:
        """Send message and get response, returning response and updated messages."""
        response, tool_calls = self._send_message_with_tools(messages)
        messages.append({"role": "assistant", "content": response})

        # Process any tool calls
        if tool_calls:
            tool_results = []
            for tool_call in tool_calls:
                result = self._process_tool_call(tool_call, messages)
                tool_results.append(result)

            # Display tool results to user
            for result in tool_results:
                if result["success"]:
                    UIFormatter.print_write_result(result)

        return response, messages

    def _send_message(self, messages: list) -> str:
        """Send message to API and return response content."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"API communication error: {e}")

    def _send_message_with_tools(self, messages: list) -> tuple[str, list]:
        """Send message with tools and return response content and tool calls."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
            )

            tool_calls = []
            content = response.choices[0].message.content or ""

            # Extract tool calls if present
            if hasattr(response.choices[0].message, "tool_calls"):
                tool_calls = response.choices[0].message.tool_calls

            return content, tool_calls
        except Exception as e:
            raise RuntimeError(f"API communication error: {e}")

    def _process_tool_call(self, tool_call, messages: list) -> dict:
        """Process a tool call from the AI model and return result."""
        try:
            args = json.loads(tool_call.function.arguments)

            if tool_call.function.name == "write_file":
                result = self.write_tool.write_file(
                    filename=args.get("filename"),
                    content=args.get("content"),
                    description=args.get("description", ""),
                    allow_overwrite=args.get("allow_overwrite", False),
                )

            elif tool_call.function.name == "append_to_file":
                result = self.write_tool.append_to_file(
                    filename=args.get("filename"),
                    content=args.get("content"),
                    description=args.get("description", ""),
                )
            else:
                result = {
                    "success": False,
                    "message": f"Unknown tool: {tool_call.function.name}",
                }

            # Add tool result to messages for context
            messages.append(
                {
                    "role": "user",
                    "content": f"Tool result: {json.dumps(result)}",
                }
            )

            return result
        except (json.JSONDecodeError, KeyError) as e:
            error_result = {
                "success": False,
                "message": f"Tool error: Invalid arguments - {str(e)}",
            }
            messages.append(
                {
                    "role": "user",
                    "content": f"Tool error: {str(e)}",
                }
            )
            return error_result


class AICodeReviewAgent:
    """Main agent orchestrating the code review workflow."""

    def __init__(self):
        """Initialize the agent with required handlers."""
        self.ui = UserInterface()
        self.formatter = UIFormatter()
        self.openai = OpenAIHandler(self.ui.write_tool)

    def run(self) -> None:
        """Execute the main workflow."""
        try:
            self.formatter.print_system_message(
                "AI Code Review Agent Started\n"
                "You can:\n"
                "  • Ask questions or give feedback\n"
                "  • Load a file with @path/to/file.py syntax\n"
                "  • Type 'exit' to quit"
            )

            # Initialize conversation with optional file
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert coder working as a co-programmer. You have access to write_file and append_to_file tools. Use them to save any code improvements, documentation, tests, or configuration files you suggest.",
                },
            ]

            file_contents = None
            file_name = ""

            # Check if a file was provided on startup
            initial_input = self.formatter.get_user_input(
                "Start (enter question or @file.py to load)"
            )

            if self.ui.is_exit_command(initial_input):
                self.formatter.print_system_message("Goodbye!")
                return

            processed_input, file_path = self.ui.process_user_input(initial_input)

            if file_path:
                # Load file
                file_name = file_path.name
                file_contents = FileHandler.read_file(file_path)
                if not file_contents:
                    self.formatter.print_error_message(
                        f"Failed to read file: {file_path}"
                    )
                    return

                self.ui.display_file_contents(file_contents, file_name)

                # Initial analysis
                self.formatter.print_system_message("Analyzing code...")
                analysis = self.openai.analyze_code(file_contents, file_name)
                self.formatter.print_assistant_message(analysis)
                self.ui.handle_code_extraction(analysis)

                # Add to messages
                messages.extend(
                    [
                        {
                            "role": "user",
                            "content": f"Please analyze and suggest improvements for the following code ({file_name}).",
                        },
                        {"role": "user", "content": file_contents},
                        {"role": "assistant", "content": analysis},
                    ]
                )
            elif processed_input:
                # Just a question, no file
                self.formatter.print_user_message(processed_input, show_raw=False)
                messages.append({"role": "user", "content": processed_input})

                self.formatter.print_system_message("Thinking...")
                response, messages = self.openai.chat(messages)
                self.formatter.print_assistant_message(response)
                self.ui.handle_code_extraction(response)

            # Interactive chat loop
            self._interactive_chat(messages)

        except ValueError as e:
            self.formatter.print_error_message(f"Configuration error: {e}")
        except KeyboardInterrupt:
            self.formatter.print_system_message("Program interrupted by user.")
        except Exception as e:
            self.formatter.print_error_message(f"An unexpected error occurred: {e}")

    def _interactive_chat(self, messages: list) -> None:
        """Run interactive chat session with the AI."""
        self.formatter.print_system_message(
            "Interactive chat started. Type 'exit' or 'quit' to end."
        )

        while True:
            user_input = self.formatter.get_user_input()

            if self.ui.is_exit_command(user_input):
                self.formatter.print_system_message("Exiting chat. Goodbye!")
                # Display summary of written files
                summary = self.ui.write_tool.get_write_history_summary()
                if summary != "No files written yet.":
                    self.formatter.print_system_message(summary)
                break

            if not user_input:
                self.formatter.print_error_message("Please enter a message.")
                continue

            # Process input for file loading
            processed_input, file_path = self.ui.process_user_input(user_input)

            if file_path:
                # File was loaded
                file_name = file_path.name
                file_contents = FileHandler.read_file(file_path)
                if not file_contents:
                    self.formatter.print_error_message(
                        f"Failed to read file: {file_path}"
                    )
                    continue

                self.ui.display_file_contents(file_contents, file_name)

                # Create message about the file
                if processed_input:
                    display_message = f"{processed_input}\n[File loaded: {file_name}]"
                else:
                    display_message = f"[File loaded: {file_name}]"

                self.formatter.print_user_message(display_message, show_raw=False)

                # Append file content to message
                messages.append(
                    {
                        "role": "user",
                        "content": f"{processed_input}\n\nFile content ({file_name}):\n{file_contents}"
                        if processed_input
                        else f"Please review this file ({file_name}):\n{file_contents}",
                    }
                )
            else:
                # Just a regular message
                if processed_input:
                    self.formatter.print_user_message(processed_input, show_raw=False)
                    messages.append({"role": "user", "content": processed_input})
                else:
                    self.formatter.print_error_message("Please enter a message.")
                    continue

            try:
                self.formatter.print_system_message("Thinking...")
                response, messages = self.openai.chat(messages)
                self.formatter.print_assistant_message(response)
                self.ui.handle_code_extraction(response)

            except RuntimeError as e:
                self.formatter.print_error_message(str(e))
                messages.pop()  # Remove the failed message


def main():
    """Entry point for the application."""
    agent = AICodeReviewAgent()
    agent.run()


if __name__ == "__main__":
    main()


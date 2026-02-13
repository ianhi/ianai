from __future__ import annotations
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional
from datetime import datetime
import json


class FileHandler:
    """Handles file operations with validation and error handling."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
    SUPPORTED_EXTENSIONS = {
        ".py",
        ".txt",
        ".md",
        ".js",
        ".ts",
        ".json",
        ".yaml",
        ".yml",
    }

    @staticmethod
    def validate_path(file_path: str) -> Optional[Path]:
        """Validate file path and return Path object if valid."""
        try:
            path = Path(file_path).resolve()

            if not path.exists():
                print(f"Error: File '{file_path}' does not exist.")
                return None

            if not path.is_file():
                print(f"Error: '{file_path}' is not a file.")
                return None

            if path.stat().st_size > FileHandler.MAX_FILE_SIZE:
                print(
                    f"Error: File exceeds maximum size of {FileHandler.MAX_FILE_SIZE / 1024 / 1024}MB."
                )
                return None

            return path
        except (OSError, ValueError) as e:
            print(f"Error validating path: {e}")
            return None

    @staticmethod
    def validate_write_path(
        file_path: str, allow_overwrite: bool = False
    ) -> Optional[Path]:
        """Validate file path for writing and return Path object if valid."""
        try:
            path = Path(file_path).resolve()

            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            # Check if file exists and overwrite is not allowed
            if path.exists() and not allow_overwrite:
                print(
                    f"Error: File '{file_path}' already exists. Use allow_overwrite=True to replace it."
                )
                return None

            # Check file extension
            if path.suffix not in FileHandler.SUPPORTED_EXTENSIONS:
                print(
                    f"Error: File extension '{path.suffix}' not supported. Supported: {FileHandler.SUPPORTED_EXTENSIONS}"
                )
                return None

            return path
        except (OSError, ValueError) as e:
            print(f"Error validating write path: {e}")
            return None

    @staticmethod
    def read_file(file_path: Path) -> Optional[str]:
        """Read file contents with comprehensive error handling."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            print(f"Error: Permission denied reading '{file_path}'.")
        except UnicodeDecodeError:
            print(f"Error: Could not decode file '{file_path}'. Is it a text file?")
            return FileHandler._try_alternative_encoding(file_path)
        except IOError as e:
            print(f"Error reading file: {e}")

        return None

    @staticmethod
    def write_file(file_path: Path, content: str) -> bool:
        """Write content to file with error handling."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            return True
        except PermissionError:
            print(f"Error: Permission denied writing to '{file_path}'.")
            return False
        except IOError as e:
            print(f"Error writing to file: {e}")
            return False

    @staticmethod
    def _try_alternative_encoding(file_path: Path) -> Optional[str]:
        """Try alternative encodings if UTF-8 fails."""
        encodings = ["latin-1", "iso-8859-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as file:
                    content = file.read()
                    print(f"Note: File read with {encoding} encoding.")
                    return content
            except (UnicodeDecodeError, IOError):
                continue
        return None


class WriteTool:
    """Tool for the AI model to write files directly."""

    OUTPUT_DIR = Path("./ai_generated_files")

    def __init__(self):
        """Initialize the write tool and create output directory."""
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.write_history = []

    def write_file(
        self,
        filename: str,
        content: str,
        description: str = "",
        allow_overwrite: bool = False,
    ) -> dict:
        """
        Write file with validation and metadata tracking.

        Args:
            filename: Name of the file to write
            content: Content to write to the file
            description: Optional description of the file's purpose
            allow_overwrite: Whether to overwrite existing files

        Returns:
            Dictionary with status, file_path, and message
        """
        file_path = self.OUTPUT_DIR / filename

        # Validate the write path
        validated_path = FileHandler.validate_write_path(
            str(file_path), allow_overwrite=allow_overwrite
        )

        if not validated_path:
            return {
                "success": False,
                "file_path": str(file_path),
                "message": f"Failed to validate path for '{filename}'",
            }

        # Write the file
        if FileHandler.write_file(validated_path, content):
            record = {
                "timestamp": datetime.now().isoformat(),
                "filename": filename,
                "file_path": str(validated_path),
                "description": description,
                "size": len(content),
            }
            self.write_history.append(record)

            return {
                "success": True,
                "file_path": str(validated_path),
                "message": f"Successfully wrote file: {validated_path}",
                "size_bytes": len(content),
            }
        else:
            return {
                "success": False,
                "file_path": str(file_path),
                "message": f"Failed to write file: {filename}",
            }

    def list_written_files(self) -> list:
        """Get list of all files written by the AI."""
        return self.write_history

    def get_write_history_summary(self) -> str:
        """Get a summary of all written files."""
        if not self.write_history:
            return "No files written yet."

        summary = f"Files written: {len(self.write_history)}\n"
        for record in self.write_history:
            summary += f"  - {record['filename']} ({record['size']} bytes) - {record['description']}\n"
        return summary


class CodeExtractor:
    """Extracts and manages Python code blocks from responses."""

    OUTPUT_DIR = Path("./generated_versions")
    PYTHON_BLOCK_PATTERN = r"```python\n(.*?)\n```"

    def __init__(self):
        """Initialize the extractor and create output directory."""
        self.OUTPUT_DIR.mkdir(exist_ok=True)
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

    def extract_code_blocks(self, text: str) -> list[tuple[int, str]]:
        """
        Extract all Python code blocks from text.
        Returns list of tuples: (block_number, code_content)
        """
        blocks = re.findall(self.PYTHON_BLOCK_PATTERN, text, re.DOTALL)
        return [(i + 1, block) for i, block in enumerate(blocks)]

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
    def print_user_message(message: str) -> None:
        """Print user message with formatting."""
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
    def get_user_input() -> str:
        """Get user input with visual separator."""
        print(
            f"\n{UIFormatter.COLORS['user']}{UIFormatter.COLORS['bold']}➜ You:{UIFormatter.COLORS['reset']} ",
            end="",
        )
        return input().strip()

    @staticmethod
    def print_code_blocks(blocks: list[tuple[int, str]]) -> None:
        """Display extracted code blocks."""
        print(
            f"\n{UIFormatter.COLORS['system']}Found {len(blocks)} code block(s):{UIFormatter.COLORS['reset']}\n"
        )

        for block_num, _ in blocks:
            print(f"  [{block_num}] Python code block")

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

    def get_file_path(self) -> Path:
        """Prompt user for a valid file path with validation."""
        while True:
            file_path = input("Enter the path of the file you want to read: ").strip()

            if not file_path:
                self.formatter.print_error_message("File path cannot be empty.")
                continue

            validated_path = FileHandler.validate_path(file_path)
            if validated_path:
                return validated_path

    def display_file_contents(self, contents: str, filename: str) -> None:
        """Display file contents in a formatted way."""
        self.formatter.print_file_contents(contents, filename)

    def is_exit_command(self, text: str) -> bool:
        """Check if user wants to exit."""
        return text.lower() in ["exit", "quit", "bye", "q"]

    @staticmethod
    def get_user_input() -> str:
        """Get user input with visual separator."""
        print(
            f"\n{UIFormatter.COLORS['user']}{UIFormatter.COLORS['bold']}➜ You:{UIFormatter.COLORS['reset']} ",
            end="",
        )
        return input().strip()

    def handle_code_extraction(self, response: str) -> None:
        """Handle code block extraction from response."""
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
            # Multiple blocks - let user choose
            while True:
                choice = (
                    input(
                        f"\n{UIFormatter.COLORS['system']}Which block to save? (1-{len(blocks)}/s for skip): {UIFormatter.COLORS['reset']}"
                    )
                    .strip()
                    .lower()
                )

                if choice == "s":
                    break

                try:
                    block_num = int(choice)
                    if 1 <= block_num <= len(blocks):
                        description = input(
                            f"{UIFormatter.COLORS['system']}Brief description (optional): {UIFormatter.COLORS['reset']}"
                        ).strip()
                        self._save_block(blocks[block_num - 1], description)
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(blocks)}")
                except ValueError:
                    print("Invalid input. Enter a number or 's' to skip.")

    def _save_block(self, block: tuple[int, str], description: str = "") -> None:
        """Save a code block to file."""
        file_path = self.code_extractor.save_code_block(block[1], description)

        if file_path:
            self.formatter.print_system_message(f"Code block saved to: {file_path}")
        else:
            self.formatter.print_error_message("Failed to save code block")


class OpenAIHandler:
    """Manages OpenAI API interactions."""

    DEFAULT_MODEL = "anthropic/claude-haiku-4.5"

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
                    "description": "Write content to a file. The file will be saved in the ai_generated_files directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file to write (e.g., 'improved_code.py')",
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
            }
        ]

    def analyze_code(self, file_contents: str) -> str:
        """Get initial analysis of code from AI."""
        messages = [
            {
                "role": "system",
                "content": "You are an expert coder working as a co-programmer to develop an AI agent. You have access to a write_file tool that allows you to save files directly. When you generate code or configuration files, use this tool to save them.",
            },
            {
                "role": "user",
                "content": "Below are the current contents of the python file we are developing. Please help me improve by adding a write tool so the model can write files directly.",
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
            for tool_call in tool_calls:
                self._process_tool_call(tool_call, messages)

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

    def _process_tool_call(self, tool_call, messages: list) -> None:
        """Process a tool call from the AI model."""
        if tool_call.function.name == "write_file":
            try:
                args = json.loads(tool_call.function.arguments)
                result = self.write_tool.write_file(
                    filename=args.get("filename"),
                    content=args.get("content"),
                    description=args.get("description", ""),
                    allow_overwrite=args.get("allow_overwrite", False),
                )

                # Add tool result to messages
                messages.append(
                    {"role": "user", "content": f"Tool result: {json.dumps(result)}"}
                )
            except (json.JSONDecodeError, KeyError) as e:
                messages.append(
                    {
                        "role": "user",
                        "content": f"Tool error: Invalid arguments - {str(e)}",
                    }
                )


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
            # Step 1: Get file
            file_path = self.ui.get_file_path()

            # Step 2: Ask permission
            if not self.ui.ask_for_permission(str(file_path)):
                self.formatter.print_system_message("Permission denied. Exiting.")
                return

            # Step 3: Read file
            file_contents = FileHandler.read_file(file_path)
            if not file_contents:
                return

            # Step 4: Display file
            self.ui.display_file_contents(file_contents, file_path.name)

            # Step 5: Analyze with AI
            self.formatter.print_system_message("Analyzing code...")
            analysis = self.openai.analyze_code(file_contents)
            self.formatter.print_assistant_message(analysis)

            # Handle code extraction from initial analysis
            self.ui.handle_code_extraction(analysis)

            # Step 6: Interactive chat
            self._interactive_chat(analysis, file_contents)

        except ValueError as e:
            self.formatter.print_error_message(f"Configuration error: {e}")
        except KeyboardInterrupt:
            self.formatter.print_system_message("Program interrupted by user.")
        except Exception as e:
            self.formatter.print_error_message(f"An unexpected error occurred: {e}")

    def _interactive_chat(self, initial_response: str, file_contents: str) -> None:
        """Run interactive chat session with the AI."""
        messages = [
            {
                "role": "system",
                "content": "You are an expert coder working as a co-programmer to develop an AI agent. You have access to a write_file tool that allows you to save files directly. Use it to save any code improvements you suggest.",
            },
            {
                "role": "user",
                "content": "Below are the current contents of the python file we are developing. Please propose improvements to the flow and file reading capabilities.",
            },
            {"role": "user", "content": file_contents},
            {"role": "assistant", "content": initial_response},
        ]

        self.formatter.print_system_message(
            "Starting interactive chat. Type 'exit' or 'quit' to end."
        )

        while True:
            user_input = self.ui.get_user_input()

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

            self.formatter.print_user_message(user_input)
            messages.append({"role": "user", "content": user_input})

            try:
                self.formatter.print_system_message("Thinking...")
                response, messages = self.openai.chat(messages)
                self.formatter.print_assistant_message(response)

                # Handle code extraction from response
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

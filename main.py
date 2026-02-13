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
        ".html",
        ".css",
        ".sql",
        ".sh",
        ".bash",
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

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the write tool and create output directory.

        Args:
            output_dir: Optional custom output directory path
        """
        if output_dir:
            self.OUTPUT_DIR = Path(output_dir)

        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
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
        # Sanitize filename to prevent path traversal
        filename = self._sanitize_filename(filename)
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

    def append_to_file(
        self,
        filename: str,
        content: str,
        description: str = "",
    ) -> dict:
        """
        Append content to an existing file.

        Args:
            filename: Name of the file to append to
            content: Content to append to the file
            description: Optional description of what was appended

        Returns:
            Dictionary with status, file_path, and message
        """
        filename = self._sanitize_filename(filename)
        file_path = self.OUTPUT_DIR / filename

        if not file_path.exists():
            return {
                "success": False,
                "file_path": str(file_path),
                "message": f"File '{filename}' does not exist. Use write_file to create it.",
            }

        try:
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(content)

            record = {
                "timestamp": datetime.now().isoformat(),
                "filename": filename,
                "file_path": str(file_path),
                "description": f"Appended: {description}",
                "size": len(content),
            }
            self.write_history.append(record)

            return {
                "success": True,
                "file_path": str(file_path),
                "message": f"Successfully appended to file: {file_path}",
                "size_bytes": len(content),
            }
        except (PermissionError, IOError) as e:
            return {
                "success": False,
                "file_path": str(file_path),
                "message": f"Failed to append to file: {str(e)}",
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

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks."""
        # Remove any path separators
        filename = filename.replace("\\", "").replace("/", "")
        # Remove leading dots
        filename = filename.lstrip(".")
        # Remove any null bytes
        filename = filename.replace("\x00", "")
        return filename or "unnamed_file.txt"


class OpenAIHandler:
    """Manages OpenAI API interactions."""

    DEFAULT_MODEL = "anthropic/claude-haiku-4.5"
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

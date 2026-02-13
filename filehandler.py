from __future__ import annotations
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional
from datetime import datetime
import json


from pathlib import Path


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

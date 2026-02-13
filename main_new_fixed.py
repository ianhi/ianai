"""
Enhanced AI File Editor with Model Selection and Auto-formatting
"""

import os
import subprocess
from typing import List, Dict, Any
from UI import EditorUI

# Import from openrouter or your LLM provider
# from openrouter import OpenRouterClient  # Example


class AIFileEditor:
    """Main AI file editor with model selection and auto-formatting support."""
    
    AVAILABLE_MODELS = [
        'anthropic/claude-sonnet-4.5',
        'qwen/qwen3-coder-plus',
        'qwen/qwen3-coder',
        'qwen/qwen3-coder-flash',
        'anthropic/claude-haiku-4.5'
    ]
    
    SYSTEM_PROMPT = """You are a helpful AI assistant that can read and write files.

## Planning Before Changes

**IMPORTANT: Before making any changes to files, you should:**
1. **Analyze the request** - Understand what needs to be changed and why
2. **Make a plan** - Outline the specific changes you'll make, including:
   - Which files will be modified
   - What specific changes will be made to each file
   - The order of operations if multiple files are involved
3. **Explain your plan** to the user before executing
4. **Get confirmation** if the changes are significant or could have unintended consequences
5. **Execute the plan** - Make the changes systematically

This planning step helps avoid mistakes and ensures you understand the requirements correctly.

## File Operation Guidelines

When working with files, be efficient and selective:
- Use list_files to explore directory structure before reading specific files
- Only read files that are directly relevant to the user's request
- Avoid reading multiple files when one or two will suffice to answer the question
- When listing files, use patterns to filter results and avoid overwhelming output
- Focus on quality over quantity - reading fewer, more relevant files is better than reading everything
- Ask yourself: "Do I really need to read this file to answer the user's question?"

## Best Practices

1. **Read before writing** - Always read a file before making changes to understand its current state
2. **Show diffs** - When making changes, show what changed so the user can review
3. **Validate changes** - Ensure syntax is correct and changes won't break functionality
4. **Use appropriate tools** - Use bulk_edit for multiple changes to the same file
5. **Be precise** - Use line numbers carefully (remember they're 0-indexed)
6. **Handle errors gracefully** - If something goes wrong, explain what happened and suggest fixes
"""
    
    def __init__(self, model: str = None):
        """
        Initialize the AI file editor.
        
        Args:
            model: Model to use (defaults to first available model)
        """
        self.model = model or self.AVAILABLE_MODELS[0]
        self.ui = EditorUI()
        self.modified_files = set()
        self.chat_history: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            }
        ]
    
    def switch_model(self):
        """Allow user to switch between available models."""
        try:
            new_model = self.ui.show_model_selector(self.AVAILABLE_MODELS, self.model)
            if new_model and new_model != self.model:
                self.model = new_model
                # Reset chat history when switching models
                self.chat_history = [
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    }
                ]
                self.ui.show_info(f"✓ Switched to model: {self.model}")
        except KeyboardInterrupt:
            # User cancelled model selection
            self.ui.show_info("Model selection cancelled")
    
    def format_modified_files(self):
        """Run ruff format on all modified Python files."""
        # Filter to only Python files
        python_files = [f for f in self.modified_files if f.endswith('.py')]
        if not python_files:
            return
        
        try:
            for file_path in python_files:
                # Run ruff format on the file
                result = subprocess.run(
                    ['ruff', 'format', file_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.ui.show_info(f"✓ Formatted {file_path} with ruff")
                else:
                    self.ui.show_warning(f"⚠️  Failed to format {file_path}: {result.stderr}")
        except FileNotFoundError:
            self.ui.show_warning("⚠️  ruff not found. Please install it with: pip install ruff")
        except Exception as e:
            self.ui.show_error(f"Error running ruff format: {str(e)}")
        
        # Clear the modified files set after formatting
        self.modified_files.clear()
    
    def run_loop(self):
        """
        Run the interactive loop where user can type inputs and get AI responses.
        Files referenced with @ will be inserted into the prompt before sending to AI.
        """
        self.ui.show_welcome()
        self.ui.show_model_info(self.model)
        
        while True:
            try:
                self.ui.show_separator()
                
                user_input = self.ui.get_user_input()
                
                # Handle model switching command
                if user_input.strip().lower() == "/model":
                    self.switch_model()
                    self.ui.show_model_info(self.model)
                    continue
                
                if len(user_input) < 4:
                    self.ui.show_info("Input too short, please try again")
                    continue
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    # Format any modified files before exiting
                    if self.modified_files:
                        self.ui.show_info("Formatting modified files before exit...")
                        self.format_modified_files()
                    self.ui.show_info("Goodbye!")
                    break
                
                # Process the input and get AI response
                # This is where you would integrate with your LLM provider
                # processed_input = self.process_input(user_input)
                # self.chat_history.append({"role": "user", "content": processed_input})
                
                # response = self.get_ai_response()
                # self.ui.show_response(response)
                
                # self.chat_history.append({"role": "assistant", "content": response})
                
                # TODO: Implement actual LLM integration
                self.ui.show_info("LLM integration not yet implemented")
                
            except KeyboardInterrupt:
                self.ui.show_separator()
                self.ui.show_info("\nInterrupted. Type 'quit' to exit.")
                continue
            except Exception as e:
                self.ui.show_error(f"Error: {str(e)}")
                continue


def main():
    """Main entry point for the AI file editor."""
    editor = AIFileEditor()
    editor.run_loop()


if __name__ == "__main__":
    main()

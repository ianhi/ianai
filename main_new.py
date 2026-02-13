from __future__ import annotations
import os
from openai import OpenAI

# Import our custom tools
from file_editing3 import FileEditor
from file_reader import FileReader
from file_writer import FileWriter
from file_inserter import FileInserter
from file_lister import FileLister
from UI import AssistantUI


class AIAssistant:
    def __init__(self, api_key=None, model="anthropic/claude-sonnet-4.5"):
        # model="qwen/qwen3-coder-flash"):
        """
        Initialize the AI Assistant.

        Args:
            api_key (str): OpenRouter API key
            model (str): Model to use (default: openai/gpt-4)
        """
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model
        self.ui = AssistantUI()

        # Initialize our tools
        self.file_editor = FileEditor()
        self.file_reader = FileReader()
        self.file_writer = FileWriter()
        self.file_inserter = FileInserter(self.file_reader)
        self.file_lister = FileLister()

        # Collect all tools
        self.tools = []
        self.tools.append(self.file_reader.get_tools())
        self.tools.append(self.file_writer.get_tools())
        self.tools.extend(self.file_editor.get_tools())
        self.tools.append(self.file_lister.get_tools())
        # self.tools.extend(self.file_inserter.get_tools())
        self.chat_history: list[dict[str, str]] = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant that can read and write files.",
            }
        ]

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
                
                if len(user_input) < 4:
                    self.ui.show_info("Input too short, please try again")
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    self.ui.show_goodbye()
                    break

                if not user_input.strip():
                    continue

                # Show user message
                self.ui.show_user_message(user_input)

                # Process the input to insert file contents
                processed_input = self.file_inserter.insert_file_content(user_input)
                
                # Add user message to chat history
                self.chat_history.append({"role": "user", "content": processed_input})

                # Get AI response with thinking indicator
                with self.ui.show_thinking():
                    response = self.get_ai_response(processed_input)
                
                # Add AI response to chat history
                self.chat_history.append({"role": "assistant", "content": response})

                # Show AI response
                self.ui.show_ai_message(response)

            except KeyboardInterrupt:
                self.ui.show_goodbye()
                break
            except Exception as e:
                self.ui.show_error(str(e))

    def execute_tool_call(self, tool_call):
        """
        Execute a single tool call and return the result.
        
        Args:
            tool_call: The tool call object from the API response
            
        Returns:
            str: Result message from the tool execution
        """
        # Show which tool is being called
        self.ui.show_tool_call(tool_call.function.name)
        
        result = None
        args = eval(tool_call.function.arguments)
        
        if tool_call.function.name == "read_file":
            result = self.file_reader.read_file(**args)
        elif tool_call.function.name == "write_file":
            result = self.file_writer.write_file(**args)
        elif tool_call.function.name == "edit_file":
            result = self.file_editor.edit_file(**args)
        elif tool_call.function.name == "insert_line":
            result = self.file_editor.insert_line(**args)
        elif tool_call.function.name == "remove_line":
            result = self.file_editor.remove_line(**args)
        elif tool_call.function.name == "change_line":
            result = self.file_editor.change_line(**args)
        elif tool_call.function.name == "list_files":
            result = self.file_lister.list_files(**args)

        # Show tool result
        if result:
            self.ui.show_tool_result(result)
        
        return result if result else "Operation completed"

    def get_ai_response(self, prompt):
        """
        Get response from OpenRouter AI model.
        Continues in a loop executing tools until AI provides a final text response.

        Args:
            prompt (str): Prompt to send to the AI

        Returns:
            str: AI response text
        """
        # Keep looping until we get a response without tool calls
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                tools=self.tools,
                tool_choice="auto",
            )
            
            ai_message = response.choices[0].message

            # If no tool calls, we're done - return the text response
            if not ai_message.tool_calls:
                return ai_message.content if ai_message.content else "Task completed."

            # Execute all tool calls
            tool_results = []
            for tool_call in ai_message.tool_calls:
                result = self.execute_tool_call(tool_call)
                
                tool_results.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": result,
                    }
                )

            # Add assistant message and tool results to chat history
            self.chat_history.append(ai_message)
            self.chat_history.extend(tool_results)
            
            # Loop continues - will make another API call with updated history


from dotenv import load_dotenv

load_dotenv()
agent = AIAssistant()
agent.run_loop()

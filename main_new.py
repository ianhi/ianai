from __future__ import annotations
import os
from openai import OpenAI

# Import our custom tools
from file_editing3 import FileEditor
from file_reader import FileReader
from file_writer import FileWriter
from file_inserter import FileInserter


class AIAssistant:
    def __init__(self, api_key=None, model="qwen/qwen3-coder-flash"):
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

        # Initialize our tools
        self.file_editor = FileEditor()
        self.file_reader = FileReader()
        self.file_writer = FileWriter()
        self.file_inserter = FileInserter(self.file_reader)

        # Collect all tools
        self.tools = []
        # self.tools.append(self.file_reader.get_tools())
        self.tools.append(self.file_writer.get_tools())
        self.tools.append(self.file_editor.get_tools())
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
        print("AI Assistant initialized. Type 'quit' to exit.")
        print("Use '@filename' to insert file contents into your prompts.")
        print("-" * 50)

        while True:
            try:
                print("-" * 50)
                print("\n\n\n")
                print("-" * 50)
                user_input = input("\nYou: ")
                if len(user_input) < 4:
                    print(len(user_input))
                    print(user_input)
                    raise ValueError("some horrible loop")

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if not user_input.strip():
                    continue

                # Process the input to insert file contents
                processed_input = self.file_inserter.insert_file_content(user_input)
                # Add user message to chat history
                self.chat_history.append({"role": "user", "content": processed_input})

                # Get AI response
                response = self.get_ai_response(processed_input)
                # Add AI response to chat history
                self.chat_history.append({"role": "assistant", "content": response})

                print(f"\nAI: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break

    def get_ai_response(self, prompt):
        """
        Get response from OpenRouter AI model.

        Args:
            prompt (str): Prompt to send to the AI

        Returns:
            str: AI response text
        """
        # print(dict(self.tools))
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.chat_history,
            tools=self.tools,
            tool_choice="auto",
        )
        ai_message = response.choices[0].message

        if ai_message.tool_calls:
            # Handle tool calls if any
            # Execute tools and get results
            tool_results = []
            result = None
            for tool_call in ai_message.tool_calls:
                print(tool_call)
                if tool_call.function.name == "write_file":
                    args = eval(tool_call.function.arguments)
                    result = self.file_writer.write_file(**args)
                elif tool_call.function.name == "edit_file":
                    args = eval(tool_call.function.arguments)
                    result = self.file_editor.edit_file(**args)
                if result:
                    tool_results.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": result,
                        }
                    )

            # Send tool results back to AI
            self.chat_history.append(ai_message)
            self.chat_history.extend(tool_results)

            # Get final response from AI after tool execution
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                tools=self.tools,
                tool_choice="auto",
            )
            return final_response.choices[0].message.content
        else:
            return ai_message.content

        return response.choices[0].message.content


from dotenv import load_dotenv

load_dotenv()
agent = AIAssistant()
agent.run_loop()

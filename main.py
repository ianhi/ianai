import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


def ask_for_permission(file_path):
    """Ask the user for permission to read the specified file."""
    response = (
        input(f"Do you want to read the file '{file_path}'? (y/n): ").strip().lower()
    )
    return response in ("y", "yes")


def read_file(file_path):
    """Read the contents of a file with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except PermissionError:
        print(f"Error: Permission denied reading '{file_path}'.")
        return None
    except UnicodeDecodeError:
        print(f"Error: Could not decode file '{file_path}'. Is it a text file?")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def get_valid_file_path():
    """Prompt user for a valid file path."""
    while True:
        file_path = input("Enter the path of the file you want to read: ").strip()
        if not file_path:
            print("File path cannot be empty.")
            continue
        if os.path.exists(file_path):
            return file_path
        print(f"The specified file '{file_path}' does not exist.")


def initialize_openai_client():
    """Initialize and return OpenAI client."""
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


def chat_with_agent(client, file_contents):
    """Run interactive chat with AI agent."""
    messages = [
        {
            "role": "system",
            "content": "You are an expert coder working as a co-programmer to develop an AI agent.",
        },
        {
            "role": "user",
            "content": "Below are the current contents of the python file we are developing. Please propose improvements to the flow and file reading capabilities.",
        },
        {"role": "user", "content": file_contents},
    ]

    try:
        # Initial analysis
        response = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
        )
        assistant_response = response.choices[0].message.content
        print(f"\nAssistant: {assistant_response}\n")
        messages.append({"role": "assistant", "content": assistant_response})

        # Interactive loop
        while True:
            print("=" * 50)
            user_input = input("You: ").strip()
            print("=" * 50)

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Exiting chat. Goodbye!")
                break

            if not user_input:
                print("Please enter a message.")
                continue

            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="anthropic/claude-haiku-4.5",
                messages=messages,
            )

            assistant_response = response.choices[0].message.content
            print(f"\nAssistant: {assistant_response}\n")
            messages.append({"role": "assistant", "content": assistant_response})

    except Exception as e:
        print(f"Error during chat: {e}")


def main():
    """Main function to orchestrate the workflow."""
    try:
        # Initialize API client
        client = initialize_openai_client()

        # Get and validate file
        file_path = get_valid_file_path()

        # Ask for permission
        if not ask_for_permission(file_path):
            print("Permission denied. The file will not be read.")
            return

        # Read file
        file_contents = read_file(file_path)
        if file_contents is None:
            return

        print(f"\n{'=' * 50}")
        print("File contents:")
        print(f"{'=' * 50}")
        print(file_contents)
        print(f"{'=' * 50}\n")

        # Start chat with agent
        chat_with_agent(client, file_contents)

    except ValueError as e:
        print(f"Configuration error: {e}")
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

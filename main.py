def ask_for_permission(file_path):
    """Ask the user for permission to read the specified file."""
    response = (
        input(f"Do you want to read the file '{file_path}'? (y/n): ").strip().lower()
    )
    if response in ("y", "yes"):
        return True
    return False


def read_file(file_path):
    """Read the contents of a file."""
    with open(file_path, "r") as file:
        contents = file.read()
        return contents


def main():
    from openai import OpenAI
    from dotenv import load_dotenv
    import os

    load_dotenv()

    api_key = os.environ["OPENROUTER_API_KEY"]
    # print(api_key)

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    def chat_with_agent(file_contents):
        messages = [
            {
                "role": "system",
                "content": "You are an expert coder wokring as a co-programmer to develp an ai agent.",
            }
        ]

        messages.append(
            {
                "role": "user",
                "content": "Below are the current contents of the python file we are developing. Please propose improvements to the flow and file reading capabilities.",
            }
        )
        messages.append({"role": "user", "content": file_contents})

        response = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5", messages=messages
        )

        assistant_response = response.choices[0].message.content
        print(f"Assistant: {assistant_response}")
        messages.append({"role": "assistant", "content": assistant_response})

        while True:
            print("============\n\n\n")
            user_input = input("You: ")
            print("============\n\n\n")
            if user_input.lower() in ["exit", "quit"]:
                break

            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="anthropic/claude-haiku-4.5", messages=messages
            )

            assistant_response = response.choices[0].message.content
            print(f"Assistant: {assistant_response}")
            messages.append({"role": "assistant", "content": assistant_response})

    file_path = input("Enter the path of the file you want to read: ").strip()
    if not os.path.exists(file_path):
        print("The specified file does not exist.")
        return

    if ask_for_permission(file_path):
        file_contents = read_file(file_path)
        if file_contents is not None:
            print("File contents:")
            print(file_contents)
            # Here you can add your logic to send or process the file
        else:
            print("Failed to read the file.")
    else:
        print("Permission denied. The file will not be read.")

    chat_with_agent(file_contents)


if __name__ == "__main__":
    main()

    # print(completion.choices[0].message.content)
    # with open("output.md", "w") as f:
    #     f.write(completion.choices[0].message.content)


if __name__ == "__main__":
    main()

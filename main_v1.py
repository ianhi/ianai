from __future__ import annotations
from openai import OpenAI
from dotenv import load_dotenv
import os

# Generated on 2026-02-13 04:33:44


def main():

    load_dotenv()

    api_key = os.environ["OPENROUTER_API_KEY"]
    # print(api_key)

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    DEFAULT_MODEL = "qwen/qwen3-coder-flash"

    def chat_with_agent():
        messages = [
            {
                "role": "system",
                "content": "You are a coding assistant. Generate Python code when asked.",
            }
        ]

        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model=DEFAULT_MODEL, messages=messages
            )

            assistant_response = response.choices[0].message.content
            print(f"Assistant: {assistant_response}")
            messages.append({"role": "assistant", "content": assistant_response})

    chat_with_agent()


if __name__ == "__main__":
    main()

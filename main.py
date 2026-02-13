def main():
    from openai import OpenAI
    from dotenv import load_dotenv
    import os

    load_dotenv()

    api_key = os.environ["OPENROUTER_API_KEY"]
    # print(api_key)

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    # completion = client.chat.completions.create(
    #     model="mistralai/codestral-2508",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "You are a helpful coding assistant. Generate Python code when asked.",
    #         },
    #         {
    #             "role": "user",
    #             "content": "I am building a coding agent from scratch in python this is my first query. I am using the openai library via openrouter. I have implemented no tooling. Except the chat with agent funciton you recommends.",
    #         },
    #     ],
    # )

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
                model="openai/gpt-4o-mini", messages=messages
            )

            assistant_response = response.choices[0].message.content
            print(f"Assistant: {assistant_response}")
            messages.append({"role": "assistant", "content": assistant_response})

    chat_with_agent()
    # print(completion.choices[0].message.content)
    # with open("output.md", "w") as f:
    #     f.write(completion.choices[0].message.content)


if __name__ == "__main__":
    main()

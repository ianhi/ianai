def main():
    from openai import OpenAI
    from dotenv import load_dotenv
    import os

    load_dotenv()

    api_key = os.environ["OPENROUTER_API_KEY"]
    # print(api_key)

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    completion = client.chat.completions.create(
        model="mistralai/codestral-2508",
        messages=[
            {
                "role": "user",
                "content": "I am building a coding agent from scratch in python this is my first query. I am using the openai library via openrouter. I have implemented no tool yet. What would you advise I make first? ",
            }
        ],
    )
    print(completion.choices[0].message.content)
    with open("output.md", "w") as f:
        f.write(completion.choices[0].message.content)


if __name__ == "__main__":
    main()

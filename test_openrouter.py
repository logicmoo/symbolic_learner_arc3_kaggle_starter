import os
from openai import OpenAI


def main() -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not configured")

    print("OPENROUTER_API_KEY is configured; its value will not be displayed.")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print("Model used:", response.model)
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()

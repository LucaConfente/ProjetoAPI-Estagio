from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",  # ou "gpt-4.0", "gpt-3.5-turbo", etc.
    messages=[
        {"role": "user", "content": "Tell me a three sentence bedtime story about a unicorn."}
    ]
)

print(response.choices[0].message.content)
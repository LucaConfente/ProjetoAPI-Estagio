from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()


# TESTE DA OPENAI COM A KEY com dotaenv

response = client.chat.completions.create(
    model="gpt-4o",  # ou "gpt-4.0", "gpt-3.5-turbo", etc.
    messages=[
        {"role": "user", "content": "O que sao buracos negros"}
    ]
)

print(response.choices[0].message.content)
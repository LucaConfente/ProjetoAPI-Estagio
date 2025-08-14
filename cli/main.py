import os
from dotenv import load_dotenv
import openai

load_dotenv() # Carrega as variáveis do arquivo .env

openai.api_key = os.getenv("OPENAI_API_KEY")
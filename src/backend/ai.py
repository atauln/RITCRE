import os
from llama_index.llms.gemini import Gemini
from llama_index.core.llms import ChatMessage
from backend.db import get_db

from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL')

def get_llm() -> Gemini:
    llm = Gemini(
        api_key=GEMINI_API_KEY,
        model=GEMINI_MODEL,
    )
    return llm

if __name__ == '__main__':
    print(get_llm().chat([ChatMessage(role='user', text='Hello, how are you?')]))
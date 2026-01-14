from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = None
LLM_PROVIDER = None

if OPENAI_API_KEY:
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=OPENAI_API_KEY,
        timeout=30,
        max_retries=1,
    )
elif GOOGLE_API_KEY:
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.2,
        google_api_key=GOOGLE_API_KEY
    )
else:
    raise RuntimeError(
        "No LLM API key found. Set OPENAI_API_KEY or GOOGLE_API_KEY"
    )
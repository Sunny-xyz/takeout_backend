import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

# Initialize OpenAI client using the API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not set. Please check your .env file.")
client = OpenAI(api_key=openai_api_key)

async def get_llm_response(prompt: str) -> str:
    loop = asyncio.get_event_loop()

    def sync_call():
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    return await loop.run_in_executor(None, sync_call)

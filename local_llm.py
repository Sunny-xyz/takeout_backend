import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables if needed
load_dotenv()

# Initialize the local LLM pipeline using GPT-Neo (or any model you prefer)
llm_pipeline = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")

# Set up an executor for blocking calls
executor = ThreadPoolExecutor(max_workers=3)

async def get_llm_response(prompt: str) -> str:
    loop = asyncio.get_event_loop()

    def sync_call():
        result = llm_pipeline(prompt, max_length=200, do_sample=True, temperature=0.7)
        return result[0]['generated_text']

    return await loop.run_in_executor(executor, sync_call)

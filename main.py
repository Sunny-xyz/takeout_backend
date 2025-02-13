import os
import json
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from concurrent.futures import ThreadPoolExecutor
from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging and FastAPI app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

# Initialize the Hugging Face text-generation pipeline with GPT-Neo (free model)
llm_pipeline = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")

# Set up a thread pool executor for running blocking LLM calls
executor = ThreadPoolExecutor(max_workers=3)

# Define Pydantic models for the recommendation request and response
class RecommendationRequest(BaseModel):
    preferences: List[str]  # e.g., ["spicy", "fast service", "vegan options"]

class RecommendationResponse(BaseModel):
    recommendations: List[str]

# Helper function to call the LLM asynchronously
async def get_llm_response(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        lambda: llm_pipeline(prompt, max_length=200, do_sample=True, temperature=0.7)
    )
    # Return the generated text from the first result
    return result[0]['generated_text']

# Root endpoint for a simple health-check
@app.get("/")
async def read_root():
    return {"message": "Hello from the LLM integration endpoint!"}

# Endpoint to generate recommendations using the LLM
@app.post("/recommendations", response_model=RecommendationResponse)
async def generate_recommendations(request: RecommendationRequest):
    # Refined prompt instructing the model to output only valid JSON
    prompt = (
        "User preferences: " + ", ".join(request.preferences) + ". " +
        "Based on these preferences, output a JSON array of exactly 3 takeout restaurant recommendations. " +
        "Each recommendation must be a JSON object with exactly two keys: 'name' and 'description'. " +
        "Return only the JSON array with no additional text."
    )
    logger.info("LLM prompt: %s", prompt)
    llm_output = await get_llm_response(prompt)
    logger.info("LLM raw output: %s", llm_output)
    
    try:
        # Try to parse the output directly as JSON
        recommendations = json.loads(llm_output)
        # Optionally, validate that it's a list of exactly 3 items
        if not (isinstance(recommendations, list) and len(recommendations) == 3):
            raise ValueError("Invalid recommendation list length")
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("Error decoding LLM response: %s", e)
        # Fallback: Provide a default response
        recommendations = [
            {"name": "Default Restaurant 1", "description": "A popular choice with excellent reviews."},
            {"name": "Default Restaurant 2", "description": "Known for its quick service and tasty meals."},
            {"name": "Default Restaurant 3", "description": "Offers a variety of vegan options."},
        ]
    return RecommendationResponse(recommendations=[f"{rec['name']}: {rec['description']}" for rec in recommendations])

@app.get("/test-llm")
async def test_llm():
    prompt = "Hello, world! Please generate a short greeting."
    output = await get_llm_response(prompt)
    return {"prompt": prompt, "output": output}

# Entry point for running the app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

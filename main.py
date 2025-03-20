import os
import json
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Configure logging and FastAPI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

# Choose which LLM implementation to use based on the environment variable USE_OPENAI.
USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() in ["true", "1"]

if USE_OPENAI:
    from openai_llm import get_llm_response
    logger.info("Using OpenAI LLM")
else:
    from local_llm import get_llm_response
    logger.info("Using Local LLM")

# Define request/response models
class RecommendationRequest(BaseModel):
    preferences: List[str]  # e.g., ["indian", "vegan"]

class RecommendationResponse(BaseModel):
    recommendations: List[str]

# Root endpoint for health-check
@app.get("/")
async def read_root():
    return {"message": "Hello from our recommendations API!"}

# Endpoint to generate recommendations
@app.post("/recommendations", response_model=RecommendationResponse)
async def generate_recommendations(request: RecommendationRequest):
    # Fetch restaurant data from the Restaurant API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://127.0.0.1:8002/restaurants")
            response.raise_for_status()
            restaurants = response.json()
        except Exception as e:
            logger.error("Error fetching restaurants: %s", e)
            restaurants = []

    # Filter restaurants based on user preferences (by cuisine)
    matching_restaurants = []
    for feature in restaurants:
        cuisine = feature.get("properties", {}).get("cuisine", "").lower()
        for pref in request.preferences:
            if pref.lower() in cuisine:
                matching_restaurants.append(feature)
                break  # Avoid duplicate matches

    # Prepare restaurant context
    sample_restaurants = matching_restaurants[:5]
    if sample_restaurants:
        restaurant_info = "; ".join(
            f"{r.get('properties', {}).get('name', 'Unknown')} ({r.get('properties', {}).get('cuisine', 'Unknown')})"
            for r in sample_restaurants
        )
    else:
        restaurant_info = "No matching restaurants found."

    # Build prompt for the LLM
    prompt = (
        "User preferences: " + ", ".join(request.preferences) + ". " +
        "Based on these preferences, provide a list of 3 takeout restaurant recommendations, each with a brief description. " +
        "Consider ONLY the following available restaurants: " + restaurant_info
    )
    logger.info("LLM prompt: %s", prompt)

    # Generate response from the chosen LLM
    llm_output = await get_llm_response(prompt)
    logger.info("LLM output: %s", llm_output)

    return RecommendationResponse(recommendations=[llm_output])

@app.get("/test-llm")
async def test_llm():
    prompt = "Hello, world! Please generate a short greeting."
    output = await get_llm_response(prompt)
    return {"prompt": prompt, "output": output}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

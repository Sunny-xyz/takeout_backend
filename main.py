import os
import json
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
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

# Define a structured recommendation model
class RecommendationItem(BaseModel):
    name: str
    short_description: str
    highlight: str

# Define the response model (list of items)
class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]

# Request model
class RecommendationRequest(BaseModel):
    preferences: List[str]  # e.g., ["indian", "vegan"]

@app.get("/")
async def read_root():
    return {"message": "Hello from our recommendations API!"}

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
            f"{r.get('properties', {}).get('name', 'Unknown')} "
            f"({r.get('properties', {}).get('cuisine', 'Unknown')})"
            for r in sample_restaurants
        )
    else:
        restaurant_info = "No matching restaurants found."

    # Build a prompt instructing the LLM to return valid JSON
    # with exactly 3 recommendations, each with name, short_description, highlight
    prompt = (
        "User preferences: " + ", ".join(request.preferences) + ". "
        "Please provide exactly 3 restaurant recommendations in valid JSON format. "
        "Each recommendation should have: "
        "- name (string)\n"
        "- short_description (string)\n"
        "- highlight (string)\n"
        "Return only valid JSON (no extra text), and DO NOT include triple backticks."
        "Example:\n"
        "[\n"
        "  {\n"
        '    "name": "Spice Villa",\n'
        '    "short_description": "A restaurant offering delicious Indian curries.",\n'
        '    "highlight": "Excellent naan bread."\n'
        "  },\n"
        "  {\n"
        '    "name": "Masala Hut",\n'
        '    "short_description": "Great vegetarian options.",\n'
        '    "highlight": "Homemade paneer."\n'
        "  },\n"
        "  {\n"
        '    "name": "Tandoori Express",\n'
        '    "short_description": "Quick takeout service.",\n'
        '    "highlight": "Wide variety of spicy dishes."\n'
        "  }\n"
        "]\n"
        f"Consider ONLY the following available restaurants: {restaurant_info}"
    )
    logger.info("LLM prompt: %s", prompt)

    # Generate response from the chosen LLM
    llm_output = await get_llm_response(prompt)
    logger.info("LLM raw output: %s", llm_output)

    # Parse the JSON returned by the LLM
    # If parsing fails, return an empty list or handle gracefully
    try:
        parsed = json.loads(llm_output)
        # Validate the parsed data against the RecommendationItem model
        validated = [RecommendationItem(**item) for item in parsed]
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.error("Error parsing LLM JSON output: %s", e)
        validated = []

    return RecommendationResponse(recommendations=validated)

@app.get("/test-llm")
async def test_llm():
    prompt = "Hello, world! Please generate a short greeting."
    output = await get_llm_response(prompt)
    return {"prompt": prompt, "output": output}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

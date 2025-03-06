import os
import json
import asyncio
import logging
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from concurrent.futures import ThreadPoolExecutor
from transformers import pipeline
from dotenv import load_dotenv
import httpx  # Added to call the Restaurant API

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

# Helper function to post-process the LLM output based on our available restaurant names
def post_process_llm_output(llm_output: str, restaurant_names: list) -> list:
    recommendations = []
    # Try splitting the output by newlines and check for known restaurant names.
    for line in llm_output.split('\n'):
        for name in restaurant_names:
            if name.lower() in line.lower():
                cleaned_line = line.strip()
                if cleaned_line and cleaned_line not in recommendations:
                    recommendations.append(cleaned_line)
                break
    # Fallback: if we haven't found enough recommendations, try splitting by sentences.
    if len(recommendations) < 3:
        for sentence in re.split(r'[.!?]', llm_output):
            for name in restaurant_names:
                if name.lower() in sentence.lower():
                    cleaned_sentence = sentence.strip()
                    if cleaned_sentence and cleaned_sentence not in recommendations:
                        recommendations.append(cleaned_sentence)
                    break
            if len(recommendations) >= 3:
                break
    return recommendations[:3] if recommendations else [llm_output.strip()]

# Root endpoint for a simple health-check
@app.get("/")
async def read_root():
    return {"message": "Hello from the LLM integration endpoint!"}

# Updated endpoint to generate recommendations using the LLM and restaurant data
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
    
    # Filter restaurants based on user preferences by checking the 'cuisine' part
    matching_restaurants = []
    for feature in restaurants:
        cuisine = feature.get("properties", {}).get("cuisine", "").lower()
        for pref in request.preferences:
            if pref.lower() in cuisine:
                matching_restaurants.append(feature)
                break  # Avoids duplicate matches

    # Limits us to a few matches for context in the prompt
    sample_restaurants = matching_restaurants[:5]
    if sample_restaurants:
        restaurant_info = "; ".join(
            f"{r.get('properties', {}).get('name', 'Unknown')} ({r.get('properties', {}).get('cuisine', 'Unknown')})"
            for r in sample_restaurants
        )
        # Keep a list of restaurant names for post-processing.
        restaurant_names = [r.get('properties', {}).get('name', 'Unknown') for r in sample_restaurants]
    else:
        restaurant_info = "No matching restaurants found."
        restaurant_names = []
    # The prompt
    prompt = (
        "User preferences: " + ", ".join(request.preferences) + ". " +
        "Based on these preferences, provide a list of 3 takeout restaurant recommendations, each with a brief description. " +
        "Consider the following available restaurants: " + restaurant_info
    )
    logger.info("LLM prompt: %s", prompt)
    llm_output = await get_llm_response(prompt)
    logger.info("LLM raw output: %s", llm_output)
    
    # Post-process the LLM output to better match our available restaurants.
    recommendations = post_process_llm_output(llm_output, restaurant_names)
    return RecommendationResponse(recommendations=recommendations)


@app.get("/test-llm")
async def test_llm():
    prompt = "Hello, world! Please generate a short greeting."
    output = await get_llm_response(prompt)
    return {"prompt": prompt, "output": output}

# Entry point for running the app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

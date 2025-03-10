# Takeout Recommendation Backend

This project is a FastAPI-based backend that provides takeout restaurant recommendations. It integrates a free Hugging Face LLM (using GPT-Neo) to generate recommendations based on user preferences.

## Features

- **FastAPI Backend:** Provides API endpoints for recommendations.
- **LLM Integration:** Uses a free Hugging Face model (GPT-Neo) to generate restaurant recommendations.
- **Structured Output:** Returns recommendations in a structured JSON format.
- **Companion App:** A Rails companion app that allows users to test endpoints and the LLM response

## Prerequisites

- Python 3.8 or later
- pip
- Ruby: Version 2.7 or later.
- Rails: Version 6.0 or later.
- SQLite3: The default database used by Rails.## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Sunny-xyz/takeout-backend.git
   cd takeout-backend
2. **Create a Virtual Environment:**

   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate

3. **Install Dependencies**
   ```
   pip install -r requirements.txt

## Running the Application

Start the FastAPI Server with Uvicorn:
   ```
   uvicorn main:app --reload
   ```
- The server will be running at http://127.0.0.1:8000.
- Access the interactive API documentation at http://127.0.0.1:8000/docs to test the endpoints.
- You can test the LLM functionality at http://127.0.0.1:8000/test-llm to ensure responses are being generated correctly. This endpoint sends a simple greeting prompt to the LLM and returns the generated output.


Starting the Rails server:

Run:
   ```
   ./bin/dev/
   ```
## API Endpoints

### GET /
- Description: Health-check endpoint.
- Response: JSON message confirming the server is running.

### POST /recommendations
- Description: Generates a list of takeout restaurant recommendations based on user preferences.
- Request Body Example:
   ```
    {
    "preferences": ["spicy", "fast service", "vegan options"]
  }
   ```
- Response Example:
   ```
  {
    "recommendations": [
      {
        "id": "1",
        "name": "Restaurant A",
        "description": "Great for spicy dishes and quick service."
      },
      {
        "id": "2",
        "name": "Restaurant B",
        "description": "Offers vegan options with fast service."
      },
      {
        "id": "3",
        "name": "Restaurant C",
        "description": "Known for spicy food and an affordable menu."
      }
    ]
  }
   ```

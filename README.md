# Takeout Recommendation Backend

This project is a FastAPI-based backend that provides takeout restaurant recommendations by integrating a free Hugging Face LLM (GPT-Neo). The backend uses user preferences to generate contextual restaurant suggestions and is complemented by a Rails companion app for testing and demonstration.

## Features

- **FastAPI Backend:** Provides API endpoints for recommendations.
- **LLM Integration:** Uses a free Hugging Face model (GPT-Neo) to generate restaurant recommendations.
- **Structured Output:** Returns recommendations in a structured JSON format.
- **Companion App:** A Rails companion app that allows users to test endpoints and the LLM response
- **Dynamic Recommendation Generation:** Uses user preferences and available restaurant data to create contextual recommendations
- **Companion Rails App:** A Rails-based front-end that allows users to test endpoints and view the LLM generated responses in a user friendly interface

## Prerequisites

- Python 3.8 or later
- pip
- Ruby: Version 2.7 or later.
- Rails: Version 6.0 or later.
- SQLite3: The default database used by Rails.## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Sunny-xyz/takeout_backend.git
   cd takeout-backend

2. **Install Dependencies**
   ```
   pip install -r requirements.txt

3. **Set Up Environment Variables:**
   ```
   Create a .env file if needed to configure environment variables required by the backend.
   ```


## Running the Application

### Start the FastAPI Server

Launch the back-end server using Uvicorn:
   ```
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
- The server will be running at http://127.0.0.1:8000.
- Access the interactive API documentation at http://127.0.0.1:8000/docs to test the endpoints.
- You can test the LLM functionality at http://127.0.0.1:8000/test-llm to ensure responses are being generated correctly. This endpoint sends a simple greeting prompt to the LLM and returns the generated output.

### Start the Restaurant API
The backend fetches restaurant data from a separate FastAPI service. Start it with:
   ```
uvicorn restaurants_api:app --host 127.0.0.1 --port 8002 --reload
   ```
- The server will be running at http://127.0.0.1:8002.
- Access the interactive API documentation at http://127.0.0.1:8002/docs to test the endpoints.
- You can test the restaurant API functionality at http://127.0.0.1:8002/restaurants to ensure that the restaurant information is being displayed as expected.

Start the Rails Companion App:

Run:
   ```
   ./bin/dev/
   ```
- The server will be running at localhost:3000

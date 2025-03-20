import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

# Initialize OpenAI client using the API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not set. Please check your .env file.")
client = OpenAI(api_key=openai_api_key)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "Write a one-sentence bedtime story about a unicorn."
        }
    ]
)

print(completion.choices[0].message.content)
import json
from fastapi import HTTPException

try:
    with open("export.geojson", "r") as f:
        restaurant_data = json.load(f)
except Exception as e:
    restaurant_data = None
    print("Error loading restaurant data:", e)

import json
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from the Restaurant API!"}

try:
    with open("export.geojson", "r") as f:
        restaurant_data = json.load(f)
except Exception as e:
    restaurant_data = None
    print("Error loading restaurant data:", e)

@app.get("/restaurants")
def get_restaurants():
    if restaurant_data and "features" in restaurant_data:
        return restaurant_data["features"]
    raise HTTPException(status_code=500, detail="Restaurant data not available.")

@app.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: int):
    if restaurant_data and "features" in restaurant_data:
        for feature in restaurant_data["features"]:
            restaurant_fhrs_id = feature.get("properties", {}).get("fhrs:id")

            if restaurant_fhrs_id is not None and int(restaurant_fhrs_id) == restaurant_id:
                return feature
        raise HTTPException(status_code=404, detail="Restaurant not found.")
    raise HTTPException(status_code=500, detail="Restaurant data not available.")

import requests
from requests.structures import CaseInsensitiveDict
from groq import Groq
import os
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError
import time
import http.client
import json

# API Keys
GROQ_API_KEY = "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"
GEOAPIFY_API_KEY = "cbe278cf7b0a4f1a88b02bbc18848819"
RAPIDAPI_KEY = "fb80f5eadcmshfda1d42ee564a33p15fbdfjsnffaae5e1911a"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# 🔁 LLM with Retry
@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def LLM_QnA_agent(prompt, temperature=1.0, max_tokens=1024):
    try:
        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            stream=True,
            stop=None,
        )
        response_content = ""
        for chunk in completion:
            response_content += chunk.choices[0].delta.content or ""
        return response_content
    except Exception as e:
        print(f"Error during Azure LLM call: {e}")
        raise

# 📍 Places nearby
def get_places(category, bbox):
    url = f"https://api.geoapify.com/v2/places?categories={category}&filter=rect%3A{bbox[0]}%2C{bbox[1]}%2C{bbox[2]}%2C{bbox[3]}&limit=20&apiKey={GEOAPIFY_API_KEY}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    try:
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error during API request: {e}")
        return None

# 🧳 Travel info
def get_travel_info(place, state, country):
    prompt = f"Give me travel information for {place}, {state}, {country}."
    try:
        response = LLM_QnA_agent(prompt)
        return {
            "description": response,
            "source": "AWS"
        }
    except RetryError as e:
        return {
            "description": f"Failed to get response from LLM after retries: {e}",
            "source": "AWS"
        }

# 🌤️ Current Weather
def get_weather_info(city, country_code="EN"):
    try:
        conn = http.client.HTTPSConnection("open-weather13.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "open-weather13.p.rapidapi.com"
        }
        endpoint = f"/city/{city}/{country_code}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

# 🌦️ 3-Day Forecast
def get_weather_forecast(lat, lon):
    try:
        conn = http.client.HTTPSConnection("open-weather13.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "open-weather13.p.rapidapi.com"
        }
        endpoint = f"/city/fivedaysforcast/{lat}/{lon}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching forecast: {e}")
        return None

# 🌎 Climate Info by ZIP Code
def get_climate_by_zip(zip_code):
    try:
        conn = http.client.HTTPSConnection("climate-by-zip.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "climate-by-zip.p.rapidapi.com"
        }
        endpoint = f"/climate/{zip_code}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching climate data: {e}")
        return None

# 🍽️ TripAdvisor Restaurants
def get_tripadvisor_restaurants(location_id="304554"):
    try:
        conn = http.client.HTTPSConnection("tripadvisor16.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "tripadvisor16.p.rapidapi.com"
        }
        endpoint = f"/api/v1/restaurant/searchRestaurants?locationId={location_id}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching restaurants: {e}")
        return None

# ✈️ Flight Information by Airport Code
def get_flight_info(code_type, code):
    try:
        conn = http.client.HTTPSConnection("aerodatabox.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "aerodatabox.p.rapidapi.com"
        }
        endpoint = f"/flights/airports/{code_type}/{code}?offsetMinutes=-120&durationMinutes=720&withLeg=true&direction=Both&withCancelled=true&withCodeshared=true&withCargo=true&withPrivate=true&withLocation=false"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching flight info: {e}")
        return None

# 🚗 iBright InCab API
def get_ibrigth_message():
    try:
        conn = http.client.HTTPSConnection("ibright-incab.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "ibright-incab.p.rapidapi.com"
        }
        conn.request("GET", "/message", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching iBright message: {e}")
        return None

# ▶️ Test all functions
if __name__ == "__main__":
    # 🧠 AI Answer
    print("\n🧠 AI Response:")
    prompt = "What are the latest trends in AI research?"
    try:
        response = LLM_QnA_agent(prompt)
        print("\n\nFull AI Response:")
        print(response)
    except RetryError as e:
        print(f"Failed after multiple attempts: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    # 🏪 Nearby Places
    category = "commercial.supermarket"
    bbox = (10.716463, 48.755151, 10.835314, 48.680903)
    places = get_places(category, bbox)

    if places:
        print("\n\n🏪 Places Found:")
        for place in places.get("features", []):
            name = place["properties"].get("name", "Unknown")
            address = place["properties"].get("formatted", "No address available")
            print(f"- {name}: {address}")
    else:
        print("No places found.")

    # 🌤️ Current Weather
    city = "London"
    weather_info = get_weather_info(city)
    if weather_info:
        print(f"\n\n🌤️ Current Weather in {city}:")
        print(json.dumps(weather_info, indent=2))
    else:
        print("Could not fetch weather info.")

    # 🌦️ Forecast
    lat, lon = 30.438, -89.1028
    forecast_info = get_weather_forecast(lat, lon)
    if forecast_info:
        print(f"\n\n📆 3-Day Forecast for ({lat}, {lon}):")
        print(json.dumps(forecast_info, indent=2))
    else:
        print("Could not fetch forecast.")

    # 🌍 Climate Data by ZIP
    zip_code = "87102"
    climate_data = get_climate_by_zip(zip_code)
    if climate_data:
        print(f"\n\n🌡️ Climate Data for ZIP {zip_code}:")
        print(json.dumps(climate_data, indent=2))
    else:
        print("Could not fetch climate data.")

    # 🍽️ TripAdvisor Restaurants
    location_id = "304554"
    restaurants = get_tripadvisor_restaurants(location_id)
    if restaurants:
        print(f"\n\n🍽️ Restaurants for location ID {location_id}:")
        print(json.dumps(restaurants, indent=2))
    else:
        print("Could not fetch restaurant data.")

    # ✈️ Flight Info
    code_type = "iata"
    airport_code = "YYZ"
    flights = get_flight_info(code_type, airport_code)
    if flights:
        print(f"\n\n✈️ Flights for {airport_code}:")
        print(json.dumps(flights, indent=2))
    else:
        print("Could not fetch flight info.")

    # 🚗 iBright InCab Test
    ibr = get_ibrigth_message()
    if ibr:
        print(f"\n\n🚗 iBright InCab Response:")
        print(json.dumps(ibr, indent=2))
    else:
        print("Could not fetch iBright message.")

from groq import Groq
import time
import json
import http.client
from tenacity import retry, wait_exponential, stop_after_attempt
import requests
from requests.structures import CaseInsensitiveDict

# === API KEYS ===
GROQ_API_KEY = "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"
GEOAPIFY_API_KEY = "cbe278cf7b0a4f1a88b02bbc18848819"
RAPIDAPI_KEY = "fb80f5eadcmshfda1d42ee564a33p15fbdf7Z2tprVk38IhsQlod"

# === Initialize Groq client ===
client = Groq(api_key=GROQ_API_KEY)

# === Retry-enabled function to call Groq ===
@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def LLM_QnA_agent(prompt, temperature=1.0, max_tokens=1024):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
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
        print(f"Error during Gemini LLM call: {e}")
        raise

# === Routing API function ===
def get_route_info(start_lat, start_lon, end_lat, end_lon, mode="drive"):
    url = f"https://api.geoapify.com/v1/routing?waypoints={start_lat},{start_lon}|{end_lat},{end_lon}&mode={mode}&apiKey={GEOAPIFY_API_KEY}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            route = data.get("features", [])[0]["properties"]
            return {
                "distance": route.get("distance"),
                "time": route.get("time"),
                "mode": mode,
                "units": "meters & seconds"
            }
        else:
            return {"error": f"Failed to fetch route. Status: {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# === Travel info from LLM ===
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

# === Yahoo Weather by City ===
def get_yahoo_weather(city, unit="f"):
    try:
        conn = http.client.HTTPSConnection("yahoo-weather5.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "yahoo-weather5.p.rapidapi.com"
        }

        endpoint = f"/weather?location={city}&format=json&u={unit}"
        conn.request("GET", endpoint, headers=headers)

        res = conn.getresponse()
        data = res.read()
        conn.close()

        weather_data = json.loads(data.decode("utf-8"))
        return weather_data

    except Exception as e:
        print(f"Error fetching Yahoo weather data by city: {e}")
        return None

# === Yahoo Weather by WOEID ===
def get_yahoo_weather_by_woeid(woeid, unit="f"):
    try:
        conn = http.client.HTTPSConnection("yahoo-weather5.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "yahoo-weather5.p.rapidapi.com"
        }

        endpoint = f"/weather?woeid={woeid}&format=json&u={unit}"
        conn.request("GET", endpoint, headers=headers)

        res = conn.getresponse()
        data = res.read()
        conn.close()

        weather_data = json.loads(data.decode("utf-8"))
        return weather_data

    except Exception as e:
        print(f"Error fetching Yahoo weather data by WOEID: {e}")
        return None

# === Climate Change News ===
def get_climate_news(source="tnyt"):
    try:
        conn = http.client.HTTPSConnection("climate-change-news48.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "climate-change-news48.p.rapidapi.com"
        }

        endpoint = f"/news/{source}"
        conn.request("GET", endpoint, headers=headers)

        res = conn.getresponse()
        data = res.read()
        conn.close()

        news_data = json.loads(data.decode("utf-8"))
        return news_data

    except Exception as e:
        print(f"Error fetching climate change news: {e}")
        return None

# === Agoda Hotel Details ===
def get_agoda_hotel_details(property_id="9062231"):
    try:
        conn = http.client.HTTPSConnection("agoda-com.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "agoda-com.p.rapidapi.com"
        }

        endpoint = f"/hotels/details?propertyId={property_id}"
        conn.request("GET", endpoint, headers=headers)

        res = conn.getresponse()
        data = res.read()
        conn.close()

        hotel_data = json.loads(data.decode("utf-8"))
        return hotel_data

    except Exception as e:
        print(f"Error fetching Agoda hotel details: {e}")
        return None

# === Skyscanner Flight Details ===
def get_flight_details():
    try:
        conn = http.client.HTTPSConnection("sky-scanner3.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "sky-scanner3.p.rapidapi.com"
        }

        conn.request("GET", "/web/flights/details", headers=headers)

        res = conn.getresponse()
        data = res.read()
        conn.close()

        flight_data = json.loads(data.decode("utf-8"))
        return flight_data

    except Exception as e:
        print(f"Error fetching Skyscanner flight details: {e}")
        return None

# === Cab Booking Mock API ===
def get_cab_booking_info(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, mode="standard"):
    # Mock API to simulate a cab booking system response
    try:
        # You would replace this with actual calls to Uber/Lyft API or another service
        mock_cab_response = {
            "pickup": {
                "latitude": pickup_lat,
                "longitude": pickup_lon,
                "address": "Pickup Address (Mock)"
            },
            "dropoff": {
                "latitude": dropoff_lat,
                "longitude": dropoff_lon,
                "address": "Dropoff Address (Mock)"
            },
            "mode": mode,
            "estimated_fare": "$25.50",
            "estimated_time": "15 minutes",
            "available_cabs": 5,
            "service": "MockCabService"
        }
        return mock_cab_response
    except Exception as e:
        print(f"Error fetching cab booking info: {e}")
        return None

# === Example Usage ===
if __name__ == "__main__":
    prompt = "What can you tell me about the latest advancements in AI?"

    print("\n=== Chatbot Response ===")
    try:
        response = LLM_QnA_agent(prompt)
        print("\n\nFull Response:\n", response)
    except Exception as e:
        print(f"Chatbot Error: {e}")

    print("\n=== Route Info ===")
    start_lat, start_lon = 50.96209827745463, 4.414458883409225
    end_lat, end_lon = 50.429137079078345, 5.00088081232559
    route_info = get_route_info(start_lat, start_lon, end_lat, end_lon)
    print(route_info)

    print("\n=== Yahoo Weather by City (Sunnyvale) ===")
    weather_city = get_yahoo_weather("Sunnyvale")
    print(json.dumps(weather_city, indent=2) if weather_city else "Weather fetch failed.")

    print("\n=== Yahoo Weather by WOEID (2502265 - Sunnyvale) ===")
    weather_woeid = get_yahoo_weather_by_woeid(2502265)
    print(json.dumps(weather_woeid, indent=2) if weather_woeid else "Weather fetch failed.")

    print("\n=== Climate Change News (New York Times) ===")
    climate_news = get_climate_news("tnyt")
    print(json.dumps(climate_news, indent=2) if climate_news else "News fetch failed.")

    print("\n=== Agoda Hotel Details ===")
    agoda_details = get_agoda_hotel_details("9062231")  # Example property ID
    print(json.dumps(agoda_details, indent=2) if agoda_details else "Agoda fetch failed.")

    print("\n=== Skyscanner Flight Details ===")
    flight_info = get_flight_details()
    print(json.dumps(flight_info, indent=2) if flight_info else "Flight fetch failed.")

    print("\n=== Cab Booking Information ===")
    cab_info = get_cab_booking_info(50.96209827745463, 4.414458883409225, 50.429137079078345, 5.00088081232559)
    print(json.dumps(cab_info, indent=2) if cab_info else "Cab booking fetch failed.")

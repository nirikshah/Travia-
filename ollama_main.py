from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError
import requests
from requests.structures import CaseInsensitiveDict
import http.client
import json

# === API Keys ===
GROQ_API_KEY = "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"
GEOAPIFY_API_KEY = "cbe278cf7b0a4f1a88b02bbc18848819"
RAPIDAPI_KEY = "fb80f5eadcmshfda1d42ee564a33p15fbdfjsnffaae5e1911a"

# === Initialize Groq client ===
client = Groq(api_key=GROQ_API_KEY)

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def LLM_QnA_agent(prompt, temperature=1.0, max_tokens=1024):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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
        print(f"Ollama LLM error: {e}")
        raise
    
    # ✅ Required function to fix the AttributeError
def get_travel_info(place, state, country):
    prompt = f"Give a detailed travel guide about {place} in {state}, {country}. Include history, best places to visit, food, and budget tips."
    try:
        response = LLM_QnA_agent(prompt)
        return response
    except RetryError:
        return "Ollama failed to respond after multiple attempts."
    except Exception as e:
        return f"Error from Ollama: {e}"

def get_place_details(place_id):
    url = f"https://api.geoapify.com/v2/place-details?id={place_id}&apiKey={GEOAPIFY_API_KEY}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": f"Failed to fetch details. Status code: {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_past_weather_data(lat, lon, date, units="auto"):
    try:
        conn = http.client.HTTPSConnection("ai-weather-by-meteosource.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "ai-weather-by-meteosource.p.rapidapi.com"
        }
        endpoint = f"/time_machine?lat={lat}&lon={lon}&date={date}&units={units}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching past weather data: {e}")
        return None

def get_current_weather_data(lat, lon, timezone="auto", language="en", units="auto"):
    try:
        conn = http.client.HTTPSConnection("ai-weather-by-meteosource.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "ai-weather-by-meteosource.p.rapidapi.com"
        }
        endpoint = f"/current?lat={lat}&lon={lon}&timezone={timezone}&language={language}&units={units}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching current weather data: {e}")
        return None

def get_monthly_weather_data(lat, lon, alt, start_date, end_date):
    try:
        conn = http.client.HTTPSConnection("meteostat.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "meteostat.p.rapidapi.com"
        }
        endpoint = f"/point/monthly?lat={lat}&lon={lon}&alt={alt}&start={start_date}&end={end_date}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching monthly weather data: {e}")
        return None

def search_hotel_destinations(query="new"):
    try:
        conn = http.client.HTTPSConnection("sky-scrapper.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "sky-scrapper.p.rapidapi.com"
        }
        endpoint = f"/api/v1/hotels/searchDestinationOrHotel?query={query}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error searching hotel destinations: {e}")
        return None

def get_hotel_prices(hotel_id, entity_id, checkin, checkout, adults=1, rooms=1, currency="USD", market="en-US", country_code="US"):
    try:
        conn = http.client.HTTPSConnection("sky-scrapper.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "sky-scrapper.p.rapidapi.com"
        }
        endpoint = f"/api/v1/hotels/getHotelPrices?hotelId={hotel_id}&entityId={entity_id}&checkin={checkin}&checkout={checkout}&adults={adults}&rooms={rooms}&currency={currency}&market={market}&countryCode={country_code}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching hotel prices: {e}")
        return None

def search_flights(originSkyId, destinationSkyId, originEntityId, destinationEntityId, cabinClass="economy", adults=1, sortBy="best", currency="USD", market="en-US", countryCode="US"):
    try:
        conn = http.client.HTTPSConnection("sky-scrapper.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "sky-scrapper.p.rapidapi.com"
        }
        endpoint = f"/api/v2/flights/searchFlightsWebComplete?originSkyId={originSkyId}&destinationSkyId={destinationSkyId}&originEntityId={originEntityId}&destinationEntityId={destinationEntityId}&cabinClass={cabinClass}&adults={adults}&sortBy={sortBy}&currency={currency}&market={market}&countryCode={countryCode}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return None

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

# === Main Function ===
if __name__ == "__main__":
    # 1. Query LLM
    prompt = "Tell me about Hampi in Karnataka, India – its history, places to visit, and food."
    temperature = 0.9
    max_tokens = 1024

    print("🔍 Querying LLM...\n")
    try:
        llm_response = LLM_QnA_agent(prompt, temperature, max_tokens)
        print("\n\n✅ Full Response:\n", llm_response)
    except RetryError:
        print("❌ Retry failed after multiple attempts.")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. Geoapify Place Details
    print("\n🌍 Fetching Place Details from Geoapify...\n")
    sample_place_id = "514d368a517c511e40594bfd7b574ec84740f00103f90135335d1c00000000920313416e61746f6d697363686573204d757365756d"
    place_details = get_place_details(sample_place_id)
    print(json.dumps(place_details, indent=2))

    # 3. Meteosource Past Weather
    print("\n📜 Fetching Past Weather from Meteosource...\n")
    past_weather = get_past_weather_data(37.81021, -122.42282, "2021-08-24")
    print(json.dumps(past_weather, indent=2) if past_weather else "❌ Past weather fetch failed.")

    # 4. Current Weather
    print("\n🌤️ Fetching Current Weather from Meteosource...\n")
    current_weather = get_current_weather_data(37.81021, -122.42282)
    print(json.dumps(current_weather, indent=2) if current_weather else "❌ Current weather fetch failed.")

    # 5. Monthly Historical Weather
    print("\n📆 Fetching Monthly Historical Weather from Meteostat...\n")
    monthly_weather = get_monthly_weather_data(52.5244, 13.4105, 43, "2020-01-01", "2020-12-31")
    print(json.dumps(monthly_weather, indent=2) if monthly_weather else "❌ Monthly weather fetch failed.")

    # 6. Hotel Search
    print("\n🏨 Searching Hotels for 'New York'...\n")
    hotels = search_hotel_destinations("New York")
    print(json.dumps(hotels, indent=2) if hotels else "❌ Hotel search failed.")

    # 7. Hotel Prices
    print("\n💰 Fetching Hotel Prices...\n")
    hotel_price = get_hotel_prices("106005202", "27537542", "2024-02-20", "2024-02-21")
    print(json.dumps(hotel_price, indent=2) if hotel_price else "❌ Hotel price fetch failed.")

    # 8. Flights
    print("\n✈️ Fetching Flight Details (JFK -> MIA)...\n")
    flights = search_flights("JFK", "MIA", "95565058", "95673821")
    print(json.dumps(flights, indent=2) if flights else "❌ Flight search failed.")

    # 9. iBright Message
    print("\n📡 Fetching iBright InCab message...\n")
    ibright = get_ibrigth_message()
    print(json.dumps(ibright, indent=2) if ibright else "❌ iBright message fetch failed.")

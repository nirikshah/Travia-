from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError
import json
import time
import requests
from requests.structures import CaseInsensitiveDict
import http.client

# API Keys
GROQ_API_KEY = "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"
GEOAPIFY_API_KEY = "cbe278cf7b0a4f1a88b02bbc18848819"
WEATHER_API_HOST = "weather-api167.p.rapidapi.com"
WEATHER_API_KEY = "fb80f5eadcmshfda1d42ee564a33p15fbdf7Z2tprVk38IhsQlod"
CLIMATE_API_HOST = "koppen-climate-classification.p.rapidapi.com"
CLIMATE_API_KEY = "fb80f5eadcmshfda1d42ee564a33p15fbdfjsnffaae5e1911a"
HOTEL_API_HOST = "booking-com15.p.rapidapi.com"
HOTEL_API_KEY = "fb80f5eadcmshfda1d42ee564a33p15fbdfjsnffaae5e1911a"
FLIGHT_API_HOST = "agoda-com.p.rapidapi.com"
FLIGHT_API_KEY = "fb80f5eadcmshfda1d42ee564a33p15fbdfjsnffaae5e1911a"
CAB_API_HOST = "cab-booking2.p.rapidapi.com"
CAB_API_KEY = "fb80f5eadcmshfda1d42ee564a33p15fbdfjsnffaae5e1911a"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Chat logs file
CHAT_LOGS_FILE = 'chat_logs.json'

def load_chat_logs():
    try:
        with open(CHAT_LOGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_logs(chat_logs):
    with open(CHAT_LOGS_FILE, 'w') as f:
        json.dump(chat_logs, f, indent=4)

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def LLM_QnA_agent(prompt, temperature=0.6, max_tokens=4096):
    try:
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=0.95,
            stream=True,
            stop=None,
        )
        response_content = ""
        for chunk in completion:
            response_content += chunk.choices[0].delta.content or ""
        return response_content
    except Exception as e:
        print(f"Error during API call: {e}")
        raise


def get_weather_forecast(place, country_code="IN", cnt=3):
    conn = http.client.HTTPSConnection(WEATHER_API_HOST)
    endpoint = f"/api/weather/forecast?place={place},{country_code}&cnt={cnt}&units=metric&type=three_hour&mode=json&lang=en"
    headers = {
        'x-rapidapi-key': WEATHER_API_KEY,
        'x-rapidapi-host': WEATHER_API_HOST,
        'Accept': "application/json"
    }
    try:
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        forecast_data = json.loads(data.decode("utf-8"))

        if "list" in forecast_data:
            return [
                {
                    "time": entry["dt_txt"],
                    "temp": entry["main"]["temp"],
                    "description": entry["weather"][0]["description"]
                }
                for entry in forecast_data["list"]
            ]
        else:
            return [{"error": "Weather data not available"}]
    except Exception as e:
        return [{"error": str(e)}]

def geocode_address(address):
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={GEOAPIFY_API_KEY}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("features"):
                loc = data["features"][0]["properties"]
                return {
                    "lat": loc.get("lat"),
                    "lon": loc.get("lon"),
                    "formatted": loc.get("formatted")
                }
            else:
                return {"error": "No results found."}
        else:
            return {"error": f"Geoapify error: {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_climate_classification(lat, lon):
    conn = http.client.HTTPSConnection(CLIMATE_API_HOST)
    headers = {
        'x-rapidapi-key': CLIMATE_API_KEY,
        'x-rapidapi-host': CLIMATE_API_HOST
    }
    endpoint = f"/classification?lat={lat}&lon={lon}"
    try:
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

def get_hotels(dest_id="-2092174", location="US"):
    conn = http.client.HTTPSConnection(HOTEL_API_HOST)
    headers = {
        'x-rapidapi-key': HOTEL_API_KEY,
        'x-rapidapi-host': HOTEL_API_HOST
    }
    endpoint = f"/api/v1/hotels/searchHotels?dest_id={dest_id}&search_type=CITY&adults=1&children_age=0%2C17&room_qty=1&page_number=1&units=metric&temperature_unit=c&languagecode=en-us&currency_code=AED&location={location}"
    try:
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

def get_flight_info():
    conn = http.client.HTTPSConnection(FLIGHT_API_HOST)
    headers = {
        'x-rapidapi-key': FLIGHT_API_KEY,
        'x-rapidapi-host': FLIGHT_API_HOST
    }
    try:
        conn.request("GET", "/flights/details", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

def generate_cab_booking_otp(mobile_number):
    conn = http.client.HTTPSConnection(CAB_API_HOST)
    payload = json.dumps({"mobileNumber": mobile_number})
    headers = {
        'x-rapidapi-key': CAB_API_KEY,
        'x-rapidapi-host': CAB_API_HOST,
        'Content-Type': "application/json"
    }
    try:
        conn.request("POST", "/signup/generateotp", body=payload, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

def search_chat_logs(keyword):
    chat_logs = load_chat_logs()
    return [log for log in chat_logs if keyword.lower() in log['prompt'].lower()]

def provide_reasoning(response):
    return f"The model generated this response based on a content length of {len(response)} characters, implying it provided a detailed explanation."

def get_travel_info(place, state, country):
    prompt = f"Give me travel information for {place}, {state}, {country}."
    try:
        response = LLM_QnA_agent(prompt)
        country_code = country[:2].upper()

        geo = geocode_address(f"{place}, {state}, {country}")
        lat, lon = geo.get("lat"), geo.get("lon")

        forecast = get_weather_forecast(place, country_code=country_code)
        climate = get_climate_classification(lat, lon) if lat and lon else {"error": "Coordinates not found"}
        hotels = get_hotels(location=country_code)
        flights = get_flight_info()

        return {
            "description": response,
            "weather_forecast": forecast,
            "climate_classification": climate,
            "coordinates": {"lat": lat, "lon": lon},
            "hotels": hotels,
            "flights": flights,
            "source": "AWS"
        }
    except RetryError as e:
        return {
            "description": f"Failed to get response from LLM after retries: {e}",
            "weather_forecast": [],
            "climate_classification": {"error": "LLM failure"},
            "hotels": [],
            "flights": [],
            "source": "AWS"
        }

# Example usage
if __name__ == "__main__":
    prompt = "What can you tell me about the latest advancements in AI?"
    try:
        response = LLM_QnA_agent(prompt)
        print("\nFull Response:\n", response)

        chat_logs = load_chat_logs()
        chat_logs.append({'prompt': prompt, 'response': response})
        save_chat_logs(chat_logs)

        print("\nReasoning:\n", provide_reasoning(response))

        keyword = "AI"
        results = search_chat_logs(keyword)
        if results:
            print(f"\nSearch Results for '{keyword}':")
            for res in results:
                print(f"Prompt: {res['prompt']}, Response: {res['response']}")
        else:
            print(f"\nNo results for '{keyword}'")

        address = "38 Upper Montagu Street, Westminster, United Kingdom"
        print("\nGeocode Result:\n", geocode_address(address))

        travel = get_travel_info("Mysore", "Karnataka", "India")
        print("\nTravel Info:\n", json.dumps(travel, indent=4))

        cab_response = generate_cab_booking_otp(7418221500)
        print("\nCab Booking OTP Response:\n", json.dumps(cab_response, indent=4))

    except RetryError as e:
        print(f"Failed after retries: {e}")

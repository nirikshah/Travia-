import streamlit as st
from urllib.parse import unquote
from utils import get_place_details_from_llm
from datetime import datetime
import requests
from fpdf import FPDF
from io import BytesIO

# Setup
st.set_page_config(page_title="Place Details", page_icon="📍")
st.title("📍 Travel Details")

# Get query params
query_params = st.experimental_get_query_params()
place = unquote(query_params.get("place", [""])[0])
state = unquote(query_params.get("state", [""])[0])
country = unquote(query_params.get("country", [""])[0])

# Error if no input
if not place or not state or not country:
    st.warning("Missing place/state/country in the URL.")
    st.stop()

# --- Call your LLM wrapper function ---
details = get_place_details_from_llm(place, state, country)

if not details:
    st.error("Failed to fetch place details. Please try again.")
    st.stop()

# --- Display Location Info ---
st.subheader(f"📌 {place}, {state}, {country}")
st.write(f"**Best Time to Visit:** {details.get('best_time', 'N/A')}")
st.write(f"**Season:** {details.get('season', 'N/A')}")
st.write(f"**Weather:** {details.get('weather', 'N/A')}")
st.write(f"**Famous Food:** {details.get('famous_food', 'N/A')}")
st.write(f"**Street Food:** {details.get('street_food', 'N/A')}")
st.write(f"**Budget Stay:** {details.get('budget_stay', 'N/A')}")
st.write(f"**Hangouts:** {', '.join(details.get('hangouts', []))}")
st.write(f"**Hotels:** {', '.join(details.get('hotels', []))}")
st.write(f"**Restaurants:** {', '.join(details.get('restaurants', []))}")
st.markdown("### 📋 Itinerary")
st.write(details.get("itinerary", "N/A"))

# --- Static Map Image from Geoapify ---
def get_map_url(place, state, country):
    query = f"{place}, {state}, {country}"
    return f"https://maps.geoapify.com/v1/staticmap?style=osm-bright&center=geo:{query}&zoom=12&size=600x300&apiKey=cbe278cf7b0a4f1a88b02bbc18848819"

st.markdown("### 🌍 Map Location")
st.image(get_map_url(place, state, country), use_column_width=True)

# --- Weather Forecast (3 Time Slots) ---
st.markdown("### 🌦️ 3-Slot Weather Forecast")

def get_weather_forecast(place, state, country):
    # Dummy data – Replace with RapidAPI/WeatherAPI response
    return [
        {"slot": "Morning", "temp": "22°C", "condition": "Sunny"},
        {"slot": "Afternoon", "temp": "28°C", "condition": "Partly Cloudy"},
        {"slot": "Evening", "temp": "20°C", "condition": "Clear"},
    ]

weather_data = get_weather_forecast(place, state, country)
for forecast in weather_data:
    st.markdown(f"**{forecast['slot']}**: {forecast['temp']}, {forecast['condition']}")

# --- PDF Download ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Travel Itinerary: {place}", ln=True)

    pdf.set_font("Arial", size=12)
    for label, val in {
        "Best Time": details.get("best_time", "N/A"),
        "Season": details.get("season", "N/A"),
        "Weather": details.get("weather", "N/A"),
        "Famous Food": details.get("famous_food", "N/A"),
        "Street Food": details.get("street_food", "N/A"),
        "Budget Stay": details.get("budget_stay", "N/A"),
        "Hangouts": ', '.join(details.get("hangouts", [])),
        "Hotels": ', '.join(details.get("hotels", [])),
        "Restaurants": ', '.join(details.get("restaurants", [])),
        "Itinerary": details.get("itinerary", "N/A")
    }.items():
        pdf.multi_cell(0, 10, f"{label}: {val}")

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

st.download_button(
    label="📥 Download Itinerary as PDF",
    data=generate_pdf(),
    file_name=f"{place}_itinerary.pdf",
    mime="application/pdf"
)

# --- Feedback Form ---
st.markdown("---")
st.subheader("💬 Feedback Form")

with st.form("feedback_form"):
    files = st.file_uploader("Upload photos/videos", type=["jpg", "png", "mp4"], accept_multiple_files=True)
    opinion = st.text_area("Your opinion or experience")
    useful = st.radio("Was this itinerary useful?", ["Yes", "No", "Somewhat"])
    rating = st.slider("Rate suggestions", 1, 5)
    suggestion = st.text_input("Any improvements or new features?")

    if st.form_submit_button("Submit Feedback"):
        st.success("✅ Thank you! Your feedback is recorded.")

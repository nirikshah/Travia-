import streamlit as st
import aws_main as aws
import azure_main as azure
import gemini_main as gemini
import ollama_main as ollama

from components import autocomplete_input
from utils import (
    register_user, authenticate_user, save_chat_logs,
    calculate_best_response, get_email_by_username,
    send_password_reset_email, update_password
)

from admin_dashboard import render_admin_dashboard

# Page setup
st.set_page_config(page_title="Travel Assistant", page_icon="🌍")

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "vacation_suggestions" not in st.session_state:
    st.session_state.vacation_suggestions = {}

# --- Style Functions ---
def set_register_style():
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"] {
                height: 100%;
                background-image: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e');
                background-size: cover;
                background-position: center;
                font-family: 'Segoe UI', sans-serif;
                color: white;
            }
            .login-area {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 120px;
                gap: 15px;
                backdrop-filter: blur(6px);
                padding: 30px;
                border-radius: 15px;
            }
            .title {
                font-size: 2.5rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
                color: #ffffff;
                text-shadow: 1px 1px 3px #000;
            }
            .stTextInput input {
                background-color: rgba(255, 255, 255, 0.85) !important;
                color: #000000 !important;
                font-weight: 600;
                border-radius: 8px;
            }
            .stButton>button {
                background-color: #f9a826 !important;
                color: black !important;
                font-weight: bold;
                border-radius: 8px;
            }
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

def set_chat_style():
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"] {
                height: 100%;
                background-color: #121212;
                font-family: 'Segoe UI', sans-serif;
                color: #e0e0e0;
            }
            .main {
                background-color: #1e1e1e;
                padding: 2rem;
                border-radius: 10px;
                color: #fff;
            }
            .glow {
                font-size: 32px;
                color: #00FFFF;
                text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF;
                font-weight: bold;
                margin-bottom: 20px;
                text-align: center;
            }
            .chat-box {
                background-color: #2a2a2a;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                color: #cfcfcf;
            }
            .dark-input input {
                color: #111 !important;
                background-color: #e0e0e0 !important;
            }
            .glow-button button {
                background: linear-gradient(to right, #00ffff, #007fff);
                color: black !important;
                padding: 12px 30px;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                box-shadow: 0 0 10px #00ffff;
                transition: 0.3s ease-in-out;
            }
            .glow-button button:hover {
                box-shadow: 0 0 20px #00ffff, 0 0 30px #00ffff;
                transform: scale(1.05);
                cursor: pointer;
            }
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

# Handle password reset via query
params = st.query_params
if params.get("reset") and params.get("user"):
    username = params.get("user")[0]
    st.title("🔒 Reset Password")
    new_pass = st.text_input("New Password", type="password", key="new_pass")
    confirm = st.text_input("Confirm New Password", type="password", key="confirm_new")

    if st.button("Reset Now"):
        if new_pass != confirm:
            st.error("Passwords do not match.")
        else:
            if update_password(username, new_pass):
                st.success("Password updated successfully.")
            else:
                st.error("Error updating password.")
    st.stop()

# --- Login/Register UI ---
if not st.session_state.logged_in:
    set_register_style()
    st.markdown('<div class="login-area">', unsafe_allow_html=True)
    st.markdown('<div class="title">Welcome to Travel Assistant</div>', unsafe_allow_html=True)

    choice = st.radio("Choose an option", ("Login", "Register", "Forgot Password"), key="auth_choice")

    if choice == "Register":
        username = st.text_input("Enter Username", key="register_username")
        email = st.text_input("Enter Email", key="register_email")
        password = st.text_input("Enter Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")

        if st.button("Register", key="register_btn"):
            if password == confirm_password:
                message = register_user(username, password, email)
                st.success(message) if "successfully" in message else st.error(message)
            else:
                st.error("Passwords do not match!")

    elif choice == "Login":
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username}!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

    elif choice == "Forgot Password":
        username = st.text_input("Enter your username", key="forgot_user")
        if st.button("Send Reset Link", key="reset_btn"):
            email = get_email_by_username(username)
            if email:
                send_password_reset_email(email, username)
                st.success("Password reset link sent to your email.")
            else:
                st.error("Username not found or no email associated.")

    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Chat Page ---
if st.session_state.logged_in:
    set_chat_style()
    st.markdown('<div class="glow">🌍 Travel Assistant Chat</div>', unsafe_allow_html=True)

    if st.session_state.username == "admin":
        render_admin_dashboard()
    else:
        st.subheader("Where do you want to go?")
        with st.container():
            st.markdown("<div class='dark-input'>", unsafe_allow_html=True)
            place = autocomplete_input("Enter Place")
            state = autocomplete_input("Enter State")
            country = autocomplete_input("Enter Country")
            st.markdown("</div>", unsafe_allow_html=True)

        with st.container():
            st.markdown("<div class='glow-button'>", unsafe_allow_html=True)
            if st.button("Get Recommendation"):
                if place and state and country:
                    st.session_state.vacation_suggestions = {
                        "AWS": aws.get_travel_info(place, state, country),
                        "Azure": azure.get_travel_info(place, state, country),
                        "Gemini": gemini.get_travel_info(place, state, country),
                        "Ollama": ollama.get_travel_info(place, state, country)
                    }
                    save_chat_logs(
                        st.session_state.username,
                        place,
                        state,
                        country,
                        st.session_state.vacation_suggestions
                    )
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.vacation_suggestions:
            best_model, accuracy_scores = calculate_best_response(st.session_state.vacation_suggestions)
            best_response = st.session_state.vacation_suggestions[best_model]

            st.markdown(f"### ✅ Best Response from: {best_model}")
            st.markdown("#### 🔍 Accuracy Scores:")
            for model, score in accuracy_scores.items():
                st.write(f"- **{model}**: {score}")

            if isinstance(best_response, dict):
                st.markdown(f'<div class="chat-box">{best_response.get("description", "No description available.")}</div>', unsafe_allow_html=True)
            else:
                st.warning("Unexpected format in the best model's response.")

            st.markdown("---")
            st.markdown(
                f'<a href="/details?place={place}&state={state}&country={country}" target="_blank">More Details</a>',
                unsafe_allow_html=True
            )

import json
import os
import hashlib
import uuid
import datetime
import smtplib
from email.message import EmailMessage

USERS_FILE = "users.json"
CHAT_LOGS_FILE = "chat_logs.json"
ACCURACY_LOGS_FILE = "accuracy_logs.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def register_user(username, password, email):
    users = load_users()
    if username in users:
        return "Username already exists."
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {"password_hash": password_hash, "email": email}
    save_users(users)
    return "User registered successfully."

def authenticate_user(username, password):
    users = load_users()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return username in users and users[username]["password_hash"] == password_hash

def save_chat_logs(username, place, state, country, responses):
    log = {
        "user": username,
        "place": place,
        "state": state,
        "country": country,
        "responses": responses,
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now().isoformat()
    }
    if not os.path.exists(CHAT_LOGS_FILE):
        with open(CHAT_LOGS_FILE, 'w') as f:
            json.dump([log], f, indent=2)
    else:
        with open(CHAT_LOGS_FILE, 'r') as f:
            logs = json.load(f)
        logs.append(log)
        with open(CHAT_LOGS_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

def calculate_accuracy_score(response):
    if not isinstance(response, dict):
        return 0
    description = response.get("description", "")
    score = len(description)
    keywords = ["food", "hotel", "stay", "weather", "itinerary", "season", "hangout", "budget"]
    keyword_score = sum(1 for word in keywords if word in description.lower())
    return score + (keyword_score * 20)

def calculate_best_response(responses):
    accuracy_scores = {}
    for model, response in responses.items():
        accuracy_scores[model] = calculate_accuracy_score(response)

    best_model = max(accuracy_scores, key=accuracy_scores.get)
    log = {
        "timestamp": datetime.datetime.now().isoformat(),
        "scores": accuracy_scores,
        "best_model": best_model
    }
    with open(ACCURACY_LOGS_FILE, "a") as f:
        json.dump(log, f)
        f.write("\n")

    return best_model, accuracy_scores

def send_password_reset_email(to_email, username):
    msg = EmailMessage()
    msg['Subject'] = '🔑 Reset your Travel Assistant Password'
    msg['From'] = 'hnishu602@gmail.com'
    msg['To'] = to_email

    reset_link = f"http://localhost:8501/?reset=true&user={username}"
    msg.set_content(f"""
Hi {username},

You requested a password reset for your Travel Assistant account.

Click the link below to reset your password:
{reset_link}

If you didn’t request this, you can ignore this email.

Thanks,
Travel Assistant Team
""")
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('hnishu602@gmail.com', 'hhik kiot jumo lkmx')  # app password
            server.send_message(msg)
            print(f"✅ Email sent to {to_email}")
            return True
    except Exception as e:
        print("❌ Email send error:", e)
        return False

def update_password(username, new_password):  # <- Renamed to fix ImportError
    users = load_users()
    if username not in users:
        return False
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    users[username]["password_hash"] = password_hash
    save_users(users)
    return True

def get_email_by_username(username):
    users = load_users()
    return users.get(username, {}).get("email")

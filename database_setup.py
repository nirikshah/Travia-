import sqlite3

# Create a database (or connect to an existing one)
conn = sqlite3.connect('chatbot_app.db')
cursor = conn.cursor()

# Create a table for users (for registration and login)
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL)''')

# Create a table for chat logs (to track user questions)
cursor.execute('''CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    prompt TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')

conn.commit()
conn.close()

print("Database setup complete!")

import streamlit as st
import pandas as pd
import os
import json

FEEDBACK_FILE = "feedback.json"
CHAT_LOG_FILE = "chat_logs.json"
ACCURACY_LOG_FILE = "accuracy_logs.json"

def load_json_lines_to_df(file_path):
    try:
        with open(file_path, "r") as f:
            data = [json.loads(line) for line in f if line.strip()]
        return pd.DataFrame(data)
    except Exception as e:
        st.warning(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

def render_admin_dashboard():
    st.title("📊 Admin Dashboard")

    # --- Feedback Section ---
    st.subheader("📝 User Feedback")
    if os.path.exists(FEEDBACK_FILE):
        feedback_df = load_json_lines_to_df(FEEDBACK_FILE)
        if not feedback_df.empty:
            st.dataframe(feedback_df)

            st.subheader("📈 Feedback Analytics")
            if "model" in feedback_df.columns:
                st.bar_chart(feedback_df["model"].value_counts())

            if "rating" in feedback_df.columns:
                st.line_chart(feedback_df["rating"].value_counts().sort_index())

            if "suggestions" in feedback_df.columns:
                st.write("💬 User Suggestions:")
                for suggestion in feedback_df["suggestions"].dropna():
                    st.markdown(f"- {suggestion}")
        else:
            st.info("No feedback entries yet.")
    else:
        st.info("No feedback data available.")

    # --- Chat Logs Section ---
    st.subheader("🗂️ User Chat Logs")
    if os.path.exists(CHAT_LOG_FILE):
        chat_df = load_json_lines_to_df(CHAT_LOG_FILE)
        if not chat_df.empty:
            st.dataframe(chat_df)
        else:
            st.info("No chat log entries yet.")
    else:
        st.info("No chat logs found.")

    # --- Accuracy Logs Section ---
    st.subheader("📉 Accuracy Logs")
    if os.path.exists(ACCURACY_LOG_FILE):
        accuracy_df = load_json_lines_to_df(ACCURACY_LOG_FILE)
        if not accuracy_df.empty:
            st.dataframe(accuracy_df)

            st.subheader("🔍 Accuracy Score Trends")
            if "scores" in accuracy_df.columns:
                exploded = accuracy_df.explode("scores")
                # Or manually normalize for graphing
                all_scores = []
                for _, row in accuracy_df.iterrows():
                    for model, score in row["scores"].items():
                        all_scores.append({"timestamp": row["timestamp"], "model": model, "score": score})
                scores_df = pd.DataFrame(all_scores)
                st.line_chart(scores_df.pivot(index="timestamp", columns="model", values="score"))
        else:
            st.info("No accuracy logs yet.")
    else:
        st.info("No accuracy logs found.")

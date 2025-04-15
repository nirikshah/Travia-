import streamlit as st

# Autocomplete input using Geoapify Autocomplete API
def autocomplete_input(label):
    return st.text_input(label)

# Display each LLM response with upvote/downvote and details
def render_llm_response(model, response):
    st.subheader(f"{model} Recommendations")
    st.markdown(f"**Place:** {response.get('place', 'N/A')}")
    st.markdown(f"**State:** {response.get('state', 'N/A')}")
    st.markdown(f"**Country:** {response.get('country', 'N/A')}")
    st.markdown(f"**Best Time to Visit:** {response.get('best_time_to_visit', 'N/A')}")
    st.markdown(f"**Season:** {response.get('season', 'N/A')}")
    st.markdown(f"**Description:** {response.get('description', 'N/A')}")
    st.markdown(f"**Nearby Hangouts:** {', '.join(response.get('hangouts', []))}")
    st.markdown(f"**Hotels/Hostels:** {', '.join(response.get('hotels', []))}")
    st.markdown(f"**Restaurants:** {', '.join(response.get('restaurants', []))}")

    # Upvote/Downvote buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button(f"👍 Upvote {model}", key=f"{model}_upvote")
    with col2:
        st.button(f"👎 Downvote {model}", key=f"{model}_downvote")

    st.markdown("---")

# Feedback form UI
def render_feedback_form():
    st.subheader("Share Your Feedback")
    review = st.text_area("How was your experience?")
    helpful = st.radio("Was the suggestion helpful?", ("Yes", "No"))
    uploaded_files = st.file_uploader("Upload photos/videos", accept_multiple_files=True)
    suggestions = st.text_input("What can we improve?")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback! 🙌")

import streamlit as st
import json
import time

# Function to translate roles between Gemini and Streamlit terminology
def map_role(role):
    if role == "model":
        return "assistant"
    else:
        return role

def fetch_gemini_response(user_query):
    # Use the session's model to generate a response
    response = st.session_state.chat_session.model.generate_content(user_query)
    return response.parts[0].text

# Function for lottie file
def load_lottie_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def track_time_spent(feature_key):
    start_key = f"{feature_key}_start_time"
    
    # Initialize start time if not present
    if start_key not in st.session_state:
        st.session_state[start_key] = time.time()
    
    # Calculate elapsed time
    elapsed = int(time.time() - st.session_state[start_key])
    
    # Display Timer in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏱️ Feature Timer")
    st.sidebar.write(f"Time Spent: {elapsed}s")
    
    # Mark as used if > 60 seconds (1 minute)
    if elapsed > 60:
        st.session_state[feature_key] = True
        st.sidebar.success("✅ Feature Marked as Used!")
        st.sidebar.progress(1.0)
    else:
        # Progress bar based on 2 minutes (120s) visual goal, but ticks at 60s
        st.sidebar.progress(min(elapsed / 60, 1.0), text="Spend 1 min to track")
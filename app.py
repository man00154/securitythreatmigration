import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables for local testing
# In a real Streamlit deployment, you should use st.secrets for API keys
load_dotenv()

# --- Configuration ---
# The user-specified model and API URL
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

# Get the API key from environment variables (local) or Streamlit secrets (deployment)
# Use st.secrets in a production Streamlit app
API_KEY = os.getenv("API_KEY")

# --- Streamlit App UI ---
st.set_page_config(
    page_title="GenAI Threat Mitigation",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🛡️ MANISH - GenAI-Powered Proactive Threat Mitigation")
st.markdown("### A Virtual Security Analyst at your service.")
st.markdown(
    """
This application uses a lightweight Gemini model to analyze a given network or system log snippet.
It acts as a simple virtual security analyst, identifying potential threats and suggesting basic preventative measures.
"""
)

# Text area for user input (logs, events, etc.)
user_input = st.text_area(
    "Paste network logs, system events, or a description of an observed behavior here:",
    height=200,
    placeholder="Example: 'Unusual outbound traffic from a web server on port 22 to an unknown IP address.'"
)

# Button to trigger analysis
if st.button("Analyze Threat", type="primary"):
    if not user_input:
        st.error("Please enter some data to analyze.")
    elif not API_KEY:
        st.error("API key not found. Please set the 'API_KEY' environment variable or a Streamlit secret.")
    else:
        # Simple loading spinner
        with st.spinner("Analyzing... Awaiting virtual security analyst's report..."):
            try:
                # Construct the prompt for the Gemini API
                prompt = (
                    "You are a very simple virtual security analyst. Analyze the following system event "
                    "or network log description. Identify any potential threats. Then, in a new paragraph, "
                    "provide a single, very simple, and actionable preventative measure. "
                    "Keep your response concise and to the point.\n\n"
                    f"Event: {user_input}"
                )
                
                # Payload for the API request
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                      "temperature": 0.5,
                      "topP": 0.95,
                      "topK": 64,
                      "maxOutputTokens": 1024,
                      "stopSequences": [],
                    }
                }
                
                headers = {
                    "Content-Type": "application/json"
                }

                # Make the API call
                response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, data=json.dumps(payload))
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                
                # Parse and display the response
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    analysis_text = result['candidates'][0]['content']['parts'][0]['text']
                    st.success("### Analysis Complete")
                    st.info(analysis_text)
                else:
                    st.warning("No analysis could be generated. The model may have returned an empty response.")
            
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while calling the API: {e}")
            except (KeyError, IndexError) as e:
                st.error(f"Could not parse the API response. Error: {e}")

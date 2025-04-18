"""Script for frontend using Streamlit"""
import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Conversational Learning Assistant", layout="wide")

# Use environment variable with fallback
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Session state to store session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Function to clear session and show message


def end_session():
    if st.session_state.session_id:
        response = requests.post(
            f"{API_BASE_URL}/end_session/",
            params={"session_id": st.session_state.session_id},
            timeout=10000)
        if response.status_code == 200:
            st.session_state.session_id = None
            st.success("Session ended successfully!")
            st.rerun()  # This will clear the screen and restart the app
        else:
            st.error("Error clearing session.")


# Main UI
st.title("📚 Conversational Learning Assistant")
st.write("Upload a textbook and ask questions about its content.")

# Upload PDF section
uploaded_file = st.file_uploader("Upload a PDF book", type=["pdf"])
if uploaded_file is not None and st.session_state.session_id is None:
    with st.spinner("Processing book..."):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{API_BASE_URL}/upload/",
                                 files=files, timeout=10000)

        if response.status_code == 200:
            st.session_state.session_id = response.json()["session_id"]
            st.success("Book uploaded successfully! You can now ask questions.")
        else:
            st.error("Error processing the book.")

# Chat interface
if st.session_state.session_id:
    st.subheader("💬 Ask Questions")
    user_query = st.text_input("Enter your question:")
    if st.button("Ask"):
        if user_query:
            with st.spinner("Fetching response..."):
                response = requests.get(f"{API_BASE_URL}/query/", params={
                                        "query": user_query,
                                        "session_id": st.session_state.session_id},
                                        timeout=10000)

                if response.status_code == 200:
                    result = response.json()
                    st.write("**Answer:**", result["answer"])

                    if result["references"]:
                        with st.expander("📖 References from the book"):
                            for ref in result["references"]:
                                st.write(ref)
                else:
                    st.error("Error retrieving response.")

    # End session button
    if st.button("End Session", type="primary"):
        end_session()

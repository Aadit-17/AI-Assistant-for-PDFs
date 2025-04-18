"""Main Script for Conversational AI Chatbot using PostgreSQL-pgvector"""
import io
import os
import threading
import time
import traceback
from uuid import uuid4
import psycopg2
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from utils import store_text_in_postgres, query_postgres
from ollama_model import generate_response
from pdf_processor import extract_text_from_pdf
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# PostgreSQL Database Configuration
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Connect to PostgreSQL


def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}")


# Track user sessions & auto-delete timers
session_store = {}
session_timers = {}

SESSION_TIMEOUT = 1800  # Auto-delete session data after 30 minutes
DAILY_CLEANUP_INTERVAL = 86400  # 24 hours


def get_session_id():
    """Generate a unique session ID for each user."""
    session_id = str(uuid4())
    session_store[session_id] = []
    return session_id


def delete_session_data(session_id):
    """Delete session data from PostgreSQL."""
    if session_id in session_store:
        doc_ids = session_store.pop(session_id, [])
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM book_embeddings WHERE id = ANY(%s)", (doc_ids,))
            conn.commit()
            cur.close()
            conn.close()
            print(f"Session {session_id} data deleted due to timeout.")
        except Exception as e:
            print(f"Error deleting session data: {e}")


@app.get("/test")
async def test_endpoint(input_string: str):
    """Test endpoint that returns the input string."""
    return {"message": input_string}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), session_id: str = Depends(get_session_id)):
    """Upload & process a book without storing it on disk."""
    try:
        pdf_bytes = await file.read()
        pdf_stream = io.BytesIO(pdf_bytes)

        # Extract text & store in PostgreSQL
        text_chunks = extract_text_from_pdf(pdf_stream)
        doc_ids = store_text_in_postgres(text_chunks)

        # Track session data
        session_store[session_id].extend(doc_ids)

        # Auto-delete after timeout
        if session_id in session_timers:
            session_timers[session_id].cancel()
        session_timers[session_id] = threading.Timer(
            SESSION_TIMEOUT, delete_session_data, [session_id]
        )
        session_timers[session_id].start()

        return {"message": "Book uploaded and processed.", "session_id": session_id}
    except Exception as e:
        print(f"Error processing book: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error processing book: {str(e)}")


@app.get("/query/")
async def query_text(query: str, session_id: str):
    """Retrieve book data & generate AI response."""
    if session_id not in session_store:
        return {"error": "Invalid session ID or expired session."}

    try:
        results = query_postgres(query)
        response = generate_response(query, results)
        return {"query": query, "answer": response, "references": results}
    except Exception as e:
        print(f"Error querying text: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error querying text: {str(e)}")


@app.post("/end_session/")
async def end_session(session_id: str):
    """Manually clear session data from PostgreSQL."""
    if session_id in session_store:
        try:
            delete_session_data(session_id)
            if session_id in session_timers:
                session_timers[session_id].cancel()
                del session_timers[session_id]
            return {"message": "Session data cleared successfully."}
        except Exception as e:
            print(f"Error ending session: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error ending session: {str(e)}")
    return {"message": "Session ID not found or already deleted."}


def clear_entire_postgres():
    """Function to clear all stored data from PostgreSQL every 24 hours."""
    print("Starting PostgreSQL cleanup...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM book_embeddings")
        conn.commit()
        cur.close()
        conn.close()
        print("Cleanup completed.")
    except Exception as e:
        print(f"Error during cleanup: {e}")


def start_daily_cleanup():
    """Start a background thread to clear PostgreSQL every 24 hours."""
    while True:
        time.sleep(DAILY_CLEANUP_INTERVAL)
        clear_entire_postgres()


# Start the daily cleanup in a separate thread
cleanup_thread = threading.Thread(target=start_daily_cleanup, daemon=True)
cleanup_thread.start()

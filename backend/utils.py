"""PostgreSQL database utilities"""
import numpy as np
import psycopg2
import os
import traceback
from uuid import uuid4
from sklearn.preprocessing import normalize

# Database configuration
DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")


def get_db_connection():
    """Get a database connection."""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        print(traceback.format_exc())
        raise


def ensure_table_exists():
    """Ensure the required table exists."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_embeddings (
            id UUID PRIMARY KEY,
            text TEXT,
            embedding FLOAT8[]
        );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error ensuring table exists: {e}")
        print(traceback.format_exc())
        raise


def basic_embedding(text):
    """Generate a simple numerical embedding from text."""
    try:
        vector = np.array([ord(char)
                          for char in text[:300]])  # Truncate or pad
        vector = np.pad(vector, (0, 300 - len(vector)),
                        'constant')  # Ensure fixed length
        return normalize([vector])[0].tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        print(traceback.format_exc())
        raise


def store_text_in_postgres(text_chunks):
    """Store extracted text in PostgreSQL with embeddings."""
    try:
        ensure_table_exists()
        conn = get_db_connection()
        cursor = conn.cursor()
        doc_ids = []
        for chunk in text_chunks:
            doc_id = uuid4()
            embedding = basic_embedding(chunk)
            cursor.execute(
                "INSERT INTO book_embeddings (id, text, embedding) VALUES (%s, %s, %s)",
                (doc_id, chunk, embedding)
            )
            doc_ids.append(doc_id)
        conn.commit()
        cursor.close()
        conn.close()
        return doc_ids
    except Exception as e:
        print(f"Error storing text in PostgreSQL: {e}")
        print(traceback.format_exc())
        raise


def query_postgres(query_text):
    """Retrieve relevant text using cosine similarity."""
    try:
        ensure_table_exists()
        conn = get_db_connection()
        cursor = conn.cursor()
        query_emb = basic_embedding(query_text)
        cursor.execute(
            "SELECT text, embedding FROM book_embeddings"
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Compute cosine similarity
        similarities = [(text, np.dot(query_emb, np.array(emb)))
                        for text, emb in results]
        similarities.sort(key=lambda x: x[1], reverse=True)

        return [text for text, _ in similarities[:5]]  # Top 5 matches
    except Exception as e:
        print(f"Error querying PostgreSQL: {e}")
        print(traceback.format_exc())
        raise

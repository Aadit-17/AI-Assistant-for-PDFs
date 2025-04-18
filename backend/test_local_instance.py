"""Local testing utilities for development without PostgreSQL"""
import numpy as np
from uuid import uuid4
from sklearn.preprocessing import normalize

# In-memory storage for local development
local_storage = {}


def basic_embedding(text):
    """Generate a simple numerical embedding from text."""
    vector = np.array([ord(char) for char in text[:300]])  # Truncate or pad
    vector = np.pad(vector, (0, 300 - len(vector)),
                    'constant')  # Ensure fixed length
    return normalize([vector])[0].tolist()


def store_text_in_memory(text_chunks):
    """Store extracted text in memory with embeddings."""
    doc_ids = []
    for chunk in text_chunks:
        doc_id = str(uuid4())
        embedding = basic_embedding(chunk)
        local_storage[doc_id] = (chunk, embedding)
        doc_ids.append(doc_id)
    return doc_ids


def query_memory(query_text):
    """Retrieve relevant text using cosine similarity from memory."""
    query_emb = basic_embedding(query_text)
    results = [(text, np.dot(query_emb, np.array(emb)))
               for text, emb in local_storage.values()]
    results.sort(key=lambda x: x[1], reverse=True)
    return [text for text, _ in results[:5]]


def clear_memory():
    """Clear all data from memory storage."""
    local_storage.clear()


def delete_from_memory(doc_ids):
    """Delete specific documents from memory storage."""
    for doc_id in doc_ids:
        local_storage.pop(doc_id, None)

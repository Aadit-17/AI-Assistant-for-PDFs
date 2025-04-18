# PDF AI Assistant

A web application that allows users to upload PDF documents and interact with them using AI-powered conversations. The application uses PostgreSQL with pgvector for efficient text storage and retrieval, and provides a modern Streamlit frontend for user interaction.

## Features

- PDF document upload and processing
- AI-powered conversation with document content
- Efficient text storage using PostgreSQL
- Modern and responsive user interface
- Session management with auto-cleanup
- Secure database connections

## Architecture

The project consists of three main components:

1. **FastAPI Backend**
   - Handles PDF processing and text extraction
   - Manages database operations
   - Provides REST API endpoints
   - Implements session management

2. **Streamlit Frontend**
   - User-friendly interface for document upload
   - Real-time chat interface
   - Responsive design
   - Session management

3. **PostgreSQL Database**
   - Stores document text and embeddings
   - Efficient text retrieval
   - Automatic cleanup of old data

## API Endpoints

- `POST /upload/`: Upload and process PDF documents
- `GET /query/`: Query the document content
- `POST /end_session/`: End a user session
- `GET /test`: Test endpoint for health checks

## Local Development

### Prerequisites

- Python 3.8+
- PostgreSQL
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pdf-ai-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   # Backend dependencies
   cd backend
   pip install -r requirements.txt

   # Frontend dependencies
   cd ../frontend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the backend directory with:
   ```
   POSTGRES_DB=your_db_name
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

5. Run the services:
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn main:app --reload --port 8000

   # Terminal 2 - Frontend
   cd frontend
   streamlit run app.py
   ```
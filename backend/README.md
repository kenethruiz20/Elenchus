# Elenchus Backend - Research Controller System

## Overview

This backend provides a comprehensive research management system for the Elenchus Legal AI assistant. It manages LLM chat sessions (research conversations), sources, notes, and messages through a REST API built with FastAPI and MongoDB.

## Architecture

### Technology Stack
- **FastAPI**: Modern Python web framework for building APIs
- **MongoDB**: NoSQL document database for flexible data storage
- **Beanie**: Async ODM (Object Document Mapper) with Pydantic integration
- **Motor**: Async MongoDB driver for Python
- **Docker**: Containerization for development and deployment

### Database Models

#### Research (Chat Sessions)
Represents an LLM chat session similar to ChatPanel.tsx component.

**Fields:**
- `id`: Unique identifier (ObjectId)
- `title`: Research/conversation title
- `user_id`: Owner of the research session
- `source_ids`: Array of source document IDs
- `note_ids`: Array of note IDs
- `model`: Model ID being used (default: "gemini-1.5-flash")
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### Message
Stores individual chat messages within research sessions.

**Fields:**
- `id`: Unique identifier
- `research_id`: Associated research session ID
- `content`: Message content
- `role`: Message role ("user", "assistant", "system")
- `sequence_number`: Order within conversation
- `created_at`: Timestamp

#### Source
Manages legal documents and references.

**Fields:**
- `id`: Unique identifier
- `title`: Document title
- `content`: Document text content
- `file_type`: Type (pdf, docx, txt, url, etc.)
- `file_size`: Size in bytes
- `file_path`: Storage path
- `processing_status`: Status (pending, processing, completed, error)
- `created_at`: Upload timestamp

#### Note
User annotations and notes.

**Fields:**
- `id`: Unique identifier
- `title`: Note title
- `content`: Note content (supports markdown)
- `research_id`: Optional associated research ID
- `tags`: Array of tags for organization
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## API Endpoints

### Research Management

#### Create Research
```http
POST /api/v1/research/
Content-Type: application/json

{
  "title": "Contract Analysis Session",
  "model": "gemini-1.5-flash"
}
```

#### List Research
```http
GET /api/v1/research/
```

#### Get Research
```http
GET /api/v1/research/{research_id}
```

#### Update Research
```http
PUT /api/v1/research/{research_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "source_ids": ["source_id_1", "source_id_2"],
  "note_ids": ["note_id_1"]
}
```

#### Delete Research
```http
DELETE /api/v1/research/{research_id}
```

### Messages Management

#### Send Message
```http
POST /api/v1/messages/research/{research_id}/send
Content-Type: application/json

{
  "content": "Analyze this contract for potential risks",
  "context": {
    "use_sources": true,
    "use_notes": false
  }
}
```

#### Get Messages
```http
GET /api/v1/messages/research/{research_id}
```

#### Delete Message
```http
DELETE /api/v1/messages/{message_id}
```

### Sources Management

#### Upload Source
```http
POST /api/v1/sources/
Content-Type: multipart/form-data

file: [binary file data]
```

#### List Sources
```http
GET /api/v1/sources/
```

#### Get Source
```http
GET /api/v1/sources/{source_id}
```

#### Update Source
```http
PUT /api/v1/sources/{source_id}
Content-Type: application/json

{
  "title": "Updated Contract.pdf"
}
```

#### Delete Source
```http
DELETE /api/v1/sources/{source_id}
```

### Notes Management

#### Create Note
```http
POST /api/v1/notes/
Content-Type: application/json

{
  "title": "Key Findings",
  "content": "## Important clauses\n- Liability section needs review",
  "research_id": "research_id_here",
  "tags": ["contract", "liability"]
}
```

#### List Notes
```http
GET /api/v1/notes/
```

#### Get Note
```http
GET /api/v1/notes/{note_id}
```

#### Update Note
```http
PUT /api/v1/notes/{note_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content"
}
```

#### Delete Note
```http
DELETE /api/v1/notes/{note_id}
```

## Database Collections

### MongoDB Setup

The system creates the following collections with optimized indexes:

#### Collections:
- `research`: Research/conversation sessions
- `messages`: Chat messages
- `sources`: Legal documents and references  
- `notes`: User annotations

#### Indexes:
- **research**: `user_id + created_at` (compound), `title` (text search)
- **messages**: `research_id + sequence_number` (compound)
- **sources**: `user_id + created_at` (compound), `title` (text search)
- **notes**: `user_id + created_at` (compound), `research_id`, `tags`

## Installation & Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- MongoDB (or use Docker setup)

### Development Setup

1. **Clone and navigate to backend:**
```bash
cd /Users/amadrazo/Desktop/dev/legalai/Elenchus/backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements/mongodb.txt
```

4. **Set up environment variables:**
Create `.env` file:
```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=elenchus_dev

# API Settings
APP_NAME=Elenchus Backend
APP_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Google Gemini (optional)
GOOGLE_API_KEY=your_api_key_here
```

### Docker Setup (Recommended)

1. **Start full stack with Docker Compose:**
```bash
# From project root
docker-compose up --build
```

This starts:
- MongoDB database (port 27017)
- Backend API (port 8000)
- Frontend (port 3000)
- Redis cache (port 6379)

2. **Start only backend services:**
```bash
docker-compose up mongodb backend --build
```

### Running the Application

#### Development Mode
```bash
# With uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

#### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, access interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Testing

### Manual Testing

1. **Health Check:**
```bash
curl http://localhost:8000/health
```

2. **Create Research:**
```bash
curl -X POST "http://localhost:8000/api/v1/research/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Research", "model": "gemini-1.5-flash"}'
```

3. **List Research:**
```bash
curl http://localhost:8000/api/v1/research/
```

### Using the API

The API follows RESTful conventions and returns JSON responses. All endpoints support:
- **Authentication**: User ID extracted from session/token
- **Validation**: Pydantic models ensure data integrity
- **Error Handling**: Consistent HTTP status codes and error messages
- **Async Operations**: Non-blocking I/O for better performance

### Integration with Frontend

The frontend (Next.js) can integrate with this backend by:

1. **Updating API calls** in frontend components to use backend endpoints
2. **Configuring CORS** to allow frontend domain
3. **Managing authentication** state between frontend and backend
4. **Implementing real-time updates** via WebSockets (future enhancement)

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── research.py      # Research CRUD endpoints
│   │   │   ├── messages.py      # Messages management
│   │   │   ├── sources.py       # Sources handling
│   │   │   ├── notes.py         # Notes management
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── config/
│   │   ├── database.py          # MongoDB connection & setup
│   │   └── settings.py          # App configuration
│   ├── models/
│   │   ├── research.py          # Research document model
│   │   ├── message.py           # Message document model
│   │   ├── source.py            # Source document model
│   │   ├── note.py              # Note document model
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── research.py          # Research Pydantic schemas
│   │   ├── message.py           # Message schemas
│   │   ├── source.py            # Source schemas
│   │   ├── note.py              # Note schemas
│   │   └── __init__.py
│   └── main.py                  # FastAPI application entry point
├── docker/
│   ├── Dockerfile.mongodb       # MongoDB container config
│   └── mongo-init/
│       └── 01-init-db.js        # Database initialization script
├── requirements/
│   └── mongodb.txt              # MongoDB-specific dependencies
├── requirements.txt             # Base Python dependencies
└── README.md                    # This file
```

## Next Steps

1. **Testing**: Add comprehensive test suite with pytest
2. **Authentication**: Implement proper user authentication/authorization
3. **File Processing**: Add document parsing for PDF/DOCX sources
4. **Real-time Updates**: WebSocket support for live chat updates
5. **Caching**: Redis integration for improved performance
6. **Monitoring**: Add logging, metrics, and health monitoring
7. **AI Integration**: Connect to Google Gemini API for actual responses

## Troubleshooting

### Common Issues

1. **BSON Import Error**: 
   - Ensure only `pymongo` is installed, not standalone `bson` package
   - Run: `pip uninstall bson -y`

2. **MongoDB Connection Failed**:
   - Check MongoDB is running: `docker-compose up mongodb`
   - Verify connection string in `.env`

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Port Conflicts**:
   - Change ports in `docker-compose.yml` if 8000/27017 are in use
   - Update CORS origins in settings

### Development Tips

- Use `docker-compose logs backend` to view backend logs
- Access MongoDB directly: `docker exec -it elenchus-mongodb mongo`
- API documentation updates automatically with code changes
- Use Pydantic models for consistent validation across the application
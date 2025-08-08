# Elenchus - Legal AI Assistant

A hybrid legal AI assistant application with RAG (Retrieval Augmented Generation) capabilities, featuring a modern frontend that replicates Google's NotebookLM interface and a powerful FastAPI backend with Google Gemini AI integration.

![Elenchus Legal AI](https://via.placeholder.com/800x400/1e293b/f8fafc?text=Elenchus+Legal+AI)

## 🚀 Features

### ✅ Core Features
- **Three-Panel Layout**: Sources (left), Chat (center), and Studio (right) panels
- **Dark Theme**: Professional legal interface with modern design
- **Document Processing**: Upload and process PDFs, DOCs, and text files
- **RAG-Powered Chat**: AI chat with document context and citations
- **Vector Search**: Semantic search through uploaded documents
- **Notes Management**: Create legal briefs, case analyses, and research notes
- **Background Processing**: Asynchronous document processing pipeline
- **Export Functionality**: Export conversations and notes to markdown

### 🔧 Advanced Features
- **Document Chunking**: Intelligent text segmentation for better retrieval
- **Embedding Generation**: Vector embeddings with sentence-transformers
- **Multi-tenancy**: User-isolated data and document access
- **Google Cloud Storage**: Scalable file storage with structured paths
- **Task Queue**: Background job processing with Redis Queue
- **Real-time Monitoring**: RQ Dashboard for task monitoring

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 + React 18 + TypeScript
- **Styling**: Tailwind CSS with custom dark theme
- **State Management**: Zustand with localStorage persistence
- **Icons**: Lucide React
- **Development**: ESLint + TypeScript strict mode

### Backend & RAG Stack
- **API Framework**: FastAPI + Python 3.11
- **Database**: MongoDB with Beanie ODM
- **Vector Database**: Qdrant for similarity search
- **Task Queue**: Redis + RQ (Redis Queue)
- **AI Integration**: Google Gemini 1.5 Flash
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **File Storage**: Google Cloud Storage
- **Authentication**: JWT with OAuth 2.0 support
- **Deployment**: Docker + Google Cloud Run

## 📦 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+ and pip
- **Docker** and Docker Compose
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### 🚀 Development Setup (Recommended)

**1. Clone and Setup Environment**
```bash
git clone <repository-url>
cd Elenchus

# Copy and configure environment file
cp backend/.env.example backend/.env
```

**2. Configure Environment Variables**
Edit `backend/.env` and add your configuration:
```bash
# Required: Add your Google Gemini API key
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional: Google Cloud Storage (for file uploads)
GCP_PROJECT=your-gcp-project-id
GCP_BUCKET=your-gcs-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
```

**3. Setup Backend Dependencies**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/base.txt
pip install -r requirements/mongodb.txt
pip install -r requirements/rag.txt
cd ..
```

**4. Setup Frontend Dependencies**
```bash
npm install
```

**5. Start Development Environment**
```bash
# This script starts all infrastructure and runs frontend/backend locally
./devrun.sh
```

This starts:
- **MongoDB** and **RAG infrastructure** in Docker containers
- **Backend** with debugging on `http://localhost:8000`
- **Frontend** with hot reload on `http://localhost:3000`

### 🐳 Production Docker Setup

**Start Full Production Stack:**
```bash
# Configure environment (same as development)
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start full production stack
docker-compose up -d --build

# Or use the Docker manager
./docker-manager.sh prod up --build
```

Production URLs:
- **Application**: http://localhost:3001
- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 🔧 Environment Configuration

### Required Environment Variables

Create `backend/.env` with these essential settings:

```bash
# Application Settings
APP_NAME="Elenchus Legal AI"
DEBUG=true
SECRET_KEY=your-super-secret-key-at-least-32-characters-long

# Database - MongoDB (automatically configured for Docker)
MONGODB_URL=mongodb://elenchus_admin:elenchus_password_2024@localhost:27018/elenchus?authSource=admin
MONGODB_DATABASE=elenchus

# Google AI API (REQUIRED)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# RAG Stack Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=legal_documents
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBED_DIMENSION=384

# Google Cloud Platform (Optional - for file storage)
GCP_PROJECT=your-gcp-project-id
GCP_BUCKET=your-gcs-bucket-name
GCP_BUCKET_BASE_PATH=user_docs
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json

# Performance Settings
MAX_CHUNK_SIZE=800
CHUNK_OVERLAP=100
SEARCH_TOP_K=8

# Background Processing
RQ_REDIS_URL=redis://:rag_queue_password@localhost:6380/1
WORKER_CONCURRENCY=4
TASK_TIMEOUT=3600
```

### Optional: Google Cloud Storage Setup

For file upload functionality:

1. **Create GCS Bucket**: Create a bucket in Google Cloud Console
2. **Create Service Account**: Generate a service account key
3. **Download Credentials**: Save as `backend/gcp-credentials.json`
4. **Update Environment**: Set `GCP_PROJECT` and `GCP_BUCKET` in `.env`

## 🎯 Development Workflow

### Using devrun.sh (Recommended)

The `devrun.sh` script provides a complete development environment:

```bash
./devrun.sh
```

**Features:**
- ✅ Automatically starts Docker infrastructure (MongoDB, Qdrant, Redis)
- ✅ Runs backend with debugging support (port 5678)
- ✅ Runs frontend with hot module replacement
- ✅ Health checks for all services
- ✅ Real-time log aggregation
- ✅ Graceful shutdown with Ctrl+C

**Development URLs:**
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Debug Port**: localhost:5678
- **Qdrant**: http://localhost:6333
- **RQ Dashboard**: http://localhost:9181

### Manual Development Setup

If you prefer to run services individually:

```bash
# 1. Start infrastructure
docker-compose -f docker-compose.dev.yml up -d

# 2. Start backend (in separate terminal)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Start frontend (in separate terminal)
npm run dev
```

## 🐳 Docker Management

### Using Docker Manager Script

Convenient script for managing different environments:

```bash
# Development (infrastructure only)
./docker-manager.sh dev up          # Start MongoDB + RAG stack
./docker-manager.sh dev up --worker # Include background worker
./docker-manager.sh dev logs        # View logs
./docker-manager.sh dev down        # Stop services

# Production (full stack)
./docker-manager.sh prod up --build # Build and start everything
./docker-manager.sh prod status     # Check service health
./docker-manager.sh prod logs       # View logs
./docker-manager.sh prod down       # Stop all services
```

### Manual Docker Commands

```bash
# Development infrastructure
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml logs -f
docker-compose -f docker-compose.dev.yml down

# Production full stack
docker-compose up -d --build
docker-compose logs -f
docker-compose down
```

## 🌐 Service Access Points

### Development Mode
| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| Backend | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Debugger | localhost:5678 | Backend debugging port |
| MongoDB | localhost:27018 | Database |
| Qdrant | http://localhost:6333 | Vector database |
| Redis RAG | localhost:6380 | Task queue |
| RQ Dashboard | http://localhost:9181 | Job monitoring |

### Production Mode
| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3001 | Main application |
| Backend | http://localhost:8001 | REST API |
| API Docs | http://localhost:8001/docs | Swagger documentation |
| RQ Dashboard | http://localhost:9181 | Job monitoring |

## 📁 Project Structure

```
Elenchus/
├── README.md                    # This file
├── docker-compose.yml          # Production: Full stack
├── docker-compose.dev.yml      # Development: Infrastructure only  
├── devrun.sh                   # Development runner script
├── docker-manager.sh           # Docker environment manager
├── 
├── components/                 # React components
│   ├── ChatPanel.tsx          # Chat interface with RAG
│   ├── SourcesPanel.tsx       # Document management
│   └── StudioPanel.tsx        # Notes and export tools
├── store/                     # State management
│   └── useStore.ts           # Zustand store with persistence
├── 
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── api/v1/           # REST API endpoints
│   │   ├── models/           # MongoDB models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── rag_service.py      # Vector search & embeddings
│   │   │   ├── document_processor.py # Document parsing
│   │   │   └── rag_worker.py       # Background processing
│   │   └── config/           # Configuration
│   ├── requirements/         # Python dependencies
│   │   ├── base.txt         # Core dependencies
│   │   ├── mongodb.txt      # Database support
│   │   └── rag.txt          # RAG stack dependencies
│   ├── docker/              # Docker configurations
│   └── scripts/             # Utility scripts
└── RAG_IMPLEMENTATION_PLAN.md # Development roadmap
```

## 🎯 Usage Guide

### Getting Started
1. **Start Development**: Run `./devrun.sh` for complete setup
2. **Add Documents**: Upload PDFs, DOCs, or text files via Sources panel
3. **Wait for Processing**: Documents are processed in background
4. **Start Chatting**: Ask questions about your documents
5. **Create Notes**: Generate legal briefs, analyses, and research notes
6. **Export Results**: Download conversations and notes

### Key Features
- **Document Upload**: Drag & drop or click to upload legal documents
- **RAG Chat**: AI responses with document context and citations
- **Smart Search**: Vector-based similarity search through documents
- **Background Processing**: Asynchronous document processing pipeline
- **Export Tools**: Download conversations and notes in markdown format
- **Multi-format Support**: PDF, DOC, DOCX, and TXT files

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Upload document (requires authentication)
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"

# Search documents
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "contract terms", "top_k": 5}'
```

## 🚧 Development & Testing

### RAG Stack Testing
```bash
# Test RAG setup (from backend directory)
cd backend
python scripts/test_rag_setup.py
```

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
npm run test
```

### Debugging
- **Backend**: Attach debugger to port 5678 when using `devrun.sh`
- **Frontend**: Use React DevTools browser extension
- **Logs**: Check `logs/` directory or use `docker-compose logs`

## 🔒 Security & Authentication

- **JWT Authentication**: Secure API access
- **User Isolation**: Multi-tenant data separation
- **File Validation**: Document type and size limits
- **Environment Secrets**: Secure API key management

## 🚀 Deployment

### Google Cloud Run (Recommended)
```bash
# Build and deploy
./backend/deploy.sh
```

### Manual Docker Deployment
```bash
# Production build
docker-compose up -d --build

# Scale services
docker-compose up -d --scale rag-worker=3
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the development setup above
4. Make changes and test thoroughly
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for language model capabilities
- Qdrant for vector database technology
- FastAPI for the excellent Python web framework
- Next.js and Tailwind CSS for modern web development

---

**Need Help?** 
- 📚 Check the [API Documentation](http://localhost:8000/docs) 
- 🐛 Report issues in GitHub Issues
- 💬 Join discussions in GitHub Discussions
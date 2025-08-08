#!/bin/bash
# RAG Stack Stage 1 Setup Script
# Sets up the infrastructure and tests connectivity

set -e

echo "🚀 Setting up RAG Stack - Stage 1"
echo "=================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}[STEP]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "app/config/settings.py" ]]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

# Step 1: Check Docker and Docker Compose
print_step "Checking Docker setup"
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Step 2: Install Python dependencies
print_step "Installing RAG dependencies"
if [[ -f "./venv/bin/activate" ]]; then
    source ./venv/bin/activate
    print_status "Activated virtual environment"
else
    print_warning "Virtual environment not found. Make sure you're in the correct backend directory."
fi

# Install RAG requirements
pip install -r requirements/rag.txt
print_status "RAG dependencies installed"

# Step 3: Start RAG infrastructure
print_step "Starting RAG infrastructure services"
cd ..
docker-compose -f docker-compose.dev.yml up -d
cd backend

print_status "Waiting for services to start..."
sleep 10

# Step 4: Check service health
print_step "Checking service health"

# Check Qdrant
print_status "Checking Qdrant..."
if curl -s http://localhost:6333/health > /dev/null; then
    print_status "✅ Qdrant is healthy"
else
    print_warning "⚠️  Qdrant may not be ready yet"
fi

# Check Redis RAG
print_status "Checking Redis RAG..."
if docker exec elenchus-redis-rag-dev redis-cli -a rag_queue_password ping > /dev/null 2>&1; then
    print_status "✅ Redis RAG is healthy"
else
    print_warning "⚠️  Redis RAG may not be ready yet"
fi

# Step 5: Test RAG setup
print_step "Running RAG setup tests"
python scripts/test_rag_setup.py

# Step 6: Display service information
print_step "Service Information"
echo "==================="
echo "🗃️  Qdrant Vector DB:     http://localhost:6333"
echo "🔄 Redis RAG Queue:       localhost:6380"
echo "📊 RQ Dashboard:          http://localhost:9181"
echo ""
echo "Configuration:"
echo "- Embedding Model:        sentence-transformers/all-MiniLM-L6-v2"
echo "- Embedding Dimension:    384"
echo "- Vector Collection:      legal_documents"
echo "- Max Chunk Size:         800 characters"
echo "- Search Top K:           8"

# Step 7: Create GCP credentials placeholder if needed
print_step "Checking GCP credentials"
if [[ ! -f "gcp-credentials.json" ]]; then
    print_warning "GCP credentials file not found"
    echo "To enable Google Cloud Storage integration:"
    echo "1. Download your service account key from Google Cloud Console"
    echo "2. Save it as 'gcp-credentials.json' in the backend directory"
    echo "3. Make sure the service account has access to the bucket: legalai_documents"
else
    print_status "✅ GCP credentials file found"
fi

# Step 8: Final instructions
print_step "Next Steps"
echo "==========="
echo "1. ✅ Stage 1 setup complete!"
echo "2. 🔄 Background services are running"
echo "3. 📝 Check the logs: docker-compose -f docker-compose.dev.yml logs"
echo "4. 🛑 Stop services: docker-compose -f docker-compose.dev.yml down"
echo ""
echo "Ready for Stage 2: Data Models & Database Setup"

print_status "🎉 RAG Stack Stage 1 setup completed successfully!"
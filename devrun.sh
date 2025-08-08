#!/bin/bash

# Elenchus AI Development Runner
# Starts backend and frontend in development mode with hot reload and debugging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=3000
BACKEND_PORT=8000
BACKEND_DEBUG_PORT=5678
export NEXT_PUBLIC_API_URL="http://localhost:${BACKEND_PORT}"

# Logs directory
LOGS_DIR="./logs"
mkdir -p $LOGS_DIR

echo -e "${PURPLE}🚀 Elenchus AI Development Runner${NC}"
echo -e "${PURPLE}===================================${NC}"
echo ""
echo -e "${CYAN}Configuration:${NC}"
echo -e "  Frontend: http://localhost:${FRONTEND_PORT}"
echo -e "  Backend:  http://localhost:${BACKEND_PORT}"
echo -e "  Debug:    localhost:${BACKEND_DEBUG_PORT}"
echo -e "  Logs:     ${LOGS_DIR}/"
echo ""

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Force kill if needed
    pgrep -f "npm run dev" | xargs -r kill -9 2>/dev/null || true
    pgrep -f "uvicorn" | xargs -r kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM EXIT

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is already in use${NC}"
        echo -e "${YELLOW}Please stop any existing services on port $port${NC}"
        exit 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $name to start...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        
        echo -ne "${YELLOW}   Attempt $attempt/$max_attempts...${NC}\r"
        sleep 2
        ((attempt++))
    done
    
    echo -e "\n${RED}❌ $name failed to start after $max_attempts attempts${NC}"
    return 1
}

# Check prerequisites
echo -e "${CYAN}🔍 Checking prerequisites...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed${NC}"
    exit 1
fi

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${RED}❌ Backend virtual environment not found${NC}"
    echo -e "${YELLOW}Please run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements/minimal.txt${NC}"
    exit 1
fi

# Check if backend dependencies are up to date
echo -e "${CYAN}🔍 Checking backend dependencies...${NC}"
cd backend
source venv/bin/activate
if ! python -c "from app.main import app; print('✅ Backend dependencies OK')" > /dev/null 2>&1; then
    echo -e "${YELLOW}📦 Updating backend dependencies...${NC}"
    echo -e "${CYAN}  Using minimal requirements to avoid dependency conflicts${NC}"
    pip install -r requirements/minimal.txt
    if ! python -c "from app.main import app; print('✅ Backend dependencies OK')" > /dev/null 2>&1; then
        echo -e "${RED}❌ Backend dependency installation failed${NC}"
        echo -e "${YELLOW}  Try: cd backend && pip install -r requirements/minimal.txt${NC}"
        exit 1
    fi
fi
cd ..

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi

# Check ports
echo -e "${CYAN}🔌 Checking ports...${NC}"
check_port $FRONTEND_PORT
check_port $BACKEND_PORT
check_port $BACKEND_DEBUG_PORT

# Start Docker services (MongoDB and RAG Stack)
echo -e "${CYAN}🐳 Starting development infrastructure...${NC}"
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for infrastructure services...${NC}"
sleep 10

# Check if RAG services are healthy
echo -e "${CYAN}🔍 Checking RAG services...${NC}"
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Qdrant is ready${NC}"
else
    echo -e "${YELLOW}⚠️  Qdrant may still be starting...${NC}"
fi

if docker exec elenchus-redis-rag-dev redis-cli -a rag_queue_password ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis RAG is ready${NC}"
else
    echo -e "${YELLOW}⚠️  Redis RAG may still be starting...${NC}"
fi

# Start Backend with debugging
echo -e "${CYAN}🔧 Starting backend with debugging...${NC}"
cd backend

# Activate virtual environment and start backend with debugger
source venv/bin/activate

# Start backend with debugpy for debugging (non-blocking)
python -m debugpy --listen 0.0.0.0:$BACKEND_DEBUG_PORT -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $BACKEND_PORT \
    --reload \
    --reload-dir app \
    --log-level info \
    > "../${LOGS_DIR}/backend.log" 2>&1 &

BACKEND_PID=$!
cd ..

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "${BLUE}🐛 Debugger available on port $BACKEND_DEBUG_PORT${NC}"

# Start Frontend
echo -e "${CYAN}⚛️  Starting frontend...${NC}"
npm run dev > "${LOGS_DIR}/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for services to be ready
wait_for_service "http://localhost:$BACKEND_PORT/health" "Backend"
wait_for_service "http://localhost:$FRONTEND_PORT" "Frontend"

# Display information
echo ""
echo -e "${GREEN}🎉 All services are running!${NC}"
echo -e "${PURPLE}================================${NC}"
echo ""
echo -e "${CYAN}📱 Application URLs:${NC}"
echo -e "  🌐 Frontend:  ${BLUE}http://localhost:${FRONTEND_PORT}${NC}"
echo -e "  🔧 Backend:   ${BLUE}http://localhost:${BACKEND_PORT}${NC}"
echo -e "  📚 API Docs:  ${BLUE}http://localhost:${BACKEND_PORT}/docs${NC}"
echo ""
echo -e "${CYAN}🗃️  RAG Infrastructure:${NC}"
echo -e "  🔍 Qdrant DB:    ${BLUE}http://localhost:6333${NC}"
echo -e "  🔄 Redis RAG:    ${BLUE}localhost:6380${NC}"
echo -e "  📊 RQ Dashboard: ${BLUE}http://localhost:9181${NC}"
echo ""
echo -e "${CYAN}🐛 Debugging:${NC}"
echo -e "  🔍 Debug Port: ${BLUE}localhost:${BACKEND_DEBUG_PORT}${NC}"
echo -e "  📝 VS Code: Add debug config (see .vscode/launch.json)"
echo ""
echo -e "${CYAN}📊 Logs:${NC}"
echo -e "  📜 Backend:  ${YELLOW}tail -f ${LOGS_DIR}/backend.log${NC}"
echo -e "  📜 Frontend: ${YELLOW}tail -f ${LOGS_DIR}/frontend.log${NC}"
echo ""
echo -e "${CYAN}🛠️  Development Tips:${NC}"
echo -e "  • Backend auto-reloads on file changes"
echo -e "  • Frontend has hot module replacement"
echo -e "  • Attach debugger to port ${BACKEND_DEBUG_PORT}"
echo -e "  • Use ${BLUE}Ctrl+C${NC} to stop all services"
echo ""

# Show real-time logs
echo -e "${YELLOW}📝 Real-time logs (Ctrl+C to stop):${NC}"
echo -e "${PURPLE}=====================================\n${NC}"

# Display logs from both services
tail -f "${LOGS_DIR}/frontend.log" "${LOGS_DIR}/backend.log" 2>/dev/null &

# Wait for user interrupt
while true; do
    sleep 1
done
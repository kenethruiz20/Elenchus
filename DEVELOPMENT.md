# Development Setup Guide

This guide explains how to set up and run the Elenchus AI application in development mode with hot reload and debugging capabilities.

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18 or higher)
- **Python 3.8+**
- **Docker & Docker Compose**
- **Git**

### One-Command Setup
```bash
# Run the development environment
./devrun.sh
```

Or use the Node.js version:
```bash
node devrun.js
```

## 📁 Project Structure

```
Elenchus/
├── devrun.sh              # Shell development runner
├── devrun.js              # Node.js development runner
├── tests/                 # All test scripts
│   ├── test-auth-flow.sh
│   ├── test-auth-routing.sh
│   ├── test-docker-build.sh
│   ├── test-final-auth-fix.sh
│   └── quick-build-test.sh
├── backend/               # Python FastAPI backend
├── frontend/              # Next.js frontend (root)
├── .vscode/               # VS Code configuration
└── logs/                  # Development logs
```

## 🔧 Development Scripts

### Shell Script (devrun.sh)
- **Best for**: Unix/Linux/macOS environments
- **Features**: Process management, colored output, signal handling
- **Usage**: `./devrun.sh`

### Node.js Script (devrun.js)
- **Best for**: Cross-platform, Node.js developers
- **Features**: Modern JavaScript, async/await, platform independent
- **Usage**: `node devrun.js`

## 🐛 Debugging Configuration

### VS Code Setup
The project includes pre-configured VS Code debugging:

1. **Backend Debugging** (`🐛 Debug Backend`):
   - Attaches to debugpy on port 5678
   - Set breakpoints in Python code
   - Step through FastAPI endpoints

2. **Frontend Debugging** (`🚀 Debug Frontend`):
   - Attaches to Node.js debugger
   - Debug React components and Next.js code

3. **Combined Debugging** (`🔧 Debug Both`):
   - Starts both debuggers simultaneously

### Manual Debugging Setup

#### Backend (Python)
```bash
# Install debugpy in backend venv
cd backend
source venv/bin/activate
pip install debugpy

# Start with debugger
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn app.main:app --reload
```

#### Frontend (Next.js)
```bash
# Start with debugging
NODE_OPTIONS='--inspect' npm run dev
```

## 🔌 Service Ports

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Frontend | 3000 | http://localhost:3000 | Next.js development server |
| Backend | 8000 | http://localhost:8000 | FastAPI application |
| Backend Debug | 5678 | localhost:5678 | Python debugger |
| MongoDB | 27018 | localhost:27018 | Database |
| Redis | 6380 | localhost:6380 | Cache |

## 📊 Development Logs

Both development runners create log files in the `logs/` directory:

```bash
# Watch backend logs
tail -f logs/backend.log

# Watch frontend logs
tail -f logs/frontend.log

# Watch both simultaneously
tail -f logs/frontend.log logs/backend.log
```

## 🛠️ Manual Setup

If you prefer to set up services manually:

### 1. Install Dependencies

```bash
# Frontend
npm install

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
```

### 2. Start Services

```bash
# Start Docker services
docker-compose up mongodb redis -d

# Start backend (in backend/ directory)
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in root directory)
npm run dev
```

## 🧪 Testing

All test scripts are now organized in the `tests/` folder:

```bash
# Run authentication tests
cd tests
./test-auth-flow.sh

# Test routing
./test-auth-routing.sh

# Quick build test
./quick-build-test.sh
```

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Backend Virtual Environment Issues
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
```

### Docker Services Won't Start
```bash
# Reset Docker services
docker-compose down
docker-compose up mongodb redis -d

# Check service status
docker-compose ps
```

### Frontend Build Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json .next
npm install
```

## 🎯 Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload
2. **API Documentation**: Visit http://localhost:8000/docs for interactive API docs
3. **Database Admin**: Use MongoDB Compass to connect to localhost:27018
4. **Environment Variables**: Copy `.env.example` to `.env` for local config
5. **Code Formatting**: Use the pre-configured VS Code settings for consistent formatting

## 🔄 Stopping Services

Both development runners handle cleanup automatically when you press `Ctrl+C`. They will:

1. Stop all spawned processes
2. Clean up background services
3. Perform graceful shutdown

## 📝 Environment Variables

### Backend Configuration
Create a `.env` file in the backend directory:

```env
# Backend Configuration
MONGODB_URL=mongodb://localhost:27018/elenchus
SECRET_KEY=your-super-secret-development-key
DEBUG=true
GOOGLE_API_KEY=your-google-api-key

# Development Settings
LOG_LEVEL=info
RELOAD=true
```

### Frontend Configuration
Create a `.env.local` file in the root directory or copy from `.env.example`:

```env
# Frontend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Port Configuration Options:**
- `http://localhost:8000` - Default for devrun.sh/devrun.js
- `http://localhost:8001` - If backend runs on port 8001
- Use production URL for deployed environments

**Alternative ways to set the API URL:**
```bash
# Using npm script for port 8001
npm run dev:8001

# Setting environment variable directly
NEXT_PUBLIC_API_URL=http://localhost:8001 npm run dev

# Using the development runners (automatic)
./devrun.sh  # Sets API URL to match backend port
```

## 🤝 Contributing

1. Make sure all services start correctly with the development runners
2. Test your changes with the provided test scripts
3. Use the debugging configuration to troubleshoot issues
4. Keep logs directory in .gitignore
5. Update this documentation if you add new development tools

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [VS Code Debugging Guide](https://code.visualstudio.com/docs/editor/debugging)
- [Docker Compose Reference](https://docs.docker.com/compose/)
#!/bin/bash

# Docker setup script for Elenchus backend
# This script helps set up the Docker environment for the Elenchus Legal AI backend

set -e

echo "🐳 Setting up Elenchus Docker Environment"
echo "========================================="

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env from template..."
    cp backend/.env.minimal backend/.env
    echo "✅ Created backend/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit backend/.env and add your Google Gemini API key:"
    echo "   GOOGLE_API_KEY=your_actual_api_key_here"
    echo ""
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter after you've updated the GOOGLE_API_KEY in backend/.env..."
fi

# Check if Google API key is set
if grep -q "your_google_gemini_api_key_here\|your-google-api-key-here" backend/.env; then
    echo "❌ Please set your actual Google Gemini API key in backend/.env"
    echo "   Current key appears to be a placeholder"
    exit 1
fi

echo "🔧 Building Docker containers (this may take a few minutes)..."
echo "💡 Using optimized build with minimal dependencies for faster builds"
docker-compose build --parallel

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to become healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔍 Testing backend health..."
timeout 30s bash -c 'until curl -f http://localhost:8001/health 2>/dev/null; do sleep 2; done' && echo "✅ Backend is healthy" || echo "❌ Backend health check failed"

echo ""
echo "🌟 Setup Complete!"
echo "==================="
echo ""
echo "🌐 Access your services:"
echo "   • Frontend:      http://localhost:3001"
echo "   • Backend API:   http://localhost:8001"
echo "   • API Docs:      http://localhost:8001/docs"
echo "   • MongoDB:       localhost:27018"
echo ""
echo "📋 Useful commands:"
echo "   • View logs:     docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Rebuild:       docker-compose build --no-cache"
echo ""
echo "🔧 If you encounter issues:"
echo "   1. Check that your GOOGLE_API_KEY is set correctly in backend/.env"
echo "   2. Ensure ports 3001, 8001, 27018 are not in use"
echo "   3. Run: docker-compose logs backend"
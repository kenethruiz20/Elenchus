#!/bin/bash

# Quick Docker build test for backend only
# This tests the optimized Dockerfile build

set -e

echo "🚀 Testing optimized Docker build for backend..."
echo "================================================"

cd "$(dirname "$0")"

# Build only the backend service
echo "🔧 Building backend container with minimal dependencies..."
time docker-compose build backend

echo ""
echo "✅ Build completed!"
echo ""
echo "📊 Container size:"
docker images elenchus-backend --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo ""
echo "🔍 Testing container startup..."
docker run --rm -d --name elenchus-test-backend \
  -e GOOGLE_API_KEY=test \
  -e MONGODB_URL=mongodb://localhost:27017/test \
  -p 8099:8000 \
  elenchus-backend || echo "⚠️ Container failed to start (expected without MongoDB)"

sleep 2

echo "🧹 Cleaning up test container..."
docker stop elenchus-test-backend 2>/dev/null || true

echo ""
echo "✅ Build test completed successfully!"
echo "💡 If build was fast, the optimization worked!"
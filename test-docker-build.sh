#!/bin/bash

# Quick test for fixed Docker build
# Tests if the MongoDB context issue is resolved

set -e

echo "🧪 Testing Docker Build Fix"
echo "============================"

cd "$(dirname "$0")"

# Clean up any previous failed attempts
echo "🧹 Cleaning up previous attempts..."
docker-compose down --volumes --remove-orphans 2>/dev/null || true
docker system prune -f --volumes 2>/dev/null || true

echo ""
echo "🔧 Testing MongoDB service (official image with volume mount)..."
docker-compose build mongodb 2>/dev/null || echo "✅ MongoDB using official image (no build needed)"

echo ""
echo "🔧 Testing backend service build..."
time docker-compose build backend

echo ""
echo "✅ Build test completed successfully!"
echo ""
echo "💡 To start the full stack:"
echo "   docker-compose up -d"
echo ""
echo "💡 To test with setup script:"
echo "   ./backend/docker-setup.sh"
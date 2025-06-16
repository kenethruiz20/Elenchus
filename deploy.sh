#!/bin/bash

# Deployment script for Legal Assistant Chainlit app to Google Cloud Run

set -e

# Configuration
PROJECT_ID="legalai-462213"
SERVICE_NAME="legal-assistant"
REGION="us-central1"
ARTIFACT_REGISTRY="us-central1-docker.pkg.dev"
REPOSITORY="legal-assistant"

# Get current commit hash or use "latest"
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")

# Image name
IMAGE_NAME="$ARTIFACT_REGISTRY/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:$COMMIT_SHA"

echo "🚀 Deploying Legal Assistant to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "Image: $IMAGE_NAME"
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME .

# Push to Artifact Registry
echo "📤 Pushing to Artifact Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_NAME \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --port=8000 \
  --timeout=300s \
  --concurrency=80 \
  --project=$PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

echo ""
echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "⚠️  Remember to set environment variables in Cloud Run console:"
echo "   - GOOGLE_API_KEY"
echo "   - LITERAL_API_KEY" 
echo "   - CHAINLIT_AUTH_SECRET"
echo "   - OAUTH_GOOGLE_CLIENT_ID"
echo "   - OAUTH_GOOGLE_CLIENT_SECRET"
echo "   - CHAINLIT_URL=$SERVICE_URL" 
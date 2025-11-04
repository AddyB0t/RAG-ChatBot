#!/bin/bash

# Docker Startup Script for Resume Parser Application
# This script bypasses .env file permission issues by running docker-compose
# with hardcoded configuration

set -e

echo "=========================================="
echo "Resume Parser Docker Startup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    exit 1
fi

# Navigate to the script directory
cd "$(dirname "$0")"

echo "📁 Working directory: $(pwd)"
echo ""

# Create required directories if they don't exist
echo "📂 Creating required directories..."
mkdir -p uploads logs
echo "✅ Directories created"
echo ""

# Pull latest images
echo "🐳 Pulling Docker images..."
docker-compose pull postgres || true
echo ""

# Build the application image
echo "🔨 Building application image..."
docker-compose build --no-cache app
echo "✅ Build complete"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d
echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""

# Display logs
echo "📋 Recent logs:"
docker-compose logs --tail=20 app
echo ""

# Check health endpoint
echo "🏥 Testing health endpoint..."
sleep 5
if curl -f http://localhost:8000/api/v1/health 2>/dev/null; then
    echo "✅ Application is healthy!"
else
    echo "⚠️  Health check failed - application may still be starting"
    echo "   ML models need to download on first run (~5-10 minutes)"
    echo ""
    echo "   Monitor logs with: docker-compose logs -f app"
fi

echo ""
echo "=========================================="
echo "🎉 Docker Deployment Complete!"
echo "=========================================="
echo ""
echo "📚 Access Points:"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - ReDoc:        http://localhost:8000/redoc"
echo "   - Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "🔧 Useful Commands:"
echo "   - View logs:        docker-compose logs -f app"
echo "   - Stop services:    docker-compose down"
echo "   - Restart:          docker-compose restart app"
echo "   - Check status:     docker-compose ps"
echo ""
echo "⚠️  Note: First startup takes 5-10 minutes to download ML models"
echo ""

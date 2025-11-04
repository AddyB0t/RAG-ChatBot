#!/bin/bash

# Docker Logs Viewer
# Watch application startup and ML model downloads

echo "=========================================="
echo "Resume Parser - Docker Logs"
echo "=========================================="
echo ""
echo "Watching application logs..."
echo "Press Ctrl+C to exit"
echo ""
echo "Note: First startup takes 5-10 minutes to download ML models:"
echo "  - Flair NER model (~500MB)"
echo "  - Sentence transformer embeddings (~100MB)"
echo ""
echo "=========================================="
echo ""

# Follow logs for the app container
docker compose logs -f --tail=50 app

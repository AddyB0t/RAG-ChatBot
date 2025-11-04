#!/bin/bash
set -e

echo "=========================================="
echo "Resume Parser & Job Matcher - Starting..."
echo "=========================================="

echo "Waiting for PostgreSQL to be ready..."
python3 -c "
import sys
import time
import psycopg2
from psycopg2 import OperationalError

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host='$DB_HOST',
            port=$DB_PORT,
            user='$DB_USER',
            password='$DB_PASSWORD',
            database='$DB_NAME'
        )
        conn.close()
        print('PostgreSQL is up and running!')
        sys.exit(0)
    except OperationalError:
        retry_count += 1
        print(f'PostgreSQL is unavailable - attempt {retry_count}/{max_retries}')
        time.sleep(2)

print('ERROR: PostgreSQL did not become available in time')
sys.exit(1)
"

echo "Checking ML models..."
if [ ! -d "/app/models/flair_cache" ] || [ -z "$(ls -A /app/models/flair_cache)" ]; then
  echo "⚠️  ML models directory is empty."
  echo "📥 Models will be downloaded automatically on first use:"
  echo "   - Flair NER model (~500MB) - First resume parse"
  echo "   - This may take 5-10 minutes on first startup"
  echo "   - Subsequent starts will be much faster (models cached)"
else
  echo "✅ ML models cache found - startup will be fast"
  echo "📊 Cache size: $(du -sh /app/models/flair_cache | cut -f1)"
fi

echo "Creating necessary directories..."
mkdir -p /app/uploads /app/logs /app/models/flair_cache

echo "Application is ready to start!"
echo "=========================================="
echo "API Documentation: http://localhost:8000/docs"
echo "=========================================="

exec "$@"

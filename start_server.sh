#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

# Activate conda environment
source /mnt/data/miniconda3/bin/activate Hackathon

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

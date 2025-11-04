#!/bin/bash
source /mnt/data/miniconda3/bin/activate Hackathon
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

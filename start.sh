#!/bin/bash

# Start FastAPI backend
cd /app
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# Start Next.js frontend
cd /app/frontend
npm start &

# Start Nginx
nginx -g 'daemon off;'

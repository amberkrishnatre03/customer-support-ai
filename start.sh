#!/bin/bash

# 1. Start FastAPI backend internally
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# 2. Start Streamlit on the web port
PORT=${PORT:-8501}
streamlit run app/dashboard.py --server.port $PORT --server.address 0.0.0.0
#!/bin/sh
echo "[STARTUP] Starting metrics server on port 8000..."
python metrics_server.py &
echo "[STARTUP] Starting Streamlit on port 8501..."
streamlit run app.py --server.port=8501 --server.headless=true --server.address=0.0.0.0

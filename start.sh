#!/bin/bash
# Start Flask webhook API in background
python /app/webhook_api.py &

# Start Streamlit in foreground
streamlit run /app/main.py

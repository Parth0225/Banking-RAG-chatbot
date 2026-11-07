#!/usr/bin/env bash
set -e
echo "=== Setting up Banking & Finance RAG Chatbot ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
python scripts/extract_zip.py
echo "Next: 1) put ANTHROPIC_API_KEY in .env  2) python -m src.ingest  3) streamlit run app.py"

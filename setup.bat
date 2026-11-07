@echo off
echo === Setting up Banking & Finance RAG Chatbot ===
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
python scripts\extract_zip.py
echo.
echo Next: 1) put your ANTHROPIC_API_KEY in .env  2) python -m src.ingest  3) streamlit run app.py

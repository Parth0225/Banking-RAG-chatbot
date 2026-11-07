# RAG Chatbot for Banking and Finance

Retrieval-Augmented chatbot that answers Indian banking & finance questions from your PDF knowledge base,
with source citations. Stack: pypdf + ChromaDB + sentence-transformers (local embeddings) + Claude + Streamlit.

## Structure
```
app.py                 Streamlit chat UI
src/config.py          Settings (from .env)
src/ingest.py          PDFs -> chunks -> embeddings -> ChromaDB
src/rag.py             Retrieval + Claude answer generation
scripts/extract_zip.py Pulls PDFs from the zip in ~/Downloads into data/pdfs
data/pdfs/             Your PDFs
data/vectorstore/      Generated vector DB
```

## Setup (Windows)
1. Open a terminal in this folder and run `setup.bat`
   (creates venv, installs packages, creates `.env`, extracts PDFs from Downloads).
2. Edit `.env` and add your `ANTHROPIC_API_KEY`.
3. Build the index: `python -m src.ingest`
4. Launch: `streamlit run app.py`

Mac/Linux: use `./setup.sh` instead.

If the zip isn't found automatically: `python scripts/extract_zip.py "C:\path\to\file.zip"`
(or just paste the PDFs into `data/pdfs/`).

## Tuning
Change chunk size, overlap, top-k, model and embedding model in `.env`.

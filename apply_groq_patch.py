"""Run from the project folder:  python apply_groq_patch.py
Switches the chatbot from Anthropic to Groq (OpenAI-compatible API)."""
import subprocess, sys, getpass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if not (ROOT / "src").exists():
    sys.exit("Run this from the project folder (the one containing app.py and src/).")

CONFIG = '''import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PDF_DIR = ROOT / "data" / "pdfs"
VECTOR_DIR = ROOT / "data" / "vectorstore"
COLLECTION = "banking_finance"

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))
TOP_K = int(os.getenv("TOP_K", 5))
'''

RAG = '''"""Retrieval + generation."""
from openai import OpenAI
from . import config
from .ingest import get_collection

SYSTEM_PROMPT = """You are a helpful assistant for Indian banking and finance questions.
Answer ONLY using the provided context excerpts. If the context does not contain the
answer, say you could not find it in the knowledge base rather than guessing.
Cite sources inline like [source.pdf, p.X]. Be clear and concise.
You provide general information, not personalised financial, legal or tax advice."""


class RAGChatbot:
    def __init__(self):
        if not config.LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY missing. Add it to your .env file.")
        self.client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
        self.col = get_collection()

    def retrieve(self, query: str, k: int = config.TOP_K):
        res = self.col.query(query_texts=[query], n_results=k)
        return [
            {"text": d, "source": m["source"], "page": m["page"], "distance": dist}
            for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
        ]

    def ask(self, query: str, history: list | None = None):
        hits = self.retrieve(query)
        context = "\\n\\n".join(
            f"[{h['source']}, p.{h['page']}]\\n{h['text']}" for h in hits
        )
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += list(history or [])[-6:]
        messages.append({
            "role": "user",
            "content": f"Context:\\n{context}\\n\\nQuestion: {query}",
        })
        resp = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            max_tokens=1000,
            messages=messages,
        )
        return resp.choices[0].message.content, hits
'''

key = getpass.getpass("Paste your Groq API key (input hidden), then press Enter: ").strip()
if not key.startswith("gsk_"):
    print("Warning: Groq keys usually start with 'gsk_'. Continuing anyway.")

(ROOT / "src" / "config.py").write_text(CONFIG, encoding="utf-8")
(ROOT / "src" / "rag.py").write_text(RAG, encoding="utf-8")
(ROOT / ".env").write_text(
    f"LLM_API_KEY={key}\n"
    "LLM_BASE_URL=https://api.groq.com/openai/v1\n"
    "LLM_MODEL=openai/gpt-oss-120b\n"
    "EMBEDDING_MODEL=BAAI/bge-small-en-v1.5\n"
    "CHUNK_SIZE=1000\nCHUNK_OVERLAP=150\nTOP_K=5\n",
    encoding="utf-8",
)

req = ROOT / "requirements.txt"
lines = [l for l in req.read_text().splitlines() if not l.startswith("anthropic")]
if not any(l.startswith("openai") for l in lines):
    lines.append("openai>=1.40.0")
req.write_text("\n".join(lines) + "\n")

subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
print("\nDone. Next:\n  python -m src.ingest\n  streamlit run app.py")

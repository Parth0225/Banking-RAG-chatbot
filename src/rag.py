"""Retrieval + generation."""
from openai import OpenAI
from . import config
from .ingest import get_collection

SYSTEM_PROMPT = """You are a knowledgeable assistant for Indian banking and finance questions.
Use the provided context excerpts to answer the question directly, in your own words,
as if you simply know this information.

Rules:
- Give the answer straight away. Never say things like "according to the document",
  "described in the PDF", "the context says" or mention file names or page numbers.
- Do not add inline citations or brackets. Sources are shown separately in the app.
- Be clear and concise. Use short paragraphs or bullet points when helpful.
- If the context does not contain the answer, say: "I couldn't find that in my knowledge base."
  Do not guess or make things up.
- You give general information, not personalised financial, legal or tax advice."""


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
        context = "\n\n".join(
            f"[{h['source']}, p.{h['page']}]\n{h['text']}" for h in hits
        )
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += list(history or [])[-6:]
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}",
        })
        resp = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            max_tokens=1000,
            messages=messages,
        )
        return resp.choices[0].message.content, hits

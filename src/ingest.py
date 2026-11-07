"""Read PDFs -> chunk -> embed -> store in ChromaDB."""
import hashlib
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from . import config


def _client():
    return chromadb.PersistentClient(path=str(config.VECTOR_DIR))


def get_collection():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL
    )
    return _client().get_or_create_collection(
        name=config.COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def ingest(reset: bool = False, progress=print) -> int:
    pdfs = sorted(config.PDF_DIR.rglob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDFs found in {config.PDF_DIR}")

    if reset:
        try:
            _client().delete_collection(config.COLLECTION)
        except Exception:
            pass
    col = get_collection()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP
    )
    total = 0
    for i, pdf in enumerate(pdfs, 1):
        progress(f"[{i}/{len(pdfs)}] {pdf.name}")
        try:
            reader = PdfReader(str(pdf))
        except Exception as e:
            progress(f"  skipped ({e})")
            continue
        ids, docs, metas = [], [], []
        for page_no, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            for j, chunk in enumerate(splitter.split_text(text)):
                uid = hashlib.md5(f"{pdf.name}|{page_no}|{j}|{chunk[:50]}".encode()).hexdigest()
                ids.append(uid)
                docs.append(chunk)
                metas.append({"source": pdf.name, "page": page_no})
        for k in range(0, len(ids), 128):
            col.upsert(ids=ids[k:k+128], documents=docs[k:k+128], metadatas=metas[k:k+128])
        total += len(ids)
    progress(f"Done. {total} chunks indexed.")
    return total


if __name__ == "__main__":
    import sys
    ingest(reset="--reset" in sys.argv)

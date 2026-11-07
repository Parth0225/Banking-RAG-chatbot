"""Find the knowledge-base zip (or extracted folder) in ~/Downloads and copy all PDFs to data/pdfs."""
import shutil, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "pdfs"
PATTERN = "Indian_Banking_Finance_RAG_Knowledge*"
downloads = Path.home() / "Downloads"

DEST.mkdir(parents=True, exist_ok=True)
arg = Path(sys.argv[1]) if len(sys.argv) > 1 else None
sources = [arg] if arg else sorted(downloads.glob(PATTERN))
if not sources:
    sys.exit(f"Nothing matching {PATTERN} in {downloads}. Pass a path: python scripts/extract_zip.py <zip_or_folder>")

count = 0
for src in sources:
    if src.suffix.lower() == ".zip":
        tmp = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(src) as z:
            z.extractall(tmp)
        src = tmp
    if src.is_dir():
        for pdf in src.rglob("*.pdf"):
            shutil.copy2(pdf, DEST / pdf.name)
            count += 1
print(f"Copied {count} PDFs to {DEST}")

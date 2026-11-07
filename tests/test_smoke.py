from src import config

def test_pdf_dir_exists():
    assert config.PDF_DIR.exists()

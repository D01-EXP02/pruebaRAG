from pathlib import Path

from src.ingestion.pdf_chunker import fragmentar_documentos_pdf


def test_fragmentar_documentos_pdf_devuelve_fragmentos():
    fragmentos = fragmentar_documentos_pdf(Path("data/docs"), chunk_size=500, chunk_overlap=50)

    assert len(fragmentos) > 0
    assert all(getattr(fragmento, "page_content", None) for fragmento in fragmentos)
    assert all(fragmento.metadata.get("source") for fragmento in fragmentos)

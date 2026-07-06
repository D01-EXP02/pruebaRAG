from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def fragmentar_documentos_pdf(
    carpeta_docs: str | Path,
    chunk_size: int = 400,
    chunk_overlap: int = 150,
) -> List[Document]:
    carpeta = Path(carpeta_docs)
    if not carpeta.exists():
        raise FileNotFoundError(f"No existe la carpeta de documentos: {carpeta}")

    pdfs = sorted(carpeta.glob("*.pdf"))
    if not pdfs:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    documentos: List[Document] = []
    for pdf_path in pdfs:
        texto = leer_pdf(pdf_path)
        if not texto.strip():
            continue

        fragmentos = splitter.split_text(texto)
        for idx, fragmento in enumerate(fragmentos, start=1):
            documentos.append(
                Document(
                    page_content=fragmento.strip(),
                    metadata={
                        "source": str(pdf_path),
                        "file_name": pdf_path.name,
                        "chunk_index": idx,
                    },
                )
            )

    return documentos


def leer_pdf(pdf_path: str | Path) -> str:
    pdf_path = Path(pdf_path)
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - depende del entorno
        raise RuntimeError(
            "Falta la dependencia 'pypdf'. Instálala con 'pip install pypdf'."
        ) from exc

    reader = PdfReader(str(pdf_path))
    texto_paginas: list[str] = []
    for page in reader.pages:
        texto = page.extract_text() or ""
        texto_paginas.append(texto)

    return "\n\n".join(texto_paginas)

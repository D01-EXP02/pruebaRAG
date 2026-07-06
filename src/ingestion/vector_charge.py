"""Construcción y carga de la base vectorial (Chroma) para el sistema RAG."""
from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_VECTORSTORE_PATH = Path("data/vectorstore")


def obtener_o_crear_vectorstore(
    documentos: List[Document],
    persist_directory: str | Path | None = None,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> Chroma | None:
    """Carga el vectorstore si ya existe en disco; si no, lo construye desde los documentos."""
    carpeta = Path(persist_directory or DEFAULT_VECTORSTORE_PATH)
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    ya_existe = (carpeta / "chroma.sqlite3").exists()

    if ya_existe:
        print("[INFO] Cargando vectorstore existente desde disco (sin recalcular embeddings)...")
        return Chroma(
            persist_directory=str(carpeta),
            embedding_function=embeddings,
        )

    if not documentos:
        return None

    print("[INFO] No existe vectorstore previo. Generando embeddings por primera vez...")
    carpeta.mkdir(parents=True, exist_ok=True)
    vectorstore = Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=str(carpeta),
    )
    return vectorstore
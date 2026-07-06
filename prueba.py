from src.ingestion.vector_charge import obtener_o_crear_vectorstore
from src.ingestion.pdf_chunker import fragmentar_documentos_pdf
from pathlib import Path
from collections import Counter

documentos = fragmentar_documentos_pdf(Path("data/docs"), chunk_size=400, chunk_overlap=150)
vectorstore = obtener_o_crear_vectorstore(documentos, persist_directory="data/vectorstore")

# ¿Cuántos documentos hay realmente indexados en Chroma, y de qué archivos?
coleccion = vectorstore.get()
fuentes = [meta.get("file_name") for meta in coleccion["metadatas"]]
print("Chunks indexados en el vectorstore:", Counter(fuentes))
from pathlib import Path
from src.ingestion.pdf_chunker import fragmentar_documentos_pdf
from src.retribucion_rag.rag import construir_respuesta_rag


def test_construir_respuesta_rag():
    documentos = fragmentar_documentos_pdf(Path("data/docs"), chunk_size=600, chunk_overlap=80)
    respuesta = construir_respuesta_rag(
        consulta="¿El plan cubre una cirugía de cataratas para un afiliado activo y al día?",
        afiliado_id="A-00001",
        documentos=documentos,
    )

    assert respuesta["estado"] in {"cubierto", "no_cubierto", "cubierto_con_condiciones"}
    assert respuesta["respuesta"]
    assert respuesta["razonamiento"]
    assert respuesta["fuentes"]

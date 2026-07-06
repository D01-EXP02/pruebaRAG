from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_ollama import ChatOllama  
from src.afiliados.repositorio import AfiliadosRepository
from src.ingestion.vector_charge import obtener_o_crear_vectorstore 


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_LLM_MODEL = "llama3.2:3b"           


def construir_respuesta_rag(
    consulta: str,
    afiliado_id: str,
    documentos: List[Document],
    ruta_excel: str | Path | None = None,
    persist_directory: str | Path | None = None,
    vectorstore: Chroma | None = None,   

) -> Dict[str, Any]:
    ruta_excel = ruta_excel or Path("data/afiliados/BD_afiliados.xlsx")
    repo = AfiliadosRepository(ruta_excel)
    afiliado = repo.buscar_por_id(afiliado_id)

    if afiliado is None:
        return {
            "estado": "no_cubierto",
            "respuesta": "No se encontró el afiliado solicitado.",
            "razonamiento": ["No existe un afiliado con ese identificador."],
            "fuentes": [],
        }

    documentos_relevantes = recuperar_documentos(
        consulta,
        documentos,
        vectorstore=vectorstore,          
        persist_directory=persist_directory,
    )


    razonamiento = [
        f"Se revisó la consulta del afiliado {afiliado.id_afiliado}.",
        f"Estado del afiliado: {afiliado.estado_afiliacion} y pagos: {afiliado.estado_pagos}.",
    ]

    intencion = detectar_intencion_consulta(consulta)
    if afiliado.estado_afiliacion == "Suspendido" or afiliado.estado_afiliacion == "Retirado":
            respuesta = f"La solicitud no procede: el afiliado tiene estado '{afiliado.estado_afiliacion}'."
            estado = "no_cubierto"
    else:
            respuesta = generar_respuesta_llm(
            consulta=consulta,
            afiliado=afiliado,
            documentos=documentos_relevantes,
        )
    if afiliado.esta_activo and afiliado.esta_al_dia:
            estado = "cubierto_con_condiciones"
    else:
            estado = "no_cubierto"

    razonamiento.append(
        f"Intención detectada: {intencion}."
    )
    if not documentos_relevantes:
        razonamiento.append("No se encontraron fragmentos suficientemente relevantes en la documentación.")

    fuentes = [doc.metadata.get("source", "desconocido") for doc in documentos_relevantes[:3]]

    return {
        "estado": estado,
        "respuesta": respuesta,
        "razonamiento": razonamiento,
        "fuentes": fuentes,
    }


def detectar_intencion_consulta(consulta: str) -> str:
    texto = consulta.lower()
    if any(palabra in texto for palabra in ["nombre del plan", "plan actual", "nombre de mi plan", "plan"]):
        return "informacion_plan"
    if any(palabra in texto for palabra in ["autorizacion", "autorización", "autorizada", "autorizado"]):
        return "informacion_autorizacion"
    if any(palabra in texto for palabra in ["proceso", "procedimiento", "servicio", "cirugía", "resonancia", "cataratas"]):
        return "informacion_procedimiento"
    if any(palabra in texto for palabra in ["cobertura", "cubierto", "no cubierto", "procede"]):
        return "cobertura"
    return "general"

"""
def construir_respuesta_por_intencion(
    consulta: str,
    afiliado: Any,
    documentos: List[Document],
    intencion: str,
) -> tuple[str, str]:
    if intencion == "informacion_plan":
        return (
            f"El afiliado {afiliado.id_afiliado} está asociado al plan {afiliado.plan}."
            f" El estado del afiliado es {afiliado.estado_afiliacion} y sus pagos están {afiliado.estado_pagos}.",
            "informacion",
        )

    if intencion == "informacion_autorizacion":
        autorizacion = "Sí" if afiliado.tiene_autorizacion_previa == "Sí" else "No"
        return (
            f"La afiliación reporta autorización previa: {autorizacion}. "
            f"Servicio autorizado: {afiliado.servicio_autorizado}.",
            "informacion",
        )

    if intencion == "informacion_procedimiento":
        return (
            f"Se puede informar que el afiliado pertenece al plan {afiliado.plan} y su estado actual es {afiliado.estado_afiliacion}. "
            "La respuesta debe basarse en los documentos recuperados y en las condiciones del plan.",
            "informacion",
        )

    if afiliado.esta_activo and afiliado.esta_al_dia:
        return (
            "La solicitud puede ser considerada cubierta, siempre que se cumplan "
            "las condiciones descritas en la documentación y la autorización vigente.",
            "cubierto_con_condiciones",
        )

    return (
        "La solicitud no procede con base en el estado actual del afiliado.",
        "no_cubierto",
    )
"""


def generar_respuesta_llm(
    consulta: str,
    afiliado: Any,
    documentos: List[Document],
    modelo: str = DEFAULT_LLM_MODEL,
) -> str:
    contexto = "\n\n".join(d.page_content for d in documentos) if documentos else "Sin contexto disponible."

    prompt = f"""Eres un asistente que evalúa cobertura de un plan de salud.

Datos del afiliado:
- Plan: {afiliado.plan}
- Estado: {afiliado.estado_afiliacion}
- Pagos: {afiliado.estado_pagos}
- Autorización previa: {afiliado.tiene_autorizacion_previa}

Contexto de los documentos del plan:
{contexto}

Pregunta del afiliado: {consulta}

Responde basándote únicamente en la información anterior. Indica si está cubierto,
no cubierto, o cubierto con condiciones, y justifica citando el documento correspondiente."""

    llm = ChatOllama(model=modelo)
    return llm.invoke(prompt).content


def recuperar_documentos(
    consulta: str,
    documentos: List[Document],
    vectorstore: Chroma | None = None,
    persist_directory: str | Path | None = None,
    top_k: int = 8,
) -> List[Document]:

    try:
        if vectorstore is None:
            vectorstore = obtener_o_crear_vectorstore(documentos, persist_directory=persist_directory)
        if vectorstore is None:
            raise RuntimeError("No se pudo crear el vectorstore")
        resultados = vectorstore.similarity_search(consulta, k=top_k)
    except Exception as e:
        print(f"[WARN] Falló la búsqueda semántica: {type(e).__name__}: {e}")

    return recuperar_documentos_por_palabras_clave(consulta, documentos, top_k=top_k)


def construir_vectorstore(
    documentos: List[Document],
    persist_directory: str | Path | None = None,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> Chroma | None:
    if not documentos:
        return None

    carpeta = Path(persist_directory or "data/chroma_db")
    carpeta.mkdir(parents=True, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vectorstore = Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=str(carpeta),
    )
    return vectorstore


def recuperar_documentos_por_palabras_clave(
    consulta: str,
    documentos: List[Document],
    top_k: int = 5,
) -> List[Document]:
    consulta_lower = consulta.lower()
    relevantes: List[Document] = []
    for documento in documentos:
        contenido = documento.page_content.lower()
        if any(
            palabra in contenido
            for palabra in ["cobertura", "cubierto", "autoriz", "cirugía", "cataratas", "plan"]
        ):
            if consulta_lower in contenido or any(
                palabra in consulta_lower
                for palabra in ["cobertura", "cubierto", "cirugía", "cataratas", "autoriz"]
            ):
                relevantes.append(documento)
                continue
        if consulta_lower in contenido:
            relevantes.append(documento)
    return relevantes[:top_k]

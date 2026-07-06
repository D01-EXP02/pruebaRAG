from __future__ import annotations
import re
from pathlib import Path
from src.ingestion.vector_charge import obtener_o_crear_vectorstore 
from src.afiliados.repositorio import AfiliadosRepository
from src.ingestion.pdf_chunker import fragmentar_documentos_pdf
from src.retribucion_rag.rag import construir_respuesta_rag


def extraer_id_afiliado(consulta: str) -> str | None:
    coincidencias = re.findall(r"\bA-\d{5}\b", consulta.upper())
    return coincidencias[0] if coincidencias else None


def ejecutar_interfaz_cli() -> None:
    print("\n\n /////////////////* Asistente de cobertura de planes de salud *////////////////\n")
    print("Escribe 'salir' para terminar.\n")

    repo = AfiliadosRepository(Path("data/afiliados/BD_afiliados.xlsx"))

    print("[INFO] Preparando documentos y base vectorial...")
    documentos = fragmentar_documentos_pdf(Path("data/docs"), chunk_size=400, chunk_overlap=150)
    vectorstore = obtener_o_crear_vectorstore(documentos, persist_directory="data/vectorstore") 
    print("[INFO] Listo.\n")

    while True:
        consulta = input("Tu consulta: ").strip()
        if consulta.lower() in {"", "salir"}:
            print("Saliendo...")
            break

        afiliado_id = extraer_id_afiliado(consulta)
        if not afiliado_id:
            afiliado_id = input("No pude detectar un ID de afiliado en la consulta. Ingrésalo manualmente: ").strip()
            if afiliado_id.lower() in {"", "salir"}:
                print("Saliendo...")
                break

        afiliado = repo.buscar_por_id(afiliado_id)
        if afiliado is None:
            print("No se encontró un afiliado con ese ID. Intenta nuevamente.\n")
            continue

        documentos = fragmentar_documentos_pdf(Path("data/docs"), chunk_size=600, chunk_overlap=80)
        respuesta = construir_respuesta_rag(
            consulta=consulta,
            afiliado_id=afiliado_id,
            documentos=documentos,
            vectorstore=vectorstore,   

        )

        print(f"\nAfiliado encontrado: {afiliado.primer_nombre} {afiliado.primer_apellido}")
        print("\nRespuesta:")
        print(respuesta["respuesta"])
        print("\nRazonamiento:")
        for paso in respuesta["razonamiento"]:
            print(f"- {paso}")
        print("\nFuentes:")
        for fuente in respuesta["fuentes"]:
            print(f"- {fuente}")
        print("\n" + "-" * 60)


if __name__ == "__main__":
    ejecutar_interfaz_cli()



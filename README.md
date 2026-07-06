# Proyecto Plan de Salud con RAG

Este proyecto implementa un asistente inteligente para responder consultas formales sobre cobertura de un plan de salud, combinando:

- información contenida en documentos PDF de la carpeta `data/docs`
- el registro del afiliado almacenado en `data/afiliados/BD_afiliados.xlsx`
- un flujo de recuperación y razonamiento basado en RAG

La solución está diseñada para recibir una consulta del usuario, identificar el afiliado implicado, recuperar contexto relevante de los documentos y construir una respuesta formal, trazable y fundamentada.

## Qué incluye

- Lectura y fragmentación de PDFs desde `data/docs`
- Indexación semántica con Chroma y embeddings de HuggingFace
- Validación del afiliado a partir del ID en la base de datos Excel
- Interfaz por consola para interactuar con el sistema
- Pruebas básicas para validar el pipeline RAG

## Estructura del proyecto

```text
src/
  afiliados/        # modelos y acceso al Excel de afiliados
  agent/            # interfaz CLI para interacción con el usuario
  ingestion/        # lectura y fragmentación de PDFs
  retribucion_rag/  # pipeline RAG y recuperación semántica
  reasoning/        # espacio para lógica adicional de razonamiento
  api/              # preparación para una futura API

data/
  afiliados/        # archivo Excel con afiliados
  docs/             # documentos PDF de referencia
  chroma_db/        # base de datos vectorial Chroma
```

## Requisitos

- Python 3.10 o superior
- Entorno virtual recomendado
- Dependencias listadas en `requirements.txt`

## Entorno de desarrollo

1. Crear y activar un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar la aplicación

### Opción 1: interfaz por consola

Desde la raíz del proyecto:

```bash
python run_cli.py
```

La aplicación te pedirá:
- el ID del afiliado (o lo detectará si aparece en la consulta)
- la consulta formal que deseas evaluar

### Opción 2: probar el pipeline directamente

```bash
python -c "from pathlib import Path; from src.ingestion.pdf_chunker import fragmentar_documentos_pdf; from src.retribucion_rag.rag import construir_respuesta_rag; docs = fragmentar_documentos_pdf(Path('data/docs'), chunk_size=600, chunk_overlap=80); print(construir_respuesta_rag('consulta de ejemplo', 'A-00015', docs))"
```

## Probar los tests

```bash
pytest -q
```

## Notas

- El flujo actual usa documentos PDF y un archivo Excel como base de conocimiento.
- La recuperación semántica se apoya en Chroma y embeddings para encontrar contexto relevante.
- La respuesta se construye con base en los documentos recuperados y en el perfil del afiliado, sin inventar información.

## Instalación

1. Ejecutar `./setup.sh` (instala Ollama, descarga Llama3.2:3b, instala dependencias de Python)
2. Copiar `.env.example` a `.env`
3. Levantar el servidor de Ollama: `ollama serve` (en una terminal aparte, o como servicio)
4. Ejecutar la aplicación: `uvicorn src.api.main:app --reload`


## Configuración

Este proyecto usa Ollama local, por lo que no se requieren API keys externas.
Copia `.env.example` a `.env` y ajusta los valores si es necesario 
(por defecto ya deberían funcionar sin cambios).
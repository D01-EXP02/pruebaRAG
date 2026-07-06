from langchain_ollama import ChatOllama

def test_ollama_responde():
    llm = ChatOllama(model="llama3.2:3b")
    respuesta = llm.invoke("Responde solo con 'ok' si me escuchas")
    assert respuesta.content is not None
    assert len(respuesta.content) > 0
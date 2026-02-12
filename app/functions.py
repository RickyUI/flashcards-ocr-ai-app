from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import Chroma
import json
import base64
from dotenv import load_dotenv
import uuid
from langchain_openai import OpenAIEmbeddings
from datetime import datetime

load_dotenv()

def image_to_text(image_path: str) -> dict:
    """
    Analiza una imagen, detecta palabras resaltadas y las devuelve en formato JSON.
    """
    # Configuramos el LLM para que devuelva estrictamente un objeto JSON
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    # Leemos la imagen en binario
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Codificamos a base64
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Definimos las instrucciones detalladas
    system_message = SystemMessage(
        content=(
            "Eres un asistente experto en aprendizaje de francés. "
            "Tu tarea es analizar la imagen y extraer UNICAMENTE las palabras o frases resaltadas (marcadas con marcador). "
            "Para cada elemento encontrado, genera su traducción al español y un ejemplo de uso en francés. "
            "Responde exclusivamente en formato JSON con esta estructura: "
            "{\"flashcards\": [{\"palabra\": \"...\", \"traduccion\": \"...\", \"ejemplo_fr\": \"...\"}]}"
        )
    )

    # Adjuntamos la imagen en el mensaje del usuario
    human_message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_b64}"
                }
            },
            {
                "type": "text",
                "text": "Analiza esta imagen y extrae las palabras resaltadas siguiendo el formato JSON solicitado."
            }
        ]
    )

    # Invocamos al modelo
    response = llm.invoke([system_message, human_message])
    
    # Parseamos la respuesta
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"error": "El modelo no devolvió un JSON válido", "raw": response.content}

def save_flashcards_to_db(flashcards: dict):
    """
    Guarda flashcards en ChromaDB, evitando duplicados por ID.
    
    Args:
        flashcards: Dict con estructura {"flashcards": [{"palabra": ..., "traduccion": ..., "ejemplo_fr": ...}]}
    
    Returns:
        Dict con vectorstore, cantidad agregada y duplicados encontrados
    """
    
    # Conectar a DB (crea si no existe)
    embeddings_function = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vectorstore = Chroma(
        persist_directory="data/chroma_db",
        embedding_function=embeddings_function,
        collection_name="flashcards"  # Nombre específico
    )
    
    new_docs = []
    new_ids = []
    duplicates = []
    
    for flashcard in flashcards["flashcards"]:
        # Normalizar
        palabra_norm = flashcard["palabra"].strip().lower()
        traduccion_norm = flashcard["traduccion"].strip().lower()
        
        # Generar ID determinístico
        u_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, palabra_norm))
        
        # Verificar si ya existe
        try:
            existing = vectorstore.get(ids=[u_id])
            if existing and existing['ids']:
                duplicates.append(flashcard["palabra"])
                continue
        except Exception:
            pass  # DB vacía o primer documento
        
        # Crear documento nuevo
        new_docs.append(
            Document(
                page_content=f"{palabra_norm}\n{traduccion_norm}",
                metadata={
                    "id": u_id,
                    "palabra": flashcard["palabra"],
                    "traduccion": flashcard["traduccion"],
                    "ejemplo_fr": flashcard["ejemplo_fr"],
                    "created_at": datetime.now().isoformat(),
                }
            )
        )
        new_ids.append(u_id)
    
    # Guardar solo los nuevos
    if new_docs:
        vectorstore.add_documents(documents=new_docs, ids=new_ids)
        print(f"✅ Agregados {len(new_docs)} flashcards nuevos")
    
    if duplicates:
        print(f"⚠️ Se encontraron {len(duplicates)} duplicados: {duplicates}")
    
    return {
        "vectorstore": vectorstore,
        "added": len(new_docs),
        "duplicates": duplicates,
        "total_in_db": len(vectorstore.get()['ids']) if vectorstore.get()['ids'] else 0
    }

def get_all_flashcards():
    """
    Obtiene todas las flashcards de la base de datos.
    """
    embeddings_function = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vectorstore = Chroma(
        persist_directory="data/chroma_db",
        embedding_function=embeddings_function,
        collection_name="flashcards"
    )
    
    results = vectorstore.get()
    
    # Formateamos para que sea facil manejar en el frontend
    flashcards = []
    for flashcard in results['metadatas']:
        flashcards.append({
            "palabra": flashcard["palabra"],
            "traduccion": flashcard["traduccion"],
            "ejemplo_fr": flashcard["ejemplo_fr"]
        })
    
    return flashcards

def delete_flashcard(palabra: str):
    """
    Elimina una flashcard de la base de datos.
    """
    embeddings_function = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma(
        persist_directory="data/chroma_db",
        embedding_function=embeddings_function,
        collection_name="flashcards"
    )

    # Generamos el ID de la flashcard a eliminar (determinístico)
    u_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, palabra.strip().lower()))

    # Eliminamos la flashcard
    vectorstore.delete(ids=[u_id])

    print(f"✅ Flashcard eliminada: {palabra}")

def ai_generate_flashcard(palabra: str):
    """
    Genera una flashcard para una palabra específica.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    system_message = SystemMessage(
        content=(
            "Eres un asistente experto en aprendizaje de francés. "
            "Tu tarea es generar una flashcard para la palabra proporcionada. "
            "Para cada elemento encontrado, genera su traducción al español y un ejemplo de uso en francés. "
            "Responde exclusivamente en formato JSON con esta estructura: "
            "{\"flashcards\": [{\"palabra\": \"...\", \"traduccion\": \"...\", \"ejemplo_fr\": \"...\"}]}"
        )
    )

    human_message = HumanMessage(
        content=(
            f"Genera una flashcard para la palabra: {palabra}"
        )
    )

    response = llm.invoke([system_message, human_message])
    
    # Parseamos la respuesta
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"error": "El modelo no devolvió un JSON válido", "raw": response.content}


if __name__ == "__main__":
    # Usamos la imagen de prueba
    test_image = r"data\image0.jpeg"
    print(f"--- Procesando imagen: {test_image} ---")
    
    try:
        resultado = image_to_text(test_image)
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    
    # Guardamos las flashcards en la base de datos
    print(save_flashcards_to_db(resultado))
    

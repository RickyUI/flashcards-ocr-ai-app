from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import base64
from dotenv import load_dotenv

load_dotenv()

def image_to_text(image_path: str) -> dict:
    """
    Analiza una imagen, detecta palabras resaltadas y las devuelve en formato JSON.
    """
    # Configuramos el LLM para que devuelva estrictamente un objeto JSON
    llm = ChatOpenAI(
        model="gpt-4.1-mini", 
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


if __name__ == "__main__":
    # Usamos la imagen de prueba
    test_image = r"data\image0.jpeg"
    print(f"--- Procesando imagen: {test_image} ---")
    
    try:
        resultado = image_to_text(test_image)
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Ocurrió un error: {e}")

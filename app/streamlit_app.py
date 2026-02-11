import streamlit as st
from functions import image_to_text, save_flashcards_to_db, get_all_flashcards
import random

# Configuración de la página
st.set_page_config(page_title="Flashcards AI", page_icon="🇫🇷", layout="centered")

# Inicialización del estado de la aplicación
if "view" not in st.session_state:
    st.session_state.view = "Subir Imagen"
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "flashcards_list" not in st.session_state:
    st.session_state.flashcards_list = []

# --- Sidebar para Navegación ---
with st.sidebar:
    st.title("Menu")
    if st.button("📸 Subir Imagen", use_container_width=True):
        st.session_state.view = "Subir Imagen"
    if st.button("📚 Estudiar", use_container_width=True):
        st.session_state.view = "Estudiar"
        st.session_state.flashcards_list = get_all_flashcards()
        st.session_state.current_card_index = 0
        st.session_state.show_answer = False
        random.shuffle(st.session_state.flashcards_list)

# --- Contenido Principal ---

if st.session_state.view == "Subir Imagen":
    st.title("Flashcards AI")
    st.header("Sube una imagen con palabras en francés")
    
    uploaded_file = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Imagen subida", width="stretch")
        
        if st.button("Procesar imagen"):
            with st.spinner("Procesando imagen con IA..."):
                # Guardamos temporalmente la imagen
                with open("temp_image.jpg", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Procesamos
                resultado = image_to_text("temp_image.jpg")
                
                if "error" in resultado:
                    st.error(f"Error: {resultado['error']}")
                else:
                    st.session_state.last_result = resultado
                    st.success(f"¡Se encontraron {len(resultado['flashcards'])} flashcards!")
            
        if "last_result" in st.session_state:
            resultado = st.session_state.last_result
            # Mostramos las flashcards encontradas
            for flashcard in resultado["flashcards"]:
                with st.expander(f"🇫🇷 {flashcard['palabra']} - 🇪🇸 {flashcard['traduccion']}"):
                    st.write(f"**Ejemplo:** {flashcard['ejemplo_fr']}")
            
            # Botón para guardar
            if st.button("Guardar en mi colección"):
                with st.spinner("Guardando en la base de datos..."):
                    db_result = save_flashcards_to_db(resultado)
                    st.success(f"¡Guardadas {db_result['added']} flashcards!")
                    if db_result['duplicates']:
                        st.warning(f"Se omitieron {len(db_result['duplicates'])} flashcards duplicadas")
                    # Limpiamos para evitar guardar doble accidentalmente
                    del st.session_state.last_result
                    st.rerun()


elif st.session_state.view == "Estudiar":
    st.title("📚 Repaso de Flashcards")
    
    if not st.session_state.flashcards_list:
        st.info("Aún no tienes flashcards guardadas. ¡Sube una imagen primero!")
    else:
        # Calcular progreso
        total = len(st.session_state.flashcards_list)
        current = st.session_state.current_card_index + 1
        st.progress(current / total)
        st.write(f"Tarjeta {current} de {total}")
        
        # Obtener tarjeta actual
        card = st.session_state.flashcards_list[st.session_state.current_card_index]
        
        # --- Interfaz de la Tarjeta ---
        st.markdown("""
            <style>
            .flashcard-container {
                background-color: #f0f2f6;
                padding: 40px;
                border-radius: 15px;
                text-align: center;
                border: 2px solid #e0e0e0;
                margin-bottom: 20px;
            }
            .french-word {
                font-size: 32px;
                font-weight: bold;
                color: #1f77b4;
            }
            .translation {
                font-size: 24px;
                color: #2e7d32;
                margin-top: 10px;
            }
            .example {
                font-style: italic;
                color: #555;
                margin-top: 15px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown(f"""
                <div class="flashcard-container">
                    <div class="french-word">{card['palabra']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if not st.session_state.show_answer:
                if st.button("👁️ Mostrar Respuesta", use_container_width=True):
                    st.session_state.show_answer = True
                    st.rerun()
            else:
                st.markdown(f"""
                    <div class="flashcard-container" style="background-color: #e8f5e9;">
                        <div class="translation">🇪🇸 {card['traduccion']}</div>
                        <div class="example"><b>Ejemplo:</b> {card['ejemplo_fr']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⬅️ Anterior", use_container_width=True, disabled=(st.session_state.current_card_index == 0)):
                        st.session_state.current_card_index -= 1
                        st.session_state.show_answer = False
                        st.rerun()
                with col2:
                    if st.session_state.current_card_index < total - 1:
                        if st.button("Siguiente ➡️", use_container_width=True):
                            st.session_state.current_card_index += 1
                            st.session_state.show_answer = False
                            st.rerun()
                    else:
                        if st.button("🎉 Terminar Sesión", use_container_width=True):
                            st.session_state.view = "Subir Imagen"
                            st.rerun()

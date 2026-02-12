import streamlit as st
from functions import image_to_text, save_flashcards_to_db, get_all_flashcards, delete_flashcard, ai_generate_flashcard
import random
import time

# Page Configuration
st.set_page_config(page_title="Flashcards AI", page_icon="🇫🇷", layout="centered")

# Global Premium Styles
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 500;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .hero-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
    }
    .feature-card {
        background: #ffffff;
        color: #1a2a6c;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        height: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .feature-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transform: translateY(-5px);
    }
    .feature-card h4 {
        color: #1a2a6c !important;
        margin-bottom: 10px;
    }
    .feature-card p {
        color: #444444 !important;
        line-height: 1.5;
    }
    .flashcard-preview {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #1f77b4;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Application State Initialization
if "view" not in st.session_state:
    st.session_state.view = "Home"
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "flashcards_list" not in st.session_state:
    st.session_state.flashcards_list = []

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("🇫🇷 Flashcards AI")
    st.markdown("*Your AI-powered French learning companion*")
    st.divider()
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.view = "Home"
    if st.button("📸 Extract from Image", use_container_width=True):
        st.session_state.view = "Extract"
    if st.button("✨ Generate with AI", use_container_width=True):
        st.session_state.view = "AI Gen"
    st.divider()
    if st.button("📚 Study Mode", use_container_width=True):
        st.session_state.view = "Study"
        st.session_state.flashcards_list = get_all_flashcards()
        st.session_state.current_card_index = 0
        st.session_state.show_answer = False
        random.shuffle(st.session_state.flashcards_list)
    if st.button("⚙️ Manage Collection", use_container_width=True):
        st.session_state.view = "Manage"
        st.session_state.flashcards_list = get_all_flashcards()

# --- UI Help Function ---
def help_popover(title, description):
    with st.popover("❓"):
        st.markdown(f"### {title}")
        st.info(description)

# --- Main Content ---

if st.session_state.view == "Home":
    st.markdown("""
        <div class="hero-container">
            <h1 style="color: #1a2a6c; margin-bottom: 10px;">Master French with AI</h1>
            <p style="font-size: 18px; color: #4b6cb7;">The smartest way to build your vocabulary from books, notes, and ideas.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("### Welcome to Flashcards AI!")
    st.write("This application helps you transform French text into interactive study materials in seconds. Whether you're reading a book or thinking of a word, our AI handles the rest.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h4>📸 Image Extraction</h4>
                <p>Snap a photo of your textbook. Highlight words with a marker, and our OCR will instantly turn them into flashcards with translations and examples.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h4>✨ AI Generation</h4>
                <p>Found a new word? Type it in, and the AI will provide the perfect translation and a natural example sentence to help you understand the context.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🚀 Get Started")
    st.write("1. **Upload or Type:** Go to the sidebar to choose your method.")
    st.write("2. **Save to Deck:** Preview the generated content and add it to your personal collection.")
    st.write("3. **Study:** Use the 'Study Mode' to review your cards with a modern spaced-repetition interface.")
    
    if st.button("Start Now!", type="primary", use_container_width=True):
        st.session_state.view = "Extract"
        st.rerun()

elif st.session_state.view == "Extract":
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.title("📸 Image Extraction")
    with col2:
        help_popover(
            "How it works",
            "- Take a photo of your book or notes.\n"
            "- Ensure words you want to learn are **highlighted**.\n"
            "- The AI detects highlighted text, translates it, and generates examples."
        )
    
    st.header("Upload an image with highlighted French words")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Selected Image", use_container_width=True)
        
        if st.button("✨ Process with AI", type="primary", use_container_width=True):
            with st.spinner("Our AI is analyzing your image..."):
                with open("temp_image.jpg", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                result = image_to_text("temp_image.jpg")
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.session_state.last_result = result
                    st.success(f"Great! We found {len(result['flashcards'])} new words.")
            
        if "last_result" in st.session_state:
            result = st.session_state.last_result
            st.markdown("### Preview:")
            for flashcard in result["flashcards"]:
                with st.expander(f"🇫🇷 {flashcard['palabra']} - 🇪🇸 {flashcard['traduccion']}"):
                    st.write(f"**Example:** {flashcard['ejemplo_fr']}")
            
            if st.button("📥 Save to my deck", use_container_width=True):
                with st.spinner("Saving..."):
                    db_result = save_flashcards_to_db(result)
                    st.success(f"✅ {db_result['added']} flashcards added!")
                    if db_result['duplicates']:
                        st.warning(f"Omitted {len(db_result['duplicates'])} duplicates.")
                    del st.session_state.last_result
                    time.sleep(1)
                    st.rerun()

elif st.session_state.view == "AI Gen":
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.title("✨ AI Generation")
    with col2:
        help_popover(
            "Intelligent Generation",
            "1. Type any French word or phrase you want to learn.\n"
            "2. The AI looks for the most natural translation.\n"
            "3. It creates a contextualized example to help you memorize."
        )
    
    st.markdown("#### What word would you like to learn today?")
    word = st.text_input("Enter a French word or phrase", placeholder="e.g., Épanouissement")
    
    if st.button("🚀 Create Flashcard", type="primary", use_container_width=True):
        if word:
            with st.spinner(f"Generating content for '{word}'..."):
                result = ai_generate_flashcard(word)
                if "error" in result:
                    st.error("Could not generate flashcard. Please try again.")
                else:
                    st.session_state.last_ai_result = result
        else:
            st.warning("Please enter a word first.")

    if "last_ai_result" in st.session_state:
        card = st.session_state.last_ai_result["flashcards"][0]
        st.markdown("---")
        st.markdown(f"""
            <div class="flashcard-preview">
                <h2 style="color: #1f77b4; margin-bottom: 0;">{card['palabra']}</h2>
                <h4 style="color: #2e7d32; margin-top: 5px;">🇪🇸 {card['traduccion']}</h4>
                <p style="font-style: italic; color: #555;"><b>Example:</b> {card['ejemplo_fr']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📥 Add to my deck", use_container_width=True):
            db_result = save_flashcards_to_db(st.session_state.last_ai_result)
            st.success("✅ Added successfully!")
            del st.session_state.last_ai_result
            time.sleep(1)
            st.rerun()

elif st.session_state.view == "Study":
    st.title("📚 Study Mode")
    
    if not st.session_state.flashcards_list:
        st.info("Your deck is empty. Use the Camera or AI to create some flashcards!")
    else:
        current = st.session_state.current_card_index + 1
        total = len(st.session_state.flashcards_list)
        st.progress(current / total)
        st.write(f"Card {current} of {total}")
        
        card = st.session_state.flashcards_list[st.session_state.current_card_index]
        
        st.markdown("""
            <style>
            .flashcard-box {
                background: white;
                padding: 60px 20px;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.05);
                margin: 20px 0;
                border: 1px solid #eee;
            }
            .word-fr { font-size: 42px; font-weight: bold; color: #1f77b4; }
            .word-es { font-size: 30px; color: #2e7d32; }
            </style>
        """, unsafe_allow_html=True)
        
        if not st.session_state.show_answer:
            st.markdown(f'<div class="flashcard-box"><div class="word-fr">{card["palabra"]}</div></div>', unsafe_allow_html=True)
            if st.button("👁️ Reveal Answer", use_container_width=True, type="primary"):
                st.session_state.show_answer = True
                st.rerun()
        else:
            st.markdown(f"""
                <div class="flashcard-box" style="background-color: #f0fff0;">
                    <div class="word-es">🇪🇸 {card['traduccion']}</div>
                    <div style="margin-top:20px; color:#666; font-size: 18px;"><b>Eg:</b> {card['ejemplo_fr']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.current_card_index == 0)):
                    st.session_state.current_card_index -= 1
                    st.session_state.show_answer = False
                    st.rerun()
            with col2:
                if st.session_state.current_card_index < total - 1:
                    if st.button("Next ➡️", use_container_width=True):
                        st.session_state.current_card_index += 1
                        st.session_state.show_answer = False
                        st.rerun()
                else:
                    if st.button("🎉 Finish Session", use_container_width=True):
                        st.balloons()
                        st.session_state.view = "Home"
                        st.rerun()

elif st.session_state.view == "Manage":
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.title("⚙️ My Collection")
    with col2:
        help_popover(
            "Deck Management",
            "Here you can review all your saved words.\n\n"
            "- Use the 🗑️ button to remove words you've mastered or were incorrect.\n"
            "- Deletion is permanent."
        )
    
    if not st.session_state.flashcards_list:
        st.info("Your collection is currently empty.")
    else:
        st.write(f"You have learned **{len(st.session_state.flashcards_list)}** words so far.")
        st.divider()
        
        for i, card in enumerate(st.session_state.flashcards_list):
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                st.markdown(f"**{card['palabra']}**")
                st.caption(f"🇪🇸 {card['traduccion']}")
            with c2:
                if st.button("🗑️", key=f"del_{i}", help="Delete permanently"):
                    delete_flashcard(card['palabra'])
                    st.toast(f"Deleted: {card['palabra']}")
                    time.sleep(0.5)
                    st.session_state.flashcards_list = get_all_flashcards()
                    st.rerun()
            st.divider()

# Flashcards AI

**Master French vocabulary with the power of AI.**

Flashcards AI is a modern web application designed to help French language learners build their personal vocabulary library. By combining advanced OCR (Optical Recognition) and Generative AI, it transforms textbooks, notes, or simple ideas into interactive flashcards for effective studying.

---

## Key Features

### Smart Image Extraction (OCR)

Upload a photo of your book or class notes. If you highlight words with a neon marker, our AI will automatically:

- Detect the highlighted words.
- Provide accurate Spanish translations.
- Generate a natural French example sentence for context.

### AI-Powered Generation

Found a word you want to remember but don't have it in a book? Just type it! The AI will generate a complete flashcard including:

- Perfect translation.
- High-quality contextual usage examples.

### Interactive Study Mode

Study your collection using a clean, modern interface:

- **Flip Cards:** Review the French word and click to reveal the translation and example.
- **Progress Tracking:** See your current progress through your deck.
- **Randomized Sessions:** Every session is shuffled to ensure true long-term memorization.

### Deterministic Collection Management

- **No Duplicates:** The app uses deterministic UUIDs (Namespace-based) to ensure that even if you extract the same word twice, it won't clutter your database.
- **Permanent Cleaning:** Easily remove words you've already mastered.

---

## Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (Premium Dark/Light UI)
- **AI Orchestration:** [LangChain](https://www.langchain.com/)
- **Large Language Models:** OpenAI (GPT-4o-mini)
- **Vector Database:** [ChromaDB](https://www.trychroma.com/)
- **Embeddings:** OpenAI `text-embedding-3-small`

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/RickyUI/flashcards-ocr-ai-app.git
   cd flashcards-ocr-ai-app
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your OpenAI API Key:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

---

## Usage

Launch the application using Streamlit:

```bash
streamlit run app/streamlit_app.py
```

Click on the sidebar menu to navigate between home, extraction, generation, and study mode.

---

## Design and Architecture

- **Deterministic IDs:** Uses `uuid5` based on the word itself, allowing for efficient lookup and deletion without searching the entire vector store.
- **Vector Storage:** Persists locally in `data/chroma_db`, keeping your data private and accessible offline (once processed).
- **Premium UI:** Custom CSS injected into Streamlit for a polished look and feel.

---

Developed for French learners.

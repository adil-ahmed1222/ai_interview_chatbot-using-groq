# Resume AI Interview Chatbot

A production-ready **Personal AI Resume Chatbot** built with **Python** and **Streamlit**. Upload your CV and practice interview answers grounded strictly in your resume — powered by **Groq** (`llama3-70b-8192`) and **LangChain** RAG with **ChromaDB**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![Groq](https://img.shields.io/badge/Groq-LLM-orange)

## Features

- Upload **PDF** or **DOCX** resumes
- Extract text, chunk, embed, and store in **ChromaDB**
- ChatGPT-style chat with **streaming** Groq responses
- **Multi-turn memory** (ConversationBufferMemory + chat history)
- Answers **only from resume** (anti-hallucination system prompts)
- **STAR-method** behavioral answers when supported by CV
- Suggested interview questions & AI interview prep guide
- Auto-detect candidate name from resume header
- Download chat history, clear chat, dark glassmorphism UI
- Modular architecture (`chatbot/`, `utils/`, `prompts/`, `api/`)

## Project Structure

```
AI_interview_chatbot/
├── app.py                 # Streamlit entry point
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── .streamlit/config.toml
├── chatbot/
│   ├── llm.py             # Groq ChatGroq
│   ├── memory.py          # ConversationBufferMemory
│   ├── chains.py          # ConversationalRetrievalChain + RAG
│   ├── prompts.py         # Prompt loaders
│   └── retriever.py       # Chroma vector store
├── utils/
│   ├── pdf_reader.py
│   ├── docx_reader.py
│   ├── text_splitter.py
│   ├── embeddings.py
│   └── helpers.py
├── prompts/
│   ├── system_prompt.txt
│   └── interview_prompt.txt
├── assets/
│   └── styles.css
├── api/                   # Future REST/voice extension
├── uploads/
├── vector_db/chroma_db/
└── data/chat_history/
```

## Prerequisites

- Python **3.10+**
- [Groq API key](https://console.groq.com/keys)

## Setup

### 1. Clone or download the project

```bash
cd AI_interview_chatbot
```

### 2. Create virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> First run downloads the embedding model (`all-MiniLM-L6-v2`) — may take a few minutes.

### 4. Environment variables

Copy the example file and add your Groq key:

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-70b-8192
```

> **Note:** `llama3-70b-8192` may be deprecated on Groq. If you see model errors, set `GROQ_MODEL=llama-3.3-70b-versatile` — the app auto-falls back when needed.

## Run Locally

```bash
streamlit run app.py
```

Open: **http://localhost:8501**

### Usage

1. Open the **sidebar** → upload PDF/DOCX resume → click **Process Resume**
2. Wait for indexing (embeddings + Chroma)
3. Ask interview questions in the chat box or use suggested questions
4. Use **Generate Interview Prep** for a full prep guide
5. **Download Chat History** when finished

## Example Questions

- Tell me about yourself
- Explain your experience at [Company from resume]
- What is SDTM? / What is ADaM?
- Why are you changing jobs?
- Describe a challenging situation
- Explain SAS macros / oncology programming

## GitHub Push

```bash
git init
git add .
git commit -m "Initial commit: Resume AI Interview Chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resume-ai-chatbot.git
git push -u origin main
```

> **Never commit `.env`** — it is listed in `.gitignore`. Use Streamlit Cloud secrets for deployment.

## Deploy on Streamlit Cloud

1. Push your repo to GitHub (without `.env`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. **New app** → select repo → main file: `app.py`
4. Under **Secrets**, add:

```toml
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "llama3-70b-8192"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PERSIST_DIR = "vector_db/chroma_db"
CHUNK_SIZE = "1000"
CHUNK_OVERLAP = "150"
```

5. Deploy — allow extra time for first build (sentence-transformers + Chroma)

### Optional: `packages.txt` for Streamlit Cloud

If builds fail on memory, add a `packages.txt` with system libs as needed, or use `requirements.txt` pins.

## Security

- Store API keys in `.env` locally and **Streamlit Secrets** in production
- Rotate any key that was shared in chat or committed by mistake
- Do not upload confidential resumes to public deployments without consent

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `GROQ_API_KEY is not set` | Create `.env` from `.env.example` |
| Model decommissioned | Set `GROQ_MODEL=llama-3.3-70b-versatile` |
| Empty PDF text | Use text-based PDF, not scanned images |
| Slow first question | Embedding model loads on first resume index |
| Chroma errors | Delete `vector_db/chroma_db/` and re-upload resume |

## Tech Stack

| Layer | Technology |
|-------|------------|
| UI | Streamlit |
| LLM | Groq — llama3-70b-8192 |
| Framework | LangChain |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers (HuggingFace) |
| Parsers | pypdf, python-docx |
| Config | python-dotenv |

## License

MIT — use freely for learning and portfolio projects.

## Author

Built for interview preparation with resume-grounded AI responses.

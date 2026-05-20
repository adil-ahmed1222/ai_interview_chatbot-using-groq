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

## Deployment

### Do not use Vercel for this project

If you see:

```text
Error: Found app.py but it does not define a top-level "app" Flask instance.
```

That is expected. [Vercel](https://vercel.com/docs/frameworks/backend/flask) treats `app.py` as a **Flask** backend. This repo is a **Streamlit** app (long-running Python server + WebSockets), which Vercel serverless does **not** support.

| Platform | Works? | Why |
|----------|--------|-----|
| **Streamlit Cloud** | Yes | Built for Streamlit |
| **Render** | Yes | Long-running web service (`render.yaml` included) |
| **Railway / Fly.io / Docker** | Yes | Use included `Dockerfile` |
| **Vercel** | No | Serverless Flask/Next.js — not Streamlit |

---

### Option A — Streamlit Cloud (recommended)

1. Repo: [ai_interview_chatbot-using-groq](https://github.com/adil-ahmed1222/ai_interview_chatbot-using-groq)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app**
3. Repository: `adil-ahmed1222/ai_interview_chatbot-using-groq`
4. Branch: `main` · Main file path: **`app.py`**
5. **Advanced settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "llama-3.3-70b-versatile"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# CHROMA_PERSIST_DIR optional — omit on Streamlit Cloud (uses in-memory automatically)
CHROMA_USE_MEMORY = "true"
# On Streamlit Cloud, FAISS in-memory is used automatically (no Chroma SQLite errors)
CHUNK_SIZE = "1000"
CHUNK_OVERLAP = "150"
```

6. Deploy (first build may take 5–10 min for embeddings).

---

### Option B — Render

1. [render.com](https://render.com) → **New** → **Blueprint**
2. Connect GitHub repo `ai_interview_chatbot-using-groq`
3. Render reads `render.yaml` automatically
4. Add environment variable **`GROQ_API_KEY`** in the dashboard
5. Deploy → open the generated `.onrender.com` URL

---

### Option C — Docker (Railway, Fly.io, etc.)

```bash
docker build -t interview-chatbot .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key interview-chatbot
```

Open `http://localhost:8501`

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
| Vercel: Flask `app` error | Use Streamlit Cloud or Render — Vercel does not run Streamlit |
| Protobuf / Descriptors error on Index Resume | Use Python **3.12** on Streamlit Cloud; pull latest `requirements.txt` |
| Chroma `no such table: tenants` | Pull latest code — Streamlit Cloud uses FAISS in-memory automatically |
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

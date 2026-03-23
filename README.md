# 🚀 ZeroEntropy Interactive RAG Demo

[![DevSecOps Compliant CI](https://github.com/Taiwrash/zey-ollama-rag-lab/actions/workflows/ci.yaml/badge.svg)](https://github.com/Taiwrash/zey-ollama-rag-lab/actions/workflows/ci.yaml)

This demo showcases a premium **RAG (Retrieval-Augmented Generation)** experience, comparing a base LLM with a ZeroEntropy-enhanced model. It features a modern observability stack using **Langfuse** to trace retrieval quality and collect human feedback.

---

## 🛠 Tech Stack
- **Retrieval**: [ZeroEntropy](https://zeroentropy.dev) (Neural Reranking with `zerank-2`)
- **Generation**: [Ollama](https://ollama.com) (Local `tinyllama`)
- **Observability**: [Langfuse](https://langfuse.com) (Traces, Prompts, and Human Feedback)
- **Orchestration**: FastAPI + Python 3.13

---

## 🏃‍♂️ Quick Start (Docker - Self-Contained)

The easiest way to run the entire stack (including local Ollama) is via Docker.

### 1. Configure your environment
Create a `.env` file in the root directory:
```env
ZEROENTROPY_API_KEY=your_zeroentropy_key
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 2. Build and Run
```bash
# Build the self-contained image
docker build -t zey-rag-lab .

# Run the container
docker run -d \
  -p 8000:8000 \
  -p 11434:11434 \
  --name zey-lab \
  --env-file .env \
  zey-rag-lab
```

### 3. Access the UI
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

> [!NOTE]
> On the first run, the container will automatically pull the `tinyllama` model (~650MB). This can take 30-60 seconds before the web UI becomes available.

---

## 🧠 What's Being Showcased?

### 1. Side-by-Side Comparison
The UI presents two answers for every query:
- **Base LLM**: Raw TinyLlama response with no external knowledge.
- **ZeroEntropy RAG**: TinyLlama response augmented with high-precision context retrieved via `zerank-2`.

### 2. Full Observability with Langfuse
Every query is traced end-to-end. You can see:
- **Retrieval Latency**: Exactly how fast ZeroEntropy finds context.
- **Context Quality**: The actual chunks passed to the LLM are logged as observations.
- **Prompt Versioning**: The system prompt is managed via Langfuse, allowing updates without code redeploys.

### 3. Human-in-the-Loop Feedback
Click the 👍 or 👎 buttons in the UI to log "User Preference" scores directly into the Langfuse dashboard. This builds a dataset to prove the performance gain of your RAG system over time.

---

## 🛠 Local Development

If you prefer to run outside of Docker:

### 1. Setup Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Index Your Data
```bash
# Index the sample documents into ZeroEntropy
python 01_indexing.py
```

### 3. Start the Orchestrator
```bash
# Ensure local Ollama is running and tinyllama is pulled
python app.py
```

---

## 📂 Project Structure
- `app.py`: FastAPI orchestrator with Langfuse tracing.
- `index.html`: Premium glassmorphic UI with feedback integration.
- `01_indexing.py`: Logic for populating the ZeroEntropy collection.
- `entrypoint.sh`: Container startup script for Ollama + FastAPI.
- `baseDockerfile`: Template for the specialized Python 3.13 + Ollama environment.

---

Produced by **Taiwrash** for ZeroEntropy.

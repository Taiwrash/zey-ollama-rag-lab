# 🚀 ZeroEntropy Interactive RAG Demo

This demo showcases a premium **RAG (Retrieval-Augmented Generation)** experience, comparing a base LLM with a ZeroEntropy-enhanced model. It uses **ZeroEntropy** for world-class retrieval and **Ollama** for private, local generation.

---

## 🛠 Prerequisites

1.  **ZeroEntropy API Key**: Get one at [zeroentropy.dev](https://zeroentropy.dev).
2.  **Ollama**: Install it from [ollama.com](https://ollama.com).
3.  **Docker**: Ensure Docker is installed and running.

---

## 🏃‍♂️ Quick Start (Docker)

The easiest way to see this in action fast is via the pre-built Docker image.

### 1. Configure your environment
Create a `.env` file in your local directory:
```env
ZEROENTROPY_API_KEY=your_key_here
OLLAMA_HOST=http://host.docker.internal:11434
```

### 2. Allow Ollama connections (Mac/Windows)
To let the Docker container talk to your local Ollama:
- **Mac**: Run `launchctl setenv OLLAMA_HOST "0.0.0.0"` and restart the Ollama app.
- **Windows**: Set the environment variable `OLLAMA_HOST` to `0.0.0.0` in your System Settings and restart Ollama.

### 3. Run the Demo
Run the following command to pull and start the lab:
```bash
docker run -p 8000:8000 \
  --env-file .env \
  --add-host=host.docker.internal:host-gateway \
  taiwrash/zeroentropy-demo-by-taiwrash
```

Access the UI at: **[http://localhost:8000](http://localhost:8000)**

> Infinite Loading means the environment variables are not set correctly.

---

## 🛠 Build from Source

If you want to modify the code or see the indexing logic:

### 1. Clone the Repo
```bash
git clone https://github.com/taiwrash/zey-ollama-rag-lab
cd zey-ollama-rag-lab
```

### 2. Setup Lifecycle
Before the RAG system can "know" your data, you need to index it:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install requirements
pip install -r requirements.txt

# Index sample documents
python 01_indexing.py
```

### 3. Run the Demos
- `python 01_indexing.py`: Index sample documents.
- `python 05_rag_ollama.py`: Run a full RAG loop in your terminal.
> 1. **Note:** Ensure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull tinyllama`).
> 2. Run `export OLLAMA_HOST=http://localhost:11434` in your terminal.
- `python app.py`: **Run the full Web UI comparison tool** (accessible at `http://localhost:8000`).

---

## 📂 Key Capabilities Shown
- **Neural Reranking**: Using ZeroEntropy's `zerank-2` for high-precision context.
- **Hybrid Search**: Combining semantic relevance with metadata filters.
- **Privacy-First**: Keeping the "brain" (LLM) local while offloading complex retrieval to ZeroEntropy.

Produced by **Taiwrash** for ZeroEntropy.

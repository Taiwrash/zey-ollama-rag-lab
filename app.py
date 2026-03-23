import os
import uuid
import ollama
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy
from langfuse import Langfuse, observe, propagate_attributes

load_dotenv()

app = FastAPI(title="ZEY — ZeroEntropy RAG Lab")

# ── clients ──────────────────────────────────────────────────────────────────
zclient = ZeroEntropy()
lf = Langfuse()

ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=ollama_host)

MODEL = "tinyllama"

# ── request / response models ─────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    collection: str = "demo_collection"

class FeedbackRequest(BaseModel):
    trace_id: str
    mode: str          # "base" | "rag"
    value: int         # 1 = 👍  |  -1 = 👎

# ── traced helpers ────────────────────────────────────────────────────────────
@observe(name="base-llm-generation", as_type="generation")
def _base_generation(query: str) -> str:
    """Call TinyLlama with no extra context."""
    response = ollama_client.chat(
        model=MODEL,
        messages=[{"role": "user", "content": query}],
    )
    text = response["message"]["content"]

    # In v4, use usage_details instead of usage
    lf.update_current_generation(
        metadata={"mode": "base"},
        usage_details={"total": response.get("eval_count", 0)},
    )
    return text


@observe(name="zeroentropy-retrieval")
def _retrieve_context(query: str, collection: str, k: int = 3) -> tuple[str, list[dict]]:
    """Fetch top-k snippets from ZeroEntropy with zerank-2 reranking."""
    snippets = zclient.queries.top_snippets(
        collection_name=collection,
        query=query,
        k=k,
        reranker="zerank-2",
    )

    chunks = [
        {
            "content": s.content,
            "score": getattr(s, "score", None),
        }
        for s in snippets.results
    ]
    context_text = "\n\n".join(c["content"] for c in chunks)

    lf.update_current_span(
        metadata={
            "collection": collection,
            "k": k,
            "reranker": "zerank-2",
            "num_chunks": len(chunks),
            "top_score": chunks[0]["score"] if chunks else None,
        },
    )
    return context_text, chunks


@observe(name="rag-llm-generation", as_type="generation")
def _rag_generation(query: str, context_text: str) -> str:
    """Call TinyLlama augmented with ZeroEntropy context."""
    # Fetch the versioned prompt from Langfuse
    try:
        remote_prompt = lf.get_prompt("rag-system-prompt")
        system_prompt = remote_prompt.compile(context=context_text)
        lf.update_current_generation(prompt=remote_prompt)
    except Exception:
        system_prompt = (
            "You are a head of developer experience at ZeroEntropy. "
            "Use the following retrieved context to answer accurately. "
            "If the answer is not in the context, say you don't know based on context.\n\n"
            f"Context:\n{context_text}"
        )

    response = ollama_client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    )
    text = response["message"]["content"]

    lf.update_current_generation(
        metadata={"mode": "rag"},
        usage_details={"total": response.get("eval_count", 0)},
    )
    return text


# ── main endpoint ─────────────────────────────────────────────────────────────
@observe(name="rag-comparison")
@app.post("/api/ask")
async def ask(request: QueryRequest):
    # Root trace metadata
    try:
        lf.update_current_span(
            metadata={
                "app": "zey-ollama-rag-lab",
                "collection": request.collection,
                "model": MODEL,
            }
        )
    except Exception:
        pass

    try:
        # ── Base LLM ──────────────────────────────────────────────────────────
        base_text = _base_generation(request.query)

        # ── RAG pipeline ──────────────────────────────────────────────────────
        try:
            context_text, chunks = _retrieve_context(
                request.query, request.collection
            )
        except Exception as retrieval_err:
            context_text = f"[Retrieval error: {retrieval_err}]"
            chunks = []

        rag_text = _rag_generation(request.query, context_text)

        trace_id = lf.get_current_trace_id()

        return {
            "base_response": base_text,
            "rag_response": rag_text,
            "context_used": context_text,
            "trace_id": trace_id,
        }

    except Exception as e:
        error_msg = str(e)
        if "ConnectionRefusedError" in error_msg or "failed to connect" in error_msg.lower():
            error_msg = (
                f"Could not reach Ollama at {ollama_host}. "
                "If running in Docker, set OLLAMA_HOST=http://localhost:11434 "
                "and make sure Ollama is listening on 0.0.0.0."
            )
        raise HTTPException(status_code=500, detail=error_msg)


# ── human-feedback endpoint ───────────────────────────────────────────────────
@app.post("/api/feedback")
async def feedback(data: FeedbackRequest):
    try:
        lf.score(
            trace_id=data.trace_id,
            name="user-preference",
            value=float(data.value),
            comment=f"preferred: {data.mode}",
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── serve UI ──────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r") as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

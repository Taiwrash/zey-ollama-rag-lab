import os
import ollama
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy

load_dotenv()

app = FastAPI()

zclient = ZeroEntropy()

ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=ollama_host)

class QueryRequest(BaseModel):
    query: str
    collection: str = "demo_collection"

@app.post("/api/ask")
async def ask(request: QueryRequest):
    try:
        # 1. Base LLM Response (No Context)
        base_response = ollama_client.chat(
            model='tinyllama',
            messages=[{'role': 'user', 'content': request.query}]
        )
        base_text = base_response['message']['content']

        # 2. RAG Response (With ZeroEntropy Context)
        try:
            snippets = zclient.queries.top_snippets(
                collection_name=request.collection,
                query=request.query,
                k=3,
                reranker="zerank-2"
            )
            context_text = "\n\n".join([s.content for s in snippets.results])
        except Exception as e:
            context_text = f"Error retrieving context: {str(e)}"

        system_prompt = f"""
        You are a head pf developer experience at ZeroEntropy. Use the following retrieved context 
        to answer accurately. If not in context, say you don't know based on context.

        Context:
        {context_text}
        """

        rag_response = ollama_client.chat(
            model='tinyllama',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': request.query},
            ]
        )
        rag_text = rag_response['message']['content']

        return {
            "base_response": base_text,
            "rag_response": rag_text,
            "context_used": context_text
        }
    except Exception as e:
        error_msg = str(e)
        if "ConnectionRefusedError" in error_msg or "failed to connect" in error_msg.lower():
            error_msg = f"Could not reach Ollama at {ollama_host}. If running in Docker, ensure OLLAMA_HOST is set to http://host.docker.internal:11434 and Ollama on Mac is set to listen on 0.0.0.0"
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

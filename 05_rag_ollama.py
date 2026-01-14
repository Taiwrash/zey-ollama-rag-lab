import os
import ollama
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy

load_dotenv()

def run_local_rag_demo():
    zclient = ZeroEntropy()
    collection_name = "demo_collection"
    
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_client = ollama.Client(host=ollama_host)
    
    user_query = "What are the core capabilities of ZeroEntropy?"
    
    print(f"--- Local RAG Demo with ZeroEntropy + TinyLlama (via Ollama) ---")
    print(f"Question: {user_query}\n")

    # 2. Retrieval Step: Get relevant snippets from ZeroEntropy
    print("Step 1: Retrieving context from ZeroEntropy...")
    try:
        snippets = zclient.queries.top_snippets(
            collection_name=collection_name,
            query=user_query,
            k=3,
            reranker="zerank-2"  # Using reranker for better context
        )
    except Exception as e:
        print(f"Error during retrieval: {e}")
        print("Tip: Make sure you ran 01_indexing.py first to populate the collection!")
        return

    # Extract text from snippets (snippets is a SnippetRetrievalResponse object)
    context_text = "\n\n".join([s.content for s in snippets.results])
    
    if not context_text:
        print("No context found. Defaulting to general knowledge (demo might be empty).")
        context_text = "No specific context available from indexing."

    # 3. Augmentation Step: Prepare the System Prompt
    system_prompt = f"""
    You are a head of developer relations at ZeroEntropy. Use the following pieces of retrieved context 
    to answer the user's question accurately. If the answer isn't in the context, 
    say you don't know based on the provided information.

    Context:
    {context_text}
    """

    # 4. Generation Step: Call Local TinyLlama via Ollama
    print("Step 2: Generating response using local TinyLlama...")
    try:
        response = ollama_client.chat(
            model='tinyllama',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_query},
            ],
        )
        
        print("\n--- Final Answer from TinyLlama ---")
        print(response['message']['content'])
        
    except Exception as e:
        print(f"\nError connecting to Ollama: {e}")
        print("Tip: Ensure Ollama is running and you have run 'ollama pull tinyllama'")

if __name__ == "__main__":
    if not os.getenv("ZEROENTROPY_API_KEY"):
        print("Error: ZEROENTROPY_API_KEY not found in environment.")
    else:
        run_local_rag_demo()

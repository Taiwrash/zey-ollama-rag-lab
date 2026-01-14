import os
import base64
from datetime import datetime
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy

load_dotenv()

def run_indexing_demo():
    zclient = ZeroEntropy()
    
    collection_name = "demo_collection"
    
    print(f"--- 1. Creating Collection: {collection_name} ---")
    try:
        response = zclient.collections.add(collection_name=collection_name)
        print("Collection created successfully.")
    except Exception as e:
        print(f"Note: {e} (Collection might already exist)")

    print(f"\n--- 2. Adding a Text Document ---")
    text_content = """
    ZeroEntropy is a powerful indexing and retrieval engine designed for large-scale AI applications.
    It supports semantic search, metadata filtering, and high-performance reranking.
    This is a sample document for the indexing demo.
    """
    
    try:
        doc_response = zclient.documents.add(
            collection_name=collection_name,
            path="demo/sample_text.txt",
            content={"type": "text", "text": text_content},
            metadata={
                "timestamp": datetime.now().isoformat(),
                "category": "documentation",
                "list:tags": ["demo", "text"]
            }
        )
        print(f"Document added successfully. Message: {doc_response.message}")
    except Exception as e:
        print(f"Note: {e} (Document might already exist)")

    print(f"\n--- 3. Adding a PDF Document (via Base64) --- A simple PDF Simulation---")
    dummy_pdf_base64 = base64.b64encode(b"%PDF-1.4\n1 0 obj\n<<\n/Title (Demo Document)\n>>\nendobj").decode('utf-8')
    
    try:
        pdf_response = zclient.documents.add(
            collection_name=collection_name,
            path="demo/sample_pdf.pdf",
            content={"type": "auto", "base64_data": dummy_pdf_base64},
            metadata={
                "category": "reports",
                "list:tags": ["demo", "pdf"]
            }
        )
        print(f"PDF document added successfully. Message: {pdf_response.message}")
    except Exception as e:
        print(f"Note: {e} (Document might already exist)")

if __name__ == "__main__":
    if not os.getenv("ZEROENTROPY_API_KEY"):
        print("Error: ZEROENTROPY_API_KEY not found in environment. Please set it in .env file.")
    else:
        run_indexing_demo()

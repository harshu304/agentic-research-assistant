from src.retrieval.uploaded_paper_search import (
    search_uploaded_paper
)

from src.agentic.context_builder import (
    build_context
)

import ollama


# ==========================================
# AGENTIC QA PIPELINE
# ==========================================
def agentic_qa_pipeline(
    conn,
    session_id,
    user_question
):

    print("\n==============================")
    print("🤖 AGENTIC RAG PIPELINE START")
    print("==============================")

    print(f"\n❓ USER QUESTION: {user_question}")

    # ==========================================
    # STEP 1 — Retrieve relevant chunks
    # ==========================================
    retrieved_chunks = search_uploaded_paper(
        conn=conn,
        session_id=session_id,
        query=user_question,
        top_k=5
    )

    print(f"\n📄 RETRIEVED CHUNKS: {len(retrieved_chunks)}")

    # ==========================================
    # STEP 2 — Build structured context
    # ==========================================
    context = build_context(retrieved_chunks)

    # ==========================================
    # STEP 3 — Create grounded prompt
    # ==========================================
#     
    prompt = f"""
    You are an expert AI research assistant.

    Answer the user's question ONLY using the provided research-paper context.

    IMPORTANT RULES:
    - Provide detailed technical explanations
    - Explain the methodology clearly
    - Mention architectures, algorithms, optimization methods, and training approaches if present
    - Include fallback mechanisms or evaluation details if mentioned
    - Do NOT hallucinate
    - Do NOT invent information
    - If information is missing, explicitly say:
    "The paper does not explicitly mention this."

    CONTEXT:
    {context}

    QUESTION:
    {user_question}

    DETAILED TECHNICAL ANSWER:
    """

    print("\n🧠 GENERATING ANSWER...")

    # ==========================================
    # STEP 4 — LLM Generation
    # ==========================================
    response = ollama.chat(
        model="qwen2.5",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    print("\n✅ ANSWER GENERATED")

    return answer
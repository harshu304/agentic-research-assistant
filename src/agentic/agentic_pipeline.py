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
    You are a research paper QA assistant.

    Answer ONLY using the provided context.

    Do NOT add assumptions.
    Do NOT generate extra explanations.
    Do NOT include unrelated details.

    If information is missing, say:
    'The paper does not explicitly mention this.'

    Provide:
    1. Direct answer
    2. Key methodology details
    3. Important supporting points

    ================ CONTEXT ================

    {context}

    ================ QUESTION ================

    {user_question}

    ================ ANSWER ================
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
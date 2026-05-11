from src.retrieval.uploaded_paper_search import (
    search_uploaded_paper
)

from src.agentic.context_builder import (
    build_context
)

import ollama


# ==========================================
# DETECT WEAK ANSWERS
# ==========================================
def is_weak_answer(answer):

    weak_patterns = [

        "not explicitly mention",

        "insufficient information",

        "not enough context",

        "cannot determine",

        "unclear",

        "not provided"
    ]

    answer_lower = answer.lower()

    # too short
    if len(answer.split()) < 40:
        return True

    # weak phrase detection
    for pattern in weak_patterns:

        if pattern in answer_lower:
            return True

    return False


# ==========================================
# QUERY REWRITING
# ==========================================
def rewrite_query(query):

    query_map = {

        "methodology":
            "LLM-based few-shot learning methodology",

        "results":
            "experimental results and performance evaluation",

        "conclusion":
            "paper conclusion and future work",

        "architecture":
            "model architecture and framework",

        "training":
            "training methodology and optimization",

        "evaluation":
            "performance evaluation and experiments"
    }

    lower_query = query.lower()

    for key, improved in query_map.items():

        if key in lower_query:

            return improved

    return query


# ==========================================
# GENERATE ANSWER
# ==========================================
def generate_answer(
    question,
    context
):

    prompt = f"""
You are a research paper QA assistant.

Answer ONLY using the provided context.

Do NOT hallucinate.
Do NOT add assumptions.
Do NOT invent methodologies.
Do NOT generate unrelated details.

If information is missing, say:
'The paper does not explicitly mention this.'

Provide:
1. Direct answer
2. Key methodology details
3. Important supporting points

================ CONTEXT ================

{context}

================ QUESTION ================

{question}

================ ANSWER ================
"""

    response = ollama.chat(

        model="qwen2.5",

        messages=[

            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


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
    # STEP 1 — INITIAL RETRIEVAL
    # ==========================================
    retrieved_chunks = search_uploaded_paper(

        conn=conn,

        session_id=session_id,

        query=user_question,

        top_k=5
    )

    print(
        f"\n📄 RETRIEVED CHUNKS: "
        f"{len(retrieved_chunks)}"
    )

    # ==========================================
    # STEP 2 — BUILD CONTEXT
    # ==========================================
    context = build_context(
        retrieved_chunks
    )

    # ==========================================
    # STEP 3 — GENERATE INITIAL ANSWER
    # ==========================================
    print("\n🧠 GENERATING INITIAL ANSWER...")

    answer = generate_answer(

        user_question,

        context
    )

    print("\n====================")
    print("INITIAL ANSWER")
    print("====================")

    print(answer)

    # ==========================================
    # STEP 4 — EVALUATE ANSWER
    # ==========================================
    weak = is_weak_answer(answer)

    print(
        f"\n🧪 WEAK ANSWER DETECTED: "
        f"{weak}"
    )

    # ==========================================
    # STEP 5 — RETRY LOOP
    # ==========================================
    if weak:

        improved_query = rewrite_query(
            user_question
        )

        print(
            f"\n🔄 REWRITTEN QUERY: "
            f"{improved_query}"
        )

        improved_chunks = search_uploaded_paper(

            conn=conn,

            session_id=session_id,

            query=improved_query,

            top_k=5
        )

        print(
            f"\n📄 IMPROVED CHUNKS: "
            f"{len(improved_chunks)}"
        )

        improved_context = build_context(
            improved_chunks
        )

        print("\n🧠 REGENERATING ANSWER...")

        answer = generate_answer(

            improved_query,

            improved_context
        )

    print("\n====================")
    print("FINAL ANSWER")
    print("====================")

    print(answer)

    print("\n✅ ANSWER GENERATED")

    return answer
import ollama


def generate_answer(question, context):
    prompt = f"""
You are an AI research assistant.

STRICT RULES:
- Use ONLY the provided context.
- DO NOT invent any paper, link, or fact.
- If something is not explicitly in the context, write: "Not found in context".
- When referencing a paper, COPY the exact Title and Link from the context.
- Cite sources inline using [Title].

---------------------
Context:
{context}
---------------------

Question:
{question}

Answer format:
- Answer:
- Evidence (quotes from context):
- References (exact Title + Link as given):
"""
    response = ollama.chat(
        model="deepseek-llm",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2}
    )
    return response["message"]["content"]
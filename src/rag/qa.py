import ollama


def generate_answer(question, context):
    prompt = f"""
You are an AI research assistant.
You are a strict RAG assistant.

Answer ONLY using the provided context.
If the answer is NOT present, say:
"Not found in database."

Also provide the exact sentence used.
Do NOT use prior knowledge.
STRICT RULES:
- Use ONLY the provided context
- If exact match is not found, return the closest relevant paper
- Always include Title, Year, and Link

---------------------
Context:
{context}
---------------------

Question:
{question}

Answer format:

Result:
- Title:
- Year:
- Authors:
- Link:
"""
    response = ollama.chat(
        model="deepseek-llm",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2}
    )
    return response["message"]["content"]
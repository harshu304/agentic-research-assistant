import ollama


def generate_answer(question, context):
    prompt = f"""
You are a helpful AI research assistant.

Use ONLY the provided research paper context to answer.

If answer is not found, say "Not enough information".

---------------------
Context:
{context}
---------------------

Question:
{question}

Answer:
"""

    response = ollama.chat(
        # model="deepseek",
        model="deepseek-coder",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]
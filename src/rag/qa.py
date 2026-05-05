import ollama


def generate_answer(question, context):
    prompt = f"""
You are a STRICT research assistant.

RULES (MANDATORY):
- You can ONLY use the provided context
- DO NOT use any external knowledge
- DO NOT say "I cannot browse" or similar
- DO NOT generate new paper titles
- ONLY use papers listed in context
- If no answer → say: "No relevant paper found in database"

---------------------
CONTEXT (ONLY SOURCE OF TRUTH):
{context}
---------------------

QUESTION:
{question}

OUTPUT FORMAT (STRICT):

Answer:
- Short explanation

Papers:
- EXACT Title (Year)
- EXACT Title (Year)
"""
    response = ollama.chat(
        model="deepseek-llm",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1}
        
    )
    return response["message"]["content"]
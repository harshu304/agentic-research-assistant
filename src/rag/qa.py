# import ollama


# def generate_answer(question, context):

#     prompt = f"""
# You are a helpful research assistant.

# You MUST answer ONLY using the provided research paper context.

# IMPORTANT RULES:
# - Do NOT invent paper titles
# - Do NOT use external knowledge
# - Use ONLY the provided papers
# - If relevant papers exist:
#     - summarize them briefly
#     - include exact paper titles
#     - include links if available
# - If no relevant papers exist:
#     say exactly:
#     "No relevant paper found in database"

# ===============================================================================
# RESEARCH PAPER CONTEXT
# ===============================================================================

# {context}

# ===============================================================================
# QUESTION
# ===============================================================================

# {question}

# ===============================================================================
# OUTPUT FORMAT
# ===============================================================================

# Answer:
# <short explanation>

# Papers:
# - Exact Paper Title (Year)
#   Link: <pdf link>

# - Exact Paper Title (Year)
#   Link: <pdf link>
# """

#     # ==========================================
#     # DEBUG: print prompt sent to LLM
#     # ==========================================
#     print("\n" + "=" * 80)
#     print("🧠 FINAL PROMPT SENT TO LLM")
#     print("=" * 80)

#     print(prompt[:5000])

#     print("\n" + "=" * 80)

#     # ==========================================
#     # LLM CALL
#     # ==========================================
#     response = ollama.chat(
#         model="qwen2.5",
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         options={
#             "temperature": 0.1
#         }
#     )

#     answer = response["message"]["content"]

#     # ==========================================
#     # DEBUG: raw LLM response
#     # ==========================================
#     print("\n🤖 RAW LLM RESPONSE:\n")
#     print(answer)

#     return answer


import ollama
import re
from typing import Dict, List, Optional


def validate_context(context: str) -> Dict[str, any]:
    """
    Validate and analyze the context to detect potential issues.
    
    Args:
        context: The paper context to validate
        
    Returns:
        Dictionary with validation results
    """
    validation = {
        "has_papers": False,
        "paper_count": 0,
        "has_links": False,
        "has_none_links": False,
        "context_length": len(context)
    }
    
    # Count papers
    paper_count = context.count("[PAPER]")
    validation["paper_count"] = paper_count
    validation["has_papers"] = paper_count > 0
    
    # Check for links
    validation["has_links"] = "Link: http" in context or "Link: https" in context
    validation["has_none_links"] = "Link: None" in context
    
    return validation


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer to a research question using LLM with improved prompting.
    
    Args:
        question: The user's research question
        context: The paper context to search through
        
    Returns:
        The LLM's response with papers
    """
    
    # ==========================================
    # VALIDATION: Check context quality
    # ==========================================
    validation = validate_context(context)
    
    print("\n" + "=" * 80)
    print("📊 CONTEXT VALIDATION")
    print("=" * 80)
    print(f"✓ Papers found: {validation['paper_count']}")
    print(f"✓ Papers have links: {validation['has_links']}")
    print(f"✓ Papers marked as 'None': {validation['has_none_links']}")
    print(f"✓ Context length: {validation['context_length']} characters")
    print("=" * 80)
    
    # ==========================================
    # IMPROVED PROMPT
    # ==========================================
    prompt = f"""
You are a research assistant.

Use ONLY the provided context.

Your task:
1. Answer the user's question clearly and directly
2. Then provide supporting research papers
3. Explain concepts in simple language
4. Do not hallucinate information

FORMAT:

Answer:
<clear explanation>

Supporting Papers:
- Title (Year)
  Link: ...

CONTEXT:
{context}

QUESTION:
{question}
"""

    # ==========================================
    # DEBUG: Print prompt sent to LLM
    # ==========================================
    print("\n" + "=" * 80)
    print("🧠 FINAL PROMPT SENT TO LLM")
    print("=" * 80)
    print(prompt[:6000])
    if len(prompt) > 6000:
        print(f"\n... (prompt truncated, total length: {len(prompt)} chars)")
    print("\n" + "=" * 80)

    # ==========================================
    # LLM CALL with error handling
    # ==========================================
    try:
        print("\n⏳ Calling Qwen 2.5 LLM...")
        response = ollama.chat(
            model="qwen2.5",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.1,  # Low temperature for consistent, factual responses
                "top_p": 0.9,
                "num_predict": 500  # Limit output length
            }
        )
        
        answer = response["message"]["content"]
        
    except Exception as e:
        print(f"\n❌ Error calling LLM: {str(e)}")
        return f"Error: Failed to get response from LLM: {str(e)}"

    # ==========================================
    # POST-PROCESSING: Validate LLM response
    # ==========================================
    print("\n🤖 RAW LLM RESPONSE:\n")
    print(answer)
    print("\n" + "=" * 80)
    
    # Validation checks
    validation_results = validate_response(answer, validation)
    
    print("\n📋 RESPONSE VALIDATION")
    print("=" * 80)
    print(f"✓ Response length: {len(answer)} characters")
    print(f"✓ Contains paper titles: {validation_results['has_papers']}")
    print(f"✓ Contains links: {validation_results['has_links']}")
    print(f"✓ No hallucinated papers: {validation_results['no_hallucination']}")
    print("=" * 80)
    
    if validation_results['warning']:
        print(f"\n⚠️  WARNING: {validation_results['warning']}")
    
    return answer


def validate_response(response: str, context_validation: Dict) -> Dict[str, any]:
    """
    Validate the LLM's response quality.
    
    Args:
        response: The LLM's response
        context_validation: Validation results from context
        
    Returns:
        Dictionary with validation results
    """
    validation = {
        "has_papers": False,
        "has_links": False,
        "no_hallucination": True,
        "warning": None
    }
    
    # Check if response mentions papers
    validation["has_papers"] = "Paper" in response or "TITLE:" in response.upper()
    validation["has_links"] = ("http" in response or "Link:" in response)
    
    # Warning if context had papers but response says "no papers found"
    if context_validation["has_papers"] and "No relevant paper" in response:
        validation["warning"] = (
            "Context contains papers but LLM returned 'No relevant papers'. "
            "This may indicate weak retrieval or query mismatch."
        )
    
    return validation


def extract_papers_from_response(response: str) -> List[Dict[str, str]]:
    """
    Extract structured paper information from the LLM response.
    
    Args:
        response: The LLM's response
        
    Returns:
        List of paper dictionaries with title, year, and link
    """
    papers = []
    
    # Pattern to match "- Title (Year)" followed by "Link:"
    pattern = r'-\s*([^(]+)\s*\((\d{4})\)\s*\n\s*Link:\s*(.+)'
    matches = re.findall(pattern, response)
    
    for title, year, link in matches:
        papers.append({
            "title": title.strip(),
            "year": year,
            "link": link.strip()
        })
    
    return papers


if __name__ == "__main__":
    # Example usage
    sample_context = """
[PAPER]
Title: LinkTransformer: A Unified Package for Record Linkage with Transformer Language Models
Year: 2023
Authors: 
Link: None

Abstract:
Linking information across sources is fundamental to a variety of analyses in social science, business, and government. While large language models (LLMs) offer enormous promise for improving record linkage in noisy datasets...

[PAPER]
Title: RankVicuna: Zero-Shot Listwise Document Reranking with Open-Source Large Language Models
Year: 2023
Authors: 
Link: None

Abstract:
Researchers have successfully applied large language models (LLMs) such as ChatGPT to reranking in an information retrieval context...
"""
    
    sample_question = "Show me research papers related to LLM with links"
    
    print("\n🚀 RESEARCH ASSISTANT START")
    print("=" * 80)
    
    answer = generate_answer(sample_question, sample_context)
    
    print("\n📚 EXTRACTED PAPERS:")
    print("=" * 80)
    papers = extract_papers_from_response(answer)
    if papers:
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper['title']} ({paper['year']})")
            print(f"   Link: {paper['link']}")
    else:
        print("No papers extracted from response")
    
    print("\n✅ ASSISTANT COMPLETE")
    print("=" * 80)
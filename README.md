# Agentic Research Paper RAG System

An intelligent Research Paper Question Answering system built using a lightweight Agentic RAG architecture.

This project enables users to:

- Search research papers semantically
- Upload research paper PDFs
- Ask detailed technical questions
- Retrieve methodology, experiments, results, and architecture details
- Perform grounded Question Answering over uploaded research papers

The system combines:

- Semantic Search
- Vector Databases
- Section-Aware Retrieval
- CrossEncoder Reranking
- Agentic Retrieval Routing
- LLM-based grounded answer generation

---

# Features

## Research Paper Semantic Search

- Semantic paper retrieval using embeddings
- Latest research paper retrieval
- Year-aware filtering
- PostgreSQL pgvector similarity search
- Metadata-based retrieval

---

## Uploaded Research Paper QA

Users can upload digital research paper PDFs and ask unlimited questions.

### Pipeline

PDF Upload  
→ Text Extraction  
→ Research Paper Validation  
→ Section Parsing  
→ Chunking  
→ Embedding Generation  
→ PostgreSQL Vector Storage  
→ Semantic Retrieval  
→ CrossEncoder Reranking  
→ LLM Answer Generation

---

## Section-Aware Retrieval

The system intelligently detects sections such as:

- Abstract
- Introduction
- Methodology
- Experiments
- Results
- Challenges
- Conclusion
- References

This significantly improves retrieval quality for research-based questions.

Example:

| User Question | Prioritized Section |
|---|---|
| What methodology is used? | Methodology |
| What dataset was used? | Experiments |
| What are the results? | Results |
| What are the limitations? | Challenges |

---

## Agentic RAG Features

### Query-Aware Retrieval

The system analyzes user intent and dynamically routes retrieval toward relevant paper sections.

---

### CrossEncoder Reranking

Retrieved chunks are reranked using a transformer-based reranker to improve context relevance.

---

### Grounded LLM Generation

Answers are generated only from retrieved research-paper context to reduce hallucinations.

---

# Example Questions

Users can ask:

- What methodology is used?
- Explain the proposed architecture
- What optimization method is proposed?
- What dataset was used?
- Summarize the experimental setup
- What are the key results?
- What challenges are discussed?
- What future work is suggested?

---

# Architecture

## High-Level Architecture

```text
User Query
    ↓
Query Analyzer
    ↓
Section-Aware Retrieval
    ↓
PostgreSQL pgvector Search
    ↓
CrossEncoder Reranking
    ↓
Context Builder
    ↓
LLM Answer Generation
    ↓
Final Grounded Answer
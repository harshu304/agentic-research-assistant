import json

def clean_data(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned = []

    for paper in raw_data:
        # ❌ Skip if no abstract
        if not paper.get("abstract") or len(paper["abstract"].strip()) < 20:
            continue

        # Clean authors
        authors = ", ".join([a["name"] for a in paper.get("authors", [])])

        cleaned.append({
            "paper_id": paper.get("paperId"),
            "title": paper.get("title"),
            "abstract": paper.get("abstract"),
            "year": paper.get("year"),
            "source": paper.get("venue"),
            "pdf_url": paper.get("openAccessPdf", {}).get("url"),
            "authors": authors
        })

    print(f"✅ Cleaned papers: {len(cleaned)} / {len(raw_data)}")

    return cleaned
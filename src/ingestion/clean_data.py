import json


def clean_data(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned = []

    for paper in raw_data:

        # ❌ Skip if no abstract or too small
        abstract = paper.get("abstract")
        if not abstract or len(abstract.strip()) < 20:
            continue

        # ❌ Skip if no title
        title = paper.get("title")
        if not title:
            continue

        # 🔥 SAFE AUTHOR HANDLING
        authors_data = paper.get("authors", [])

        if isinstance(authors_data, list):
            authors = ", ".join([
                a.get("name", "")
                for a in authors_data
                if isinstance(a, dict) and a.get("name")
            ])
        elif isinstance(authors_data, str):
            authors = authors_data
        else:
            authors = ""

        # 🔥 SAFE PDF URL
        pdf_data = paper.get("openAccessPdf", {})
        if isinstance(pdf_data, dict):
            pdf_url = pdf_data.get("url")
        else:
            pdf_url = None

        cleaned.append({
            "paper_id": paper.get("paperId"),
            "title": title,
            "abstract": abstract,
            "year": paper.get("year"),
            "source": paper.get("venue"),
            "pdf_url": pdf_url,
            "authors": authors
        })

    print(f"✅ Cleaned papers: {len(cleaned)} / {len(raw_data)}")

    return cleaned
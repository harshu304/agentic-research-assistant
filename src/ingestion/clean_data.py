import ijson


def clean_data_stream(input_path):
    total = 0
    cleaned_count = 0

    with open(input_path, "r", encoding="utf-8") as f:
        papers = ijson.items(f, "item")

        for paper in papers:
            total += 1

            # ---------- ABSTRACT ----------
            abstract = paper.get("abstract")
            if not abstract or len(abstract.strip()) < 20:
                continue

            abstract = abstract.strip()

            # 🔥 FULL + TRIMMED VERSION
            full_abstract = abstract[:2000]   # store (optional limit)
            embed_text = abstract[:500]      # use for embedding

            # ---------- TITLE ----------
            title = paper.get("title")
            if not title:
                continue
            title = title.strip()

            # ---------- AUTHORS ----------
            authors_data = paper.get("authors", [])
            if isinstance(authors_data, list):
                authors = ", ".join(
                    a.get("name", "")
                    for a in authors_data
                    if isinstance(a, dict) and a.get("name")
                )
            elif isinstance(authors_data, str):
                authors = authors_data
            else:
                authors = ""

            # ---------- PDF ----------
            pdf_data = paper.get("openAccessPdf")
            pdf_url = pdf_data.get("url") if isinstance(pdf_data, dict) else None

            # ---------- YEAR ----------
            year = paper.get("year")
            if not isinstance(year, int):
                year = None

            cleaned_count += 1

            # ---------- OUTPUT ----------
            yield {
                "paper_id": paper.get("paperId"),
                "title": title,
                "abstract": full_abstract,   # ✅ full text stored
                "embed_text": embed_text,    # 🔥 used for embedding
                "year": year,
                "source": paper.get("venue"),
                "pdf_url": pdf_url,
                "authors": authors
            }

            # ---------- PROGRESS ----------
            if total % 100000 == 0:
                print(f"Processed: {total}")

    print(f"✅ Cleaned papers: {cleaned_count} / {total}")
import uuid

from src.ingestion.extract_pdf import (
    extract_text_from_pdf
)

from src.ingestion.validate_paper import (
    is_research_paper
)

from src.ingestion.chunking import (
    chunk_text
)

from src.ingestion.embed import (
    embed_batch
)

from src.ingestion.section_parser import (
    parse_sections
)


# ==========================================
# UPLOAD RESEARCH PAPER PIPELINE
# ==========================================
def upload_research_paper(conn, pdf_path):

    # ==========================================
    # Generate session ID
    # ==========================================
    session_id = str(uuid.uuid4())

    print(f"\n🆔 SESSION ID: {session_id}")

    # ==========================================
    # Extract PDF pages
    # ==========================================
    pages = extract_text_from_pdf(pdf_path)

    print(f"\n📄 TOTAL PAGES: {len(pages)}")

    # ==========================================
    # Create full text
    # ==========================================
    full_text = "\n".join(
        page["text"]
        for page in pages
    )

    # ==========================================
    # Validate research paper
    # ==========================================
    valid = is_research_paper(full_text)

    if not valid:

        print("\n❌ NOT A RESEARCH PAPER")

        return None

    print("\n✅ VALID RESEARCH PAPER")

    # ==========================================
    # PARSE DOCUMENT SECTIONS
    # ==========================================
    parsed_content = parse_sections(pages)

    # ==========================================
    # GROUP TEXT BY SECTION
    # ==========================================
    section_map = {}

    for item in parsed_content:

        section = item["section"]

        text = item["text"]

        if section not in section_map:

            section_map[section] = ""

        section_map[section] += text + "\n"

    # ==========================================
    # CREATE SECTION-WISE CHUNKS
    # ==========================================
    all_chunks = []

    for section, section_text in section_map.items():

        print(f"\n📚 PROCESSING SECTION: {section}")

        chunks = chunk_text(section_text)

        print(f"📦 TOTAL CHUNKS CREATED: {len(chunks)}")

        for chunk in chunks:

            all_chunks.append({
                "section": section,
                "text": chunk
            })

    print(f"\n📦 TOTAL CHUNKS CREATED: {len(all_chunks)}")

    # ==========================================
    # GENERATE EMBEDDINGS
    # ==========================================
    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = embed_batch(texts)

    print(f"\n🧠 EMBEDDINGS GENERATED: {len(embeddings)}")

    # ==========================================
    # INSERT INTO POSTGRESQL
    # ==========================================
    cursor = conn.cursor()

    for idx, (chunk_data, embedding) in enumerate(
        zip(all_chunks, embeddings)
    ):

        print(
            f"\n📚 CHUNK {idx} "
            f"SECTION: {chunk_data['section']}"
        )

        cursor.execute("""
            INSERT INTO uploaded_paper_chunks (
                session_id,
                file_name,
                chunk_id,
                page_number,
                section,
                chunk_text,
                embedding,
                search_vector
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                to_tsvector('english', %s)
            )
        """, (
            session_id,
            pdf_path,
            idx,
            None,
            chunk_data["section"],
            chunk_data["text"],
            embedding,
            chunk_data["text"]
        ))

    conn.commit()

    cursor.close()

    print("\n✅ PAPER INSERTED INTO DATABASE")

    print(f"\n📦 TOTAL CHUNKS STORED: {len(all_chunks)}")

    return session_id
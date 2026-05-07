from src.ingestion.extract_pdf import extract_text_from_pdf
from src.ingestion.chunking import chunk_text

pdf_path = "samle paper.pdf"

pages = extract_text_from_pdf(pdf_path)

full_text = "\n".join(
    page["text"]
    for page in pages
)

chunks = chunk_text(full_text)

print("\n📄 FIRST CHUNK:\n")

print(chunks[0])

print("\n📄 SECOND CHUNK:\n")

print(chunks[1])
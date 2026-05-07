from src.ingestion.extract_pdf import extract_text_from_pdf

# Change to your PDF path
pdf_path = "samle paper.pdf"

pages = extract_text_from_pdf(pdf_path)

print("\n✅ TOTAL PAGES:", len(pages))

print("\n📄 FIRST PAGE TEXT:\n")

print(pages[0]["text"][:3000])
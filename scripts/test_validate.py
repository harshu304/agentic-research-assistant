from src.ingestion.extract_pdf import extract_text_from_pdf
from src.ingestion.validate_paper import is_research_paper

pdf_path = "samle paper.pdf"

pages = extract_text_from_pdf(pdf_path)

full_text = "\n".join(
    page["text"]
    for page in pages
)

valid = is_research_paper(full_text)

print("\n✅ IS RESEARCH PAPER:", valid)
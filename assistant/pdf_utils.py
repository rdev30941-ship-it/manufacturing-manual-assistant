import fitz

def extract_text_from_pdf(pdf_path):
    pages = []
    with fitz.open(pdf_path) as doc:
        for page_index, page in enumerate(doc):
            text = page.get_text("text").strip()
            if text:
                pages.append({"page_number": page_index + 1, "text": text})
    return pages

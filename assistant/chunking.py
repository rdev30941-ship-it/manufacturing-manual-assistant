def chunk_pages(pages, machine_id, document_id, revision, chunk_size=1100, overlap=150):
    output = []
    for page in pages:
        text = page["text"]
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            piece = text[start:end].strip()
            if piece:
                output.append({
                    "machine_id": machine_id,
                    "document_id": document_id,
                    "revision": revision,
                    "page_number": page["page_number"],
                    "text": piece,
                })
            if end == len(text):
                break
            start = max(0, end - overlap)
    return output

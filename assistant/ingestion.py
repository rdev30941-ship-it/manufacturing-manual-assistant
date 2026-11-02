from django.db import transaction
from .models import DocumentChunk
from .pdf_utils import extract_text_from_pdf
from .chunking import chunk_pages

def ingest_manual(manual):
    pages = extract_text_from_pdf(manual.pdf_file.path)
    chunks = chunk_pages(pages, manual.machine.machine_id, manual.document_id, manual.revision)
    with transaction.atomic():
        DocumentChunk.objects.filter(manual=manual).delete()
        rows = [DocumentChunk(
            machine=manual.machine, manual=manual, document_id=c["document_id"],
            revision=c["revision"], page_number=c["page_number"], text=c["text"]
        ) for c in chunks]
        DocumentChunk.objects.bulk_create(rows)
    return len(rows)

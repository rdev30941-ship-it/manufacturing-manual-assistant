import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from .models import DocumentChunk

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def search_manuals(machine_id, question, top_k=5):
    # Filter in SQL BEFORE vectorization: cross-machine retrieval is impossible here.
    chunks = list(DocumentChunk.objects.filter(machine__machine_id=machine_id).select_related("machine").order_by("id"))
    if not chunks:
        return []
    model = get_model()
    vectors = np.asarray(model.encode([c.text for c in chunks], normalize_embeddings=True), dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    query = np.asarray(model.encode([question], normalize_embeddings=True), dtype="float32")
    scores, positions = index.search(query, min(top_k, len(chunks)))
    results = []
    seen = set()
    for score, pos in zip(scores[0], positions[0]):
        if pos < 0:
            continue
        c = chunks[int(pos)]
        identity = (c.document_id, c.page_number, c.text)
        if identity in seen:
            continue
        seen.add(identity)
        results.append({
            "score": float(score), "text": c.text, "machine_id": c.machine.machine_id,
            "document_id": c.document_id, "revision": c.revision, "page_number": c.page_number,
        })
    return results

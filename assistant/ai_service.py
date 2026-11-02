from django.conf import settings
from .retrieval import search_manuals
from .models import AIProviderConfig
from .crypto import decrypt_secret

INSUFFICIENT = "The selected machine's indexed manuals do not contain enough relevant evidence to answer this question."

def _provider_credentials():
    config = AIProviderConfig.objects.first()
    if config and config.enabled and config.encrypted_api_key:
        return decrypt_secret(config.encrypted_api_key), config.model
    if settings.USE_OPENAI and settings.OPENAI_API_KEY:
        return settings.OPENAI_API_KEY, settings.OPENAI_MODEL
    return None, None

def _optional_openai_answer(question, passages):
    # Optional and explicitly enabled only. The key stays server-side.
    api_key, model = _provider_credentials()
    if not api_key:
        return None
    import requests
    context = "\\n\\n".join(
        f"[{p['document_id']} rev {p['revision']} p.{p['page_number']}]\\n{p['text']}"
        for p in passages
    )
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "Answer only from the supplied manual passages. If they do not support an answer, say so. Cite document ID, revision and page for each claim. Do not use outside knowledge."},
                {"role": "user", "content": f"Question: {question}\\n\\nManual passages:\\n{context}"}
            ]
        },
        timeout=25,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate_answer(machine_id, question):
    results = search_manuals(machine_id, question, top_k=5)
    relevant = [r for r in results if r["score"] >= 0.30]
    if not relevant:
        return {"answer": INSUFFICIENT, "sources": [], "status": "insufficient"}
    try:
        llm_answer = _optional_openai_answer(question, relevant)
    except Exception:
        llm_answer = None
    if llm_answer:
        answer = llm_answer
    else:
        answer = "The following passages were retrieved from the selected machine's manuals. Review the cited evidence before taking action:\\n\\n" + "\\n\\n".join(r["text"] for r in relevant)
    sources = [{k: r[k] for k in ("document_id", "revision", "page_number", "text")} for r in relevant]
    return {"answer": answer, "sources": sources, "status": "answered"}

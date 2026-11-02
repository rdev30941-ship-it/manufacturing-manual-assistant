# ForgeAssist — Manufacturing Manual Assistant

A Django application for machine-scoped manual retrieval, evidence display, and question logging.

## Included
- Admin-managed machines and PDF manuals.
- PDF text extraction with PyMuPDF; one-based PDF page numbers.
- Chunking, Sentence Transformers embeddings and FAISS similarity search.
- SQL filtering by selected machine before vector retrieval.
- Evidence-only answer mode works without any API key.
- Optional OpenAI chat-completions integration (admin-configurable; disabled by default).
- Admin, Engineer and Supervisor groups.
- Question history and source metadata.
- Responsive dashboard and deployment configuration.

## Local setup (recommended Python 3.11–3.13)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```
Put the generated value after `DJANGO_SECRET_KEY=` in `.env`. Keep `.env` private.
```bash
python manage.py migrate
python manage.py setup_roles
python manage.py load_demo_data
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/ and sign in. Admin panel: http://127.0.0.1:8000/admin/

## First-time data setup
1. `load_demo_data` creates both challenge machines and registers/indexes the three bundled PDFs.
2. Add users in Admin and assign them to `Engineer` or `Supervisor` groups. Admins can be superusers or members of `Admin`.
3. New manual uploads through Django Admin are automatically extracted, chunked and indexed.

If the PDFs are already present in `media/manuals/`, create Manual records in Admin and select the matching file uploads. Do not use fictional training manuals to operate real equipment.

## Roles
- Admin: manage machines/manuals, configure optional AI provider.
- Engineer: ask questions; cannot upload manuals.
- Supervisor: review question history (read-only).
- Django superuser: full access.

## Optional OpenAI integration
The application defaults to evidence-only mode and does not need an API key.
An Admin can open **AI Setup**, paste an OpenAI key and model, then explicitly enable it. The key is encrypted in the database using a key derived from `DJANGO_SECRET_KEY`; keep that secret stable and private. Changing the Django secret makes existing encrypted keys unreadable. OpenAI requests are made server-side only. API usage can incur charges. Set up billing/keys only with an account authorized to do so.

## Deployment
A Render blueprint is provided in `render.yaml`. Provision a persistent disk for uploaded media if your hosting plan does not provide persistent storage, or use object storage for production uploads. Set environment variables securely in the hosting dashboard. Run migrations and create a superuser after deployment. Configure allowed hosts and HTTPS. For production, use managed PostgreSQL and persistent media storage.

## Important limitations
- The extractive fallback returns retrieved passages, not a generated maintenance procedure. It is deliberately conservative.
- Similarity scores are ranking signals, not proof of correctness. Tune the threshold with a labeled test set.
- PDF page citations use one-based original PDF page numbers.
- This project is a hackathon prototype, not validated for real-world industrial operation. Always follow approved site procedures and manufacturer documentation.

from pathlib import Path
from django.core.management.base import BaseCommand
from assistant.models import Machine, Manual
from assistant.ingestion import ingest_manual

MANUALS = [
    ("M-HP200", "HP-OPS-01", "HP-200 Operations Manual", "1.0", "HP200_Operations_Rev1_0.pdf"),
    ("M-HP200", "HP-MNT-01", "HP-200 Maintenance Manual", "1.0", "HP200_Maintenance_Rev1_0.pdf"),
    ("M-AC90", "AC-OM-01", "AC-90 Operations and Maintenance Manual", "1.0", "AC90_Operations_Maintenance_Rev1_0.pdf"),
]

class Command(BaseCommand):
    help = "Create the challenge machines and register/index the bundled sample manuals."
    def handle(self, *args, **options):
        hp, _ = Machine.objects.update_or_create(
            machine_id="M-HP200",
            defaults={"name":"Hydraulic forming press","model_number":"HP-200","manufacturer":""}
        )
        ac, _ = Machine.objects.update_or_create(
            machine_id="M-AC90",
            defaults={"name":"Air compressor","model_number":"AC-90","manufacturer":""}
        )
        machines = {"M-HP200": hp, "M-AC90": ac}
        media_root = Path("media/manuals")
        for machine_id, doc_id, title, revision, filename in MANUALS:
            file_path = media_root / filename
            if not file_path.exists():
                self.stderr.write(self.style.ERROR(f"Missing PDF: {file_path}"))
                continue
            manual, created = Manual.objects.update_or_create(
                document_id=doc_id,
                defaults={
                    "machine": machines[machine_id],
                    "title": title,
                    "revision": revision,
                    "pdf_file": f"manuals/{filename}",
                }
            )
            count = ingest_manual(manual)
            self.stdout.write(self.style.SUCCESS(f"{doc_id}: indexed {count} chunks"))
        self.stdout.write(self.style.SUCCESS("Demo data loaded. Create a superuser if you have not already."))

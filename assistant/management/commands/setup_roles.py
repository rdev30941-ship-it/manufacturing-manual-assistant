from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from assistant.models import Machine, Manual, QuestionLog

class Command(BaseCommand):
    help = "Create Admin, Engineer and Supervisor groups with baseline permissions."
    def handle(self, *args, **options):
        specs = {
            "Admin": ["add_machine", "change_machine", "delete_machine", "view_machine", "add_manual", "change_manual", "delete_manual", "view_manual", "view_questionlog"],
            "Engineer": ["view_machine", "view_manual", "add_questionlog", "view_questionlog"],
            "Supervisor": ["view_machine", "view_manual", "view_questionlog"],
        }
        models = {"machine": Machine, "manual": Manual, "questionlog": QuestionLog}
        for group_name, codenames in specs.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            perms = []
            for code in codenames:
                model_key = code.split("_", 1)[1]
                model = models[model_key]
                ct = ContentType.objects.get_for_model(model)
                perm = Permission.objects.filter(content_type=ct, codename=code).first()
                if perm:
                    perms.append(perm)
            group.permissions.set(perms)
            self.stdout.write(self.style.SUCCESS(f"Configured {group_name}"))

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("assistant", "0004_documentchunk"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="QuestionLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.TextField()),
                ("answer", models.TextField()),
                ("sources", models.JSONField(blank=True, default=list)),
                ("status", models.CharField(choices=[("answered", "Answered"), ("insufficient", "Insufficient evidence"), ("error", "Error")], max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("machine", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="assistant.machine")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="AIProviderConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(default="openai", max_length=40)),
                ("model", models.CharField(default="gpt-4o-mini", max_length=100)),
                ("encrypted_api_key", models.TextField(blank=True)),
                ("enabled", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]

from django.db import models
from django.conf import settings

class Machine(models.Model):
    name = models.CharField(max_length=200)
    machine_id = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    model_number = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.machine_id} — {self.name}"

class Manual(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="manuals")
    document_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    revision = models.CharField(max_length=50)
    pdf_file = models.FileField(upload_to="manuals/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.document_id} — {self.title}"

class DocumentChunk(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="chunks")
    manual = models.ForeignKey(Manual, on_delete=models.CASCADE, related_name="chunks")
    document_id = models.CharField(max_length=100)
    revision = models.CharField(max_length=50)
    page_number = models.PositiveIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.document_id} — Page {self.page_number}"

class QuestionLog(models.Model):
    STATUS_CHOICES = [("answered", "Answered"), ("insufficient", "Insufficient evidence"), ("error", "Error")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, null=True)
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.machine} — {self.created_at:%Y-%m-%d %H:%M}"

class AIProviderConfig(models.Model):
    """Stores an optional encrypted API key. The key is never returned to the browser."""
    provider = models.CharField(max_length=40, default="openai")
    model = models.CharField(max_length=100, default="gpt-4o-mini")
    encrypted_api_key = models.TextField(blank=True)
    enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.provider} ({'enabled' if self.enabled else 'fallback mode'})"

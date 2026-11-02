from django.contrib import admin
from .models import Machine, Manual, DocumentChunk, QuestionLog, AIProviderConfig
from .ingestion import ingest_manual

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("machine_id", "name", "model_number", "manufacturer")
    search_fields = ("machine_id", "name", "model_number")

@admin.register(Manual)
class ManualAdmin(admin.ModelAdmin):
    list_display = ("document_id", "title", "machine", "revision", "uploaded_at")
    list_filter = ("machine", "revision")
    search_fields = ("document_id", "title")
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            ingest_manual(obj)
            self.message_user(request, f"Manual indexed successfully: {obj.document_id}")
        except Exception as exc:
            self.message_user(request, f"Manual saved, but indexing failed: {exc}", level="ERROR")

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("document_id", "machine", "revision", "page_number")
    list_filter = ("machine", "document_id")

@admin.register(QuestionLog)
class QuestionLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "machine", "status")
    list_filter = ("status", "machine")
    readonly_fields = ("user", "machine", "question", "answer", "sources", "status", "created_at")

@admin.register(AIProviderConfig)
class AIProviderConfigAdmin(admin.ModelAdmin):
    list_display = ("provider", "model", "enabled", "updated_at")
    exclude = ("encrypted_api_key",)

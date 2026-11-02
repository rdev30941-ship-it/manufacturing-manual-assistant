import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Machine, QuestionLog, AIProviderConfig
from .ai_service import generate_answer
from .crypto import encrypt_secret, decrypt_secret

def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()

def is_supervisor(user):
    return user.is_superuser or user.groups.filter(name__in=["Admin", "Supervisor"]).exists()

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    error = ""
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            return redirect("dashboard")
        error = "Username or password is incorrect."
    return render(request, "assistant/login.html", {"error": error})

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    machines = Machine.objects.all().order_by("machine_id")
    recent = QuestionLog.objects.select_related("machine", "user").order_by("-created_at")[:6]
    return render(request, "assistant/home.html", {
        "machines": machines, "recent": recent,
        "can_manage": is_admin(request.user),
        "can_review": is_supervisor(request.user),
        "mode": "OpenAI enabled" if settings.USE_OPENAI and settings.OPENAI_API_KEY else "Evidence-only mode",
    })

@login_required
@require_POST
def ask_manual(request):
    machine_id = request.POST.get("machine_id", "").strip()
    question = request.POST.get("question", "").strip()
    if not machine_id or not question:
        return JsonResponse({"error": "Select a machine and enter a question."}, status=400)
    machine = get_object_or_404(Machine, machine_id=machine_id)
    try:
        result = generate_answer(machine.machine_id, question)
        QuestionLog.objects.create(
            user=request.user, machine=machine, question=question,
            answer=result["answer"], sources=result["sources"], status=result["status"]
        )
        return JsonResponse(result)
    except Exception as exc:
        QuestionLog.objects.create(user=request.user, machine=machine, question=question,
            answer="The search service encountered an error. Please retry.", sources=[], status="error")
        return JsonResponse({"error": "Search failed. Check that manuals are indexed and dependencies are installed."}, status=500)

@login_required
def history(request):
    if not is_supervisor(request.user):
        return HttpResponseForbidden("Supervisor or Admin access required.")
    logs = QuestionLog.objects.select_related("machine", "user").order_by("-created_at")[:200]
    return render(request, "assistant/history.html", {"logs": logs})

@login_required
def ai_settings(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admin access required.")
    config = AIProviderConfig.objects.first()
    notice = ""
    if request.method == "POST":
        provider = request.POST.get("provider", "openai")
        model = request.POST.get("model", "gpt-4o-mini").strip() or "gpt-4o-mini"
        key = request.POST.get("api_key", "").strip()
        enabled = request.POST.get("enabled") == "on"
        if not config:
            config = AIProviderConfig()
        config.provider = provider
        config.model = model
        if key:
            config.encrypted_api_key = encrypt_secret(key)
        config.enabled = enabled and bool(config.encrypted_api_key)
        config.save()
        notice = "Settings saved. The optional key is encrypted in the database and never displayed."
    has_key = bool(config and config.encrypted_api_key)
    return render(request, "assistant/ai_settings.html", {
        "config": config, "has_key": has_key, "notice": notice,
        "enabled": bool(config and config.enabled),
    })

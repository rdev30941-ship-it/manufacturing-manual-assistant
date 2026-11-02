from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from assistant import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("api/ask/", views.ask_manual, name="ask_manual"),
    path("history/", views.history, name="history"),
    path("settings/ai/", views.ai_settings, name="ai_settings"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

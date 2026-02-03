from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("transactions/", include("transactions.urls")),
    path("assistant/", include("assistant.urls")),
]

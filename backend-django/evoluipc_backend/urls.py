from django.contrib import admin
from django.urls import include, path

# Rotas raiz do projeto Django.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
]

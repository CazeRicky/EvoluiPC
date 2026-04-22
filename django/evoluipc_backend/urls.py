from django.urls import include, path

# Rotas raiz do projeto Django.
urlpatterns = [
    path("api/", include("core.urls")),
]

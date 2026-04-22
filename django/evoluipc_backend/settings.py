import os
from pathlib import Path

# Caminho base do projeto.
BASE_DIR = Path(__file__).resolve().parent.parent

# Flags e chave principal.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if host.strip()]

# Apps instalados no projeto.
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "core",
]

# Middlewares ativos da aplicacao.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "evoluipc_backend.urls"

# Configura templates HTML.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "evoluipc_backend.wsgi.application"

# Banco de dados desativado para manter a persistencia somente no Neo4j.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Recife"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuracoes de API DRF.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "core.neo4j_identity.Neo4jTokenAuthentication",
    ],
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Origens liberadas para CORS.
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "http://127.0.0.1:4173,http://localhost:4173,http://127.0.0.1:5500,http://localhost:5500").split(",")
    if origin.strip()
]

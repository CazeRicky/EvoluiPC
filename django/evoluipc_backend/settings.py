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

<<<<<<< HEAD:backend-django/evoluipc_backend/settings.py
# Banco de dados padrao.
=======
# Banco de dados desativado para manter a persistencia somente no Neo4j.
>>>>>>> 4c52f0495ecc34ce3be4d35d8c2e7ddd6dfd5379:django/evoluipc_backend/settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}

<<<<<<< HEAD:backend-django/evoluipc_backend/settings.py
# Regras de validacao de senha.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

=======
>>>>>>> 4c52f0495ecc34ce3be4d35d8c2e7ddd6dfd5379:django/evoluipc_backend/settings.py
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
<<<<<<< HEAD:backend-django/evoluipc_backend/settings.py
<<<<<<< HEAD
    for origin in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:5173,http://localhost:5173").split(",")
=======
    for origin in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "http://127.0.0.1:4173,http://localhost:4173,http://127.0.0.1:5500,http://localhost:5500").split(",")
>>>>>>> 9559f0a6af4f1787c2de574cace8515977d48d8e
=======
    for origin in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "http://127.0.0.1:4173,http://localhost:4173,http://127.0.0.1:5500,http://localhost:5500").split(",")
>>>>>>> 4c52f0495ecc34ce3be4d35d8c2e7ddd6dfd5379:django/evoluipc_backend/settings.py
    if origin.strip()
]

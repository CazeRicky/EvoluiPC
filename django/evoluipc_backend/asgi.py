# Expõe app ASGI do Django.
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoluipc_backend.settings")
# Objeto ASGI usado em deploy.
application = get_asgi_application()

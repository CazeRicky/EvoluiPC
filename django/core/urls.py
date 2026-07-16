from django.http import JsonResponse
from django.urls import path

from .views import (
    AuthMeView,
    LoginView,
    LogoutView,
    MachineCurrentView,
    ScanHistoryView,
    MachineSyncView,
    RecommendationView,
    RegisterView,
    upgrade_route_me,
    gpu_upgrade_route_me,
    list_cpus,
    list_gpus,
    gpu_compatibility,
    get_component_offers,
)

def home(request):
    return JsonResponse({"status": "ok", "service": "evoluipc-django"})

# Rotas publicas e autenticadas da API.
urlpatterns = [
    path("", home),
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/me", AuthMeView.as_view(), name="auth-me"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    
    path("machine/me", MachineCurrentView.as_view(), name="machine-me"),
    path("machine/history", ScanHistoryView.as_view(), name="machine-history"), 
    path("machine", MachineSyncView.as_view(), name="machine-sync-canonical"),
    path("machine/sync", MachineSyncView.as_view(), name="machine-sync"),
    path("upgrade-route/me", upgrade_route_me, name="upgrade-route-me"),
    path("upgrade-route/me/", upgrade_route_me, name="upgrade-route-me-slash"),
    path("upgrade-route/gpu", gpu_upgrade_route_me, name="upgrade-route-gpu"),
    path("upgrade-route/gpu/", gpu_upgrade_route_me, name="upgrade-route-gpu-slash"),
    path("recommendations/me", RecommendationView.as_view(), name="recommendations-me"),
    
    path("hardware/cpus", list_cpus, name="list-cpus"),
    path("hardware/gpus", list_gpus, name="list-gpus"),
    path("hardware/gpu/<str:gpu_name>/compatibility", gpu_compatibility, name="gpu-compatibility"),
    path("hardware/offers", get_component_offers, name="hardware-offers"),
]
from django.urls import path

from .views import (
    AuthMeView,
    LoginView,
    LogoutView,
    MachineCurrentView,
    MachineSyncView,
    RecommendationView,
    RegisterView,
    UpgradeRouteView,
)

# Rotas publicas e autenticadas da API.
urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/me", AuthMeView.as_view(), name="auth-me"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("machine/me", MachineCurrentView.as_view(), name="machine-me"),
    path("machine", MachineSyncView.as_view(), name="machine-sync-canonical"),
    path("machine/sync", MachineSyncView.as_view(), name="machine-sync"),
    path("upgrade-route/me", UpgradeRouteView.as_view(), name="upgrade-route-me"),
    path("recommendations/me", RecommendationView.as_view(), name="recommendations-me"),
]

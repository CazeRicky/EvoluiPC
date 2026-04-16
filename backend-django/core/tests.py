from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


# Testa fluxo principal de autenticacao e sync.
class AuthAndMachineFlowTests(APITestCase):
    def test_register_login_and_sync_flow(self):
        # Cadastra usuario e valida token.
        register_response = self.client.post(
            "/api/auth/register",
            {
                "username": "user_test",
                "email": "user@test.dev",
                "password": "12345678",
            },
            format="json",
        )
        self.assertEqual(register_response.status_code, 201)
        token = register_response.data["token"]

        # Sincroniza dados da maquina.
        sync_response = self.client.post(
            "/api/machine",
            {
                "schema_version": "1.0",
                "machine": {
                    "cpu": "Ryzen 5 5600",
                    "gpu": "RTX 3060",
                },
                "diagnostics": ["GPU equilibrada para Full HD"],
                "route": [{"step": "Upgrade 1", "action": "Mais RAM", "impact": "melhor estabilidade"}],
                "catalog": [{"name": "Kit 32GB DDR4", "price": "R$ 500"}],
                "source": "desktop-agent",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(sync_response.status_code, 200)
        self.assertEqual(sync_response.data["schema_version"], "1.0")

        # Busca snapshot atual salvo.
        machine_response = self.client.get(
            "/api/machine/me",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(machine_response.status_code, 200)
        self.assertEqual(machine_response.data["schema_version"], "1.0")
        self.assertEqual(machine_response.data["machine"]["cpu"], "Ryzen 5 5600")
        self.assertEqual(machine_response.data["diagnostics"], ["GPU equilibrada para Full HD"])
        self.assertEqual(machine_response.data["route"][0]["step"], "Upgrade 1")

        # Busca rota recomendada.
        route_response = self.client.get(
            "/api/upgrade-route/me",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(route_response.status_code, 200)
        self.assertEqual(route_response.data["schema_version"], "1.0")
        self.assertEqual(route_response.data["route"][0]["action"], "Mais RAM")

        # Busca catalogo recomendado.
        catalog_response = self.client.get(
            "/api/recommendations/me",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(catalog_response.status_code, 200)
        self.assertEqual(catalog_response.data["schema_version"], "1.0")
        self.assertEqual(catalog_response.data["catalog"][0]["name"], "Kit 32GB DDR4")

    def test_rejects_unsupported_schema_version(self):
        # Rejeita schema nao suportado.
        user = User.objects.create_user(username="schema_user", password="12345678")
        token = Token.objects.create(user=user)

        response = self.client.post(
            "/api/machine",
            {
                "schema_version": "2.0",
                "machine": {"cpu": "i7"},
            },
            format="json",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("supported_versions", response.data)

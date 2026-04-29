from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from .neo4j_identity import Neo4jUser
from .views import AuthMeView, LoginView, LogoutView, MachineCurrentView, MachineSyncView, RecommendationView, RegisterView, UpgradeRouteView


class Neo4jIdentityFlowTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("core.views.ensure_user_identity")
    @patch("core.views.upsert_user_profile")
    @patch("core.views.assign_random_pc_to_user")
    @patch("core.views.ensure_user_node")
    def test_register_returns_neo4j_identity(self, ensure_user_node_mock, assign_random_pc_to_user_mock, upsert_user_profile_mock, ensure_user_identity_mock):
        ensure_user_identity_mock.return_value = {
            "id": "user-1",
            "username": "user_test",
            "email": "user@test.dev",
            "token": "token-1",
        }
        assign_random_pc_to_user_mock.return_value = None
        upsert_user_profile_mock.return_value = {"profile": {}, "source": "web-register", "event_type": "register", "updated_at": "now"}

        request = self.factory.post(
            "/api/auth/register",
            {"username": "user_test", "email": "user@test.dev", "password": "12345678"},
            format="json",
        )
        response = RegisterView.as_view()(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["id"], "user-1")
        self.assertEqual(response.data["token"], "token-1")

    @patch("core.views.authenticate_identity")
    @patch("core.views.upsert_user_profile")
    def test_login_returns_neo4j_token(self, upsert_user_profile_mock, authenticate_identity_mock):
        authenticate_identity_mock.return_value = {
            "id": "user-1",
            "username": "user_test",
            "email": "user@test.dev",
            "token": "token-2",
        }
        upsert_user_profile_mock.return_value = {"profile": {}, "source": "web-login", "event_type": "login", "updated_at": "now"}

        request = self.factory.post(
            "/api/auth/login",
            {"username": "user_test", "password": "12345678"},
            format="json",
        )
        response = LoginView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["token"], "token-2")

    @patch("core.views.get_user_pc_parts", return_value=None)
    def test_new_user_gets_empty_machine_state(self, _mock):
        request = self.factory.get("/api/machine/me")
        request.user = Neo4jUser(id="user-1", username="user_test", email="user@test.dev")
        response = MachineCurrentView().get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["source"], "neo4j-empty")
        self.assertTrue(response.data["is_new_user"])

    @patch("core.views.get_user_profile", return_value={"profile": {"registration": {"username": "user_test"}}, "source": "web-register"})
    def test_auth_me_includes_profile(self, _mock_profile):
        request = self.factory.get("/api/auth/me")
        request.user = Neo4jUser(id="user-1", username="user_test", email="user@test.dev")
        response = AuthMeView().get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["registration"]["username"], "user_test")

    @patch("core.views.revoke_token")
    def test_logout_calls_neo4j_token_revoke(self, revoke_token_mock):
        request = self.factory.post("/api/auth/logout")
        request.user = Neo4jUser(id="user-1", username="user_test", email="user@test.dev")
        request.auth = "token-1"
        response = LogoutView().post(request)

        self.assertEqual(response.status_code, 200)
        revoke_token_mock.assert_called_once_with("token-1")

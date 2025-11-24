import os
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import UserOperations
from madlibs.models import MadLibTemplate, UserFilledMadlibs


class MadLibsIntegrationTest(TestCase):
    """Full database + API integration test for templates & filled madlibs"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.skip_integration = os.getenv('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true'

        if cls.skip_integration:
            print("\n==== SKIPPING MADLIBS INTEGRATION TESTS ====")

    def setUp(self):
        if self.skip_integration:
            self.skipTest("Integration tests disabled. Set SKIP_INTEGRATION_TESTS=false to enable.")

        self.client = APIClient()

        # real DB services
        self.template_service = MadLibTemplate()
        self.madlib_service = UserFilledMadlibs()
        self.user_service = UserOperations()

        # create real user in MongoDB
        self.mongo_user_id = self.user_service.create(
            username="int_test_user",
            email="int@test.com",
            oauth_provider="google",
            oauth_id="oauth_12345"
        )

        # create Django auth user for API auth
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.auth_user = User.objects.create_user(
            username="auth_api_user",
            password="pass123",
            email="auth@test.com"
        )

        # authenticate API calls
        self.client.force_authenticate(user=self.auth_user)

        # create template
        self.template_id = self.template_service.create({
            "title": "Test Adventure",
            "story": "The {adjective} {noun} went to {place}",
            "blanks": [
                {"id": "1", "placeholder": "adjective", "type": "adjective"},
                {"id": "2", "placeholder": "noun", "type": "noun"},
                {"id": "3", "placeholder": "place", "type": "location"}
            ]
        })

    def tearDown(self):
        if not self.skip_integration:
            if hasattr(self, "madlib_id"):
                self.madlib_service.delete_filled_madlib(self.madlib_id)

            if hasattr(self, "template_id"):
                self.template_service.delete(self.template_id)

            if hasattr(self, "mongo_user_id"):
                self.user_service.delete(self.mongo_user_id)

    # ---------------- TEMPLATE TESTS ---------------- #

    def test_list_templates(self):
        resp = self.client.get("/api/templates/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data["count"], 1)

    def test_retrieve_template(self):
        resp = self.client.get(f"/api/templates/{self.template_id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["title"], "Test Adventure")

    def test_search_template(self):
        resp = self.client.get("/api/templates/search/?title=adventure")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data["count"], 1)

    # ---------------- FILLED MADLIB TESTS ---------------- #

    def test_create_filled_madlib(self):
        payload = {
            "template_id": self.template_id,
            "creator_id": self.mongo_user_id,
            "inputted_blanks": [
                {"id": "1", "input": "brave"},
                {"id": "2", "input": "dragon"},
                {"id": "3", "input": "Disneyland"}
            ]
        }

        resp = self.client.post("/api/madlibs/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self.madlib_id = resp.data["id"]

    def test_retrieve_filled_madlib(self):
        # create first
        self.test_create_filled_madlib()

        resp = self.client.get(f"/api/madlibs/{self.madlib_id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["content"]), 3)

    def test_update_filled_madlib(self):
        self.test_create_filled_madlib()

        payload = {
            "inputted_blanks": [
                {"id": "1", "input": "sleepy"},
                {"id": "2", "input": "cat"},
                {"id": "3", "input": "Paris"}
            ]
        }

        resp = self.client.put(f"/api/madlibs/{self.madlib_id}/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        updated = self.madlib_service.get_by_id(self.madlib_id)
        self.assertEqual(updated["content"][0]["input"], "sleepy")

    def test_delete_filled_madlib(self):
        self.test_create_filled_madlib()

        resp = self.client.delete(f"/api/madlibs/{self.madlib_id}/")
        self.assertIn(resp.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])

    def test_get_by_creator(self):
        self.test_create_filled_madlib()

        resp = self.client.get(f"/api/madlibs/by_creator/?creator_id={self.mongo_user_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)

from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient


class SummarizeMockTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(OPENAI_API_KEY="")
    def test_mock_summary(self):
        # Objective: when no API key is set, a deterministic mock summary is returned.
        # Expected: response is 200 and contains the first two sentences.
        text = "Sentence one. Sentence two. Sentence three."
        res = self.client.post("/assistant/summarize", {"text": text}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Sentence one.", res.data["summary"])
        self.assertIn("Sentence two.", res.data["summary"])

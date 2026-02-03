from django.test import TestCase
from rest_framework.test import APIClient


class TransactionIdempotencyTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_idempotent_create(self):
        # Objective: same idempotency key + same payload returns the same transaction.
        # Expected: same ID across requests.
        payload = {"type": "credit", "amount": "10.00"}
        res1 = self.client.post("/transactions/create", payload, format="json", HTTP_IDEMPOTENCY_KEY="abc")
        self.assertEqual(res1.status_code, 201)
        res2 = self.client.post("/transactions/create", payload, format="json", HTTP_IDEMPOTENCY_KEY="abc")
        self.assertEqual(res2.status_code, 201)
        self.assertEqual(res1.data["id"], res2.data["id"])

    def test_idempotency_payload_mismatch(self):
        # Objective: reusing a key with different payloads is rejected.
        # Expected: conflict (409).
        payload1 = {"type": "credit", "amount": "10.00"}
        payload2 = {"type": "debit", "amount": "10.00"}
        res1 = self.client.post("/transactions/create", payload1, format="json", HTTP_IDEMPOTENCY_KEY="xyz")
        self.assertEqual(res1.status_code, 201)
        res2 = self.client.post("/transactions/create", payload2, format="json", HTTP_IDEMPOTENCY_KEY="xyz")
        self.assertEqual(res2.status_code, 409)

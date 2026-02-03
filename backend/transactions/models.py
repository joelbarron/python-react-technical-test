from __future__ import annotations

import uuid
from django.db import models


class Transaction(models.Model):
    class Type(models.TextChoices):
        CREDIT = "credit", "credit"
        DEBIT = "debit", "debit"

    class Status(models.TextChoices):
        CREATED = "created", "created"
        PENDING = "pending", "pending"
        PROCESSED = "processed", "processed"
        FAILED = "failed", "failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.CREATED)

    idempotency_key = models.CharField(max_length=128, unique=True, null=True, blank=True)
    client_request_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    request_hash = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.id} {self.type} {self.amount} {self.status}"

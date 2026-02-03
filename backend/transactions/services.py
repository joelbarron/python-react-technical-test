from __future__ import annotations

import hashlib
import logging
from typing import Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import IntegrityError, transaction as db_transaction

from .models import Transaction

logger = logging.getLogger(__name__)


class IdempotencyError(ValueError):
    pass


class MissingIdempotencyError(ValueError):
    pass


def _hash_payload(tx_type: str, amount: str) -> str:
    raw = f"{tx_type}:{amount}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def create_transaction(*, tx_type: str, amount: str, idempotency_key: Optional[str], client_request_id: Optional[str]) -> Transaction:
    if not idempotency_key and not client_request_id:
        raise MissingIdempotencyError("Idempotency-Key header or client_request_id is required")

    # Hash the input so we can reject accidental reuse with different payloads.
    request_hash = _hash_payload(tx_type, amount)

    lookup = {}
    if idempotency_key:
        lookup["idempotency_key"] = idempotency_key
    else:
        lookup["client_request_id"] = client_request_id

    existing = _find_existing(lookup)
    if existing:
        _assert_same_payload(existing, request_hash)
        return existing

    try:
        with db_transaction.atomic():
            # Unique constraint enforces idempotency under concurrency.
            return Transaction.objects.create(
                type=tx_type,
                amount=amount,
                idempotency_key=idempotency_key,
                client_request_id=client_request_id,
                request_hash=request_hash,
            )
    except IntegrityError:
        existing = _find_existing(lookup)
        if existing:
            _assert_same_payload(existing, request_hash)
            return existing
        raise


def _find_existing(lookup: dict) -> Optional[Transaction]:
    if not lookup:
        return None
    return Transaction.objects.filter(**lookup).first()


def _assert_same_payload(existing: Transaction, request_hash: str) -> None:
    if existing.request_hash != request_hash:
        raise IdempotencyError("Idempotency key reused with different payload")


def enqueue_processing(transaction_id: str) -> None:
    from .tasks import process_transaction_task

    process_transaction_task.delay(transaction_id)


def broadcast_transaction_update(transaction: Transaction) -> None:
    channel_layer = get_channel_layer()
    if not channel_layer:
        logger.warning("Channel layer not configured")
        return
    payload = {
        "type": "transaction_updated",
        "data": {
            "id": str(transaction.id),
            "type": transaction.type,
            "amount": str(transaction.amount),
            "status": transaction.status,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat(),
        },
    }
    async_to_sync(channel_layer.group_send)("transactions", payload)

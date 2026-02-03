from __future__ import annotations

import logging
import random
import time

from celery import shared_task
from django.db import transaction as db_transaction

from .models import Transaction
from .services import broadcast_transaction_update

logger = logging.getLogger(__name__)


@shared_task
def process_transaction_task(transaction_id: str) -> None:
    # Mark as pending immediately so clients see progress.
    with db_transaction.atomic():
        tx = Transaction.objects.select_for_update().filter(id=transaction_id).first()
        if not tx:
            logger.warning("Transaction %s not found", transaction_id)
            return
        tx.status = Transaction.Status.PENDING
        tx.save(update_fields=["status", "updated_at"])

    broadcast_transaction_update(tx)

    time.sleep(random.uniform(2, 5))

    with db_transaction.atomic():
        tx = Transaction.objects.select_for_update().filter(id=transaction_id).first()
        if not tx:
            logger.warning("Transaction %s not found", transaction_id)
            return
        # Demo: mostly processed, sometimes failed.
        tx.status = Transaction.Status.PROCESSED if random.random() > 0.2 else Transaction.Status.FAILED
        tx.save(update_fields=["status", "updated_at"])

    broadcast_transaction_update(tx)

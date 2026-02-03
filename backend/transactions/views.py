from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import (
    TransactionAsyncProcessSerializer,
    TransactionCreateSerializer,
    TransactionSerializer,
)
from .services import IdempotencyError, MissingIdempotencyError, create_transaction, enqueue_processing

logger = logging.getLogger(__name__)


class TransactionCreateView(APIView):
    def post(self, request):
        serializer = TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idempotency_key = request.headers.get("Idempotency-Key")
        client_request_id = serializer.validated_data.get("client_request_id")

        try:
            # Service layer owns idempotency logic.
            tx = create_transaction(
                tx_type=serializer.validated_data["type"],
                amount=str(serializer.validated_data["amount"]),
                idempotency_key=idempotency_key,
                client_request_id=client_request_id,
            )
        except MissingIdempotencyError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except IdempotencyError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)


class TransactionAsyncProcessView(APIView):
    def post(self, request):
        serializer = TransactionAsyncProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enqueue_processing(str(serializer.validated_data["transaction_id"]))
        return Response({"status": "queued"}, status=status.HTTP_202_ACCEPTED)


class TransactionListView(APIView):
    def get(self, request):
        queryset = Transaction.objects.order_by("-created_at")[:50]
        data = TransactionSerializer(queryset, many=True).data
        return Response(data)

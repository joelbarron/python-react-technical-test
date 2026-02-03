from __future__ import annotations

from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "type",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]


class TransactionCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=Transaction.Type.choices)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    client_request_id = serializers.CharField(required=False, allow_blank=False)


class TransactionAsyncProcessSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()

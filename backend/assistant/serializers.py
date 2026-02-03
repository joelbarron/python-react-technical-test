from __future__ import annotations

from rest_framework import serializers

from .models import SummarizationLog


class SummarizeRequestSerializer(serializers.Serializer):
    text = serializers.CharField()


class SummarizeResponseSerializer(serializers.Serializer):
    summary = serializers.CharField()


class SummarizationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummarizationLog
        fields = ["id", "text", "summary", "created_at"]

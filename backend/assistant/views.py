from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SummarizeRequestSerializer, SummarizeResponseSerializer
from .services import log_summary, summarize_text


class SummarizeView(APIView):
    def post(self, request):
        serializer = SummarizeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data["text"]
        summary = summarize_text(text)
        log_summary(text, summary)
        return Response(SummarizeResponseSerializer({"summary": summary}).data, status=status.HTTP_200_OK)

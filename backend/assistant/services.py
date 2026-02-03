from __future__ import annotations

import re

import logging
import requests
from django.conf import settings

from .models import SummarizationLog

logger = logging.getLogger(__name__)


def summarize_text(text: str) -> str:
    if settings.OPENAI_API_KEY:
        try:
            return _openai_summary(text)
        except Exception as exc:
            logger.warning("OpenAI request failed; using mock summary. Reason: %s", exc)
            return _mock_summary(text)
    return _mock_summary(text)


def _mock_summary(text: str) -> str:
    # Simple heuristic: first 1-2 sentences + ellipsis if trimmed.
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    summary = " ".join(sentences[:2])
    if len(summary) < len(cleaned):
        summary = f"{summary} ..."
    return summary


def _openai_summary(text: str) -> str:
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {
                "role": "developer",
                "content": "Summarize the input in 1-2 concise sentences. Preserve key facts. Return plain text only.",
            },
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    res = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=20)
    res.raise_for_status()
    data = res.json()
    return data["choices"][0]["message"]["content"].strip()


def log_summary(text: str, summary: str) -> SummarizationLog:
    return SummarizationLog.objects.create(text=text, summary=summary)

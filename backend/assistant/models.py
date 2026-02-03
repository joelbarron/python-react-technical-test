from __future__ import annotations

from django.db import models


class SummarizationLog(models.Model):
    text = models.TextField()
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Summary {self.id}"

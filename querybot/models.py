"""Models for querybot."""
from uuid import uuid4
from django.db import models


class Query(models.Model):
    """A single entry on the FAQ Page."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    question = models.TextField(blank=False)
    answer = models.TextField(blank=False)
    category = models.CharField(max_length=30, blank=False)
    sub_category = models.CharField(max_length=30, blank=True)
    sub_sub_category = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "Query"
        verbose_name_plural = "Queries"


class UnresolvedQuery(models.Model):
    """New question asked by someone."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    question = models.TextField(blank=False)
    category = models.CharField(max_length=30, blank=True)
    user = models.ForeignKey(
        "users.UserProfile", null=False, on_delete=models.CASCADE, related_name="Query"
    )
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "UnresolvedQuery"
        verbose_name_plural = "UnresolvedQueries"


class ChatBotLog(models.Model):
    """Reaction to an answer by chatbot"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    question = models.TextField(blank=False)
    answer = models.TextField(blank=True)
    reaction = models.IntegerField()

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "ChatBotLog"
        verbose_name_plural = "ChatBotLogs"

from django.db import models
from uuid import uuid4

# Create your models here.


BAN_REASON_CHOICHES = [
    ("IDF", "Unappropriate Comment"),
    ("Buy&Sell", "Unappropriate Activity in Buy and Sell"),
    ("Graduated ", "Passed out from Institute"),
    ("InstiBan", "Banned by Insittute Authority"),
]

BAN_DURATION_CHOICES = [
    ("1 month", "One Month"),
    ("3 months", "Three Months"),
    ("6 months", "Six Months"),
    ("12 months", "Twelve Months"),
    ("Permanent", "Permanent"),
]


class SSOBan(models.Model):
    """Bans imposed on students to access any SSO required View."""

    id = models.UUIDField(primary_key=True, default=uuid4, blank=False)
    banned_user = models.ForeignKey(
        to="users.UserProfile", related_name="banned_user", on_delete=models.CASCADE
    )
    time_of_creation = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=30, choices=BAN_REASON_CHOICHES)
    detailed_reason = models.TextField(blank=True)
    duration_of_ban = models.CharField(max_length=20, choices=BAN_DURATION_CHOICES)
    banned_by = models.ForeignKey(
        to="users.UserProfile",
        related_name="banned_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

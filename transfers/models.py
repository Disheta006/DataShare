# Create your models here.

from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL

class Transfer(models.Model):

    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    sender = models.ForeignKey(User, related_name="sent_transfers", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_transfers", on_delete=models.CASCADE)

    amount = models.IntegerField()  # in MB

    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.amount}MB)"
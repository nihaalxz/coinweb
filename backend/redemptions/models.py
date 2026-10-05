import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from wallets.models import Wallet

def mask_payout_identifier(identifier: str, method: str) -> str:
    if not identifier:
        return ""
    identifier = identifier.strip()
    if method == 'UPI' and '@' in identifier:
        parts = identifier.split('@')
        handle, provider = parts[0], parts[1]
        if len(handle) <= 2:
            masked_handle = handle + '***'
        else:
            masked_handle = handle[:2] + '*' * (len(handle) - 2)
        return f"{masked_handle}@{provider}"
    else:
        # Bank account or general string: show only last 4 chars
        if len(identifier) <= 4:
            return '****'
        return '*' * (len(identifier) - 4) + identifier[-4:]

class Redemption(models.Model):
    class PayoutMethod(models.TextChoices):
        UPI = 'UPI', 'UPI'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'

    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    redemption_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='redemptions'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name='redemptions'
    )
    coins_deducted = models.PositiveIntegerField()
    inr_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    payout_method = models.CharField(
        max_length=20,
        choices=PayoutMethod.choices,
        default=PayoutMethod.UPI,
        db_index=True
    )
    payout_identifier = models.CharField(max_length=255)
    masked_identifier = models.CharField(max_length=255, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True
    )
    utr_number = models.CharField(max_length=100, blank=True, db_index=True)
    admin_notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    requested_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'requested_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.masked_identifier and self.payout_identifier:
            self.masked_identifier = mask_payout_identifier(self.payout_identifier, self.payout_method)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Redemption({self.redemption_id}: {self.coins_deducted} coins -> ₹{self.inr_amount} [{self.status}])"

class RedemptionStatusHistory(models.Model):
    redemption = models.ForeignKey(
        Redemption,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

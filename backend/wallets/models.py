import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Wallet(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    coin_balance = models.BigIntegerField(default=0, db_index=True)
    lifetime_earned = models.BigIntegerField(default=0)
    lifetime_redeemed = models.BigIntegerField(default=0)
    is_locked = models.BooleanField(default=False, db_index=True)
    lock_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Wallet({self.user.email}) - {self.coin_balance} Coins"

class WalletTransaction(models.Model):
    class Type(models.TextChoices):
        CASHBACK = 'CASHBACK', 'Cashback'
        REFERRAL_BONUS = 'REFERRAL_BONUS', 'Referral Bonus'
        PROMOTIONAL_BONUS = 'PROMOTIONAL_BONUS', 'Promotional Bonus'
        MANUAL_CREDIT = 'MANUAL_CREDIT', 'Manual Credit'
        MANUAL_DEBIT = 'MANUAL_DEBIT', 'Manual Debit'
        REDEMPTION = 'REDEMPTION', 'Redemption'
        REVERSAL = 'REVERSAL', 'Reversal'
        REFUND = 'REFUND', 'Refund'
        ADMIN_ADJUSTMENT = 'ADMIN_ADJUSTMENT', 'Admin Adjustment'

    class Status(models.TextChoices):
        COMPLETED = 'COMPLETED', 'Completed'
        PENDING = 'PENDING', 'Pending'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    tx_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=40,
        choices=Type.choices,
        db_index=True
    )
    # Always a positive integer representing the magnitude of coin delta
    amount_coins = models.PositiveIntegerField()
    balance_before = models.BigIntegerField()
    balance_after = models.BigIntegerField()
    inr_equivalent = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
        db_index=True
    )
    
    reference_type = models.CharField(max_length=50, blank=True, db_index=True)
    reference_id = models.CharField(max_length=100, blank=True, db_index=True)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authorized_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'created_at']),
            models.Index(fields=['reference_type', 'reference_id']),
            models.Index(fields=['transaction_type', 'status']),
        ]

    def __str__(self):
        return f"[{self.tx_id}] {self.transaction_type} {self.amount_coins} coins (Wallet #{self.wallet_id})"

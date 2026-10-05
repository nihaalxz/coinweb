from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from merchants.models import Merchant
from affiliate.models import AffiliateClick

class Cashback(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        REVERSED = 'REVERSED', 'Reversed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cashbacks'
    )
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.PROTECT,
        related_name='cashbacks'
    )
    affiliate_click = models.ForeignKey(
        AffiliateClick,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cashbacks'
    )
    order_id = models.CharField(max_length=150, db_index=True)
    order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cashback_inr = models.DecimalField(max_digits=12, decimal_places=2)
    cbk_coins = models.PositiveIntegerField(db_index=True)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    rejection_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['merchant', 'order_id']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Cashback({self.user.email} - {self.merchant.name} #{self.order_id}: {self.cbk_coins} Coins [{self.status}])"

class CashbackStatusHistory(models.Model):
    cashback = models.ForeignKey(
        Cashback,
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

    def __str__(self):
        return f"Cashback #{self.cashback_id}: {self.previous_status} -> {self.new_status}"

import uuid
from django.db import models
from django.conf import settings
from merchants.models import Merchant

class AffiliateClick(models.Model):
    class Status(models.TextChoices):
        CLICKED = 'CLICKED', 'Clicked'
        CONVERTED = 'CONVERTED', 'Converted'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REVERSED = 'REVERSED', 'Reversed'

    click_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='affiliate_clicks'
    )
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name='affiliate_clicks'
    )
    source = models.CharField(max_length=100, blank=True, default='web')
    campaign = models.CharField(max_length=100, blank=True)
    sub_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    product_title = models.CharField(max_length=255, blank=True)
    product_url = models.URLField(max_length=1500, blank=True)
    estimated_coins = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CLICKED,
        db_index=True
    )
    redirect_url = models.URLField(max_length=1500)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['merchant', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        user_label = self.user.email if self.user else "Guest"
        return f"[{self.click_id}] {self.merchant.name} by {user_label} ({self.status})"

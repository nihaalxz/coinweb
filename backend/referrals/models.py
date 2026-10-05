from django.db import models
from django.conf import settings

class Referral(models.Model):
    class Status(models.TextChoices):
        REGISTERED = 'REGISTERED', 'Registered'
        QUALIFIED = 'QUALIFIED', 'Qualified'
        REWARDED = 'REWARDED', 'Rewarded'

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referrals_made'
    )
    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral_received'
    )
    referral_code_used = models.CharField(max_length=20, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTERED,
        db_index=True
    )
    reward_coins = models.PositiveIntegerField(default=100)
    qualified_at = models.DateTimeField(null=True, blank=True)
    rewarded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['referrer', 'status']),
        ]

    def __str__(self):
        return f"Referral({self.referrer.email} -> {self.referred_user.email} [{self.status}])"

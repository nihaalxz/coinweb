from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from core.models import TimeStampedModel

class Promotion(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    description = models.TextField(blank=True)
    bonus_coins = models.PositiveIntegerField(default=0)
    cashback_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True, db_index=True)
    usage_limit = models.PositiveIntegerField(default=0, help_text="0 means unlimited")
    usage_count = models.PositiveIntegerField(default=0)
    banner_url = models.URLField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_currently_running(self):
        now = timezone.now()
        return self.is_active and (self.start_date <= now <= self.end_date)

    def __str__(self):
        return f"{self.title} ({self.cashback_multiplier}x, +{self.bonus_coins} coins)"

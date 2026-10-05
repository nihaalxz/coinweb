from django.db import models
from django.utils.text import slugify
from core.models import TimeStampedModel

class Merchant(TimeStampedModel):
    class Category(models.TextChoices):
        MARKETPLACES = 'marketplaces', 'Marketplaces'
        FASHION = 'fashion', 'Fashion'
        ELECTRONICS = 'electronics', 'Electronics'
        TRAVEL = 'travel', 'Travel'
        BEAUTY = 'beauty', 'Beauty'
        GROCERY = 'grocery', 'Grocery'
        OTHER = 'other', 'Other'

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    logo_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.MARKETPLACES,
        db_index=True
    )
    website_url = models.URLField()
    affiliate_network = models.CharField(max_length=100, blank=True)
    affiliate_url_template = models.TextField(
        blank=True,
        help_text="URL template supporting {click_id}, {user_id}, {merchant_slug}"
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="CBK merchant commission % (e.g. 10.00)"
    )
    cbk_reward_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=8.00,
        help_text="Customer cashback reward % (e.g. 8.00)"
    )
    reward_badge = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'category']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.cbk_reward_rate}% Cashback)"

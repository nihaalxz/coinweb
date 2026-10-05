import math
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from django.db import models
from django.utils.text import slugify
from core.models import TimeStampedModel
from merchants.models import Merchant

class Product(TimeStampedModel):
    class Category(models.TextChoices):
        MOBILES = 'mobiles', 'Mobiles & Tablets'
        ELECTRONICS = 'electronics', 'Electronics & Gadgets'
        FASHION = 'fashion', 'Fashion & Apparel'
        HOME_KITCHEN = 'home_kitchen', 'Home & Kitchen'
        BEAUTY = 'beauty', 'Beauty & Personal Care'
        APPLIANCES = 'appliances', 'Appliances'
        OTHER = 'other', 'Other'

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    external_id = models.CharField(max_length=100, blank=True, help_text="Store product ID / ASIN / FSN")
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.ELECTRONICS,
        db_index=True
    )
    image_url = models.URLField(max_length=1000)
    target_url = models.URLField(max_length=1500, help_text="Original destination URL on merchant site")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Current sale price in INR")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Original MRP before discount")
    discount_percent = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    review_count = models.PositiveIntegerField(default=100)
    deal_badge = models.CharField(max_length=50, blank=True, default='DEAL')
    coin_reward_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custom coin cashback % override for this product. If empty, uses merchant's reward rate."
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_deal_of_the_day = models.BooleanField(default=False, db_index=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'merchant']),
            models.Index(fields=['is_active', 'category']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['is_active', 'is_deal_of_the_day']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:250]
        # Calculate discount percent if not set
        if self.original_price and self.original_price > self.price and not self.discount_percent:
            calc_discount = ((self.original_price - self.price) / self.original_price) * 100
            self.discount_percent = int(round(calc_discount))
        super().save(*args, **kwargs)

    @property
    def effective_reward_rate(self):
        """Returns the coin cashback percentage."""
        if self.coin_reward_rate is not None:
            return self.coin_reward_rate
        return self.merchant.cbk_reward_rate

    @property
    def coins_earned(self):
        """Coins earned upon purchasing this product (1 coin = ₹1 cashback value)."""
        rate = float(self.effective_reward_rate)
        amt = float(self.price)
        coins = math.floor((amt * rate) / 100.0)
        return max(coins, 1)

    def build_affiliate_url(self, click_id: str, user_id: str = "guest") -> str:
        """
        Builds the tracked affiliate link pointing to this specific product.
        Applies network-specific sub-IDs and tracking tags (like Amazon ascsubtag, Flipkart affExtParam1, Meesho tracking).
        """
        base_url = self.target_url.strip() or self.merchant.website_url.strip()
        parsed = urlparse(base_url)
        query = dict(parse_qsl(parsed.query))
        hostname = (parsed.netloc or '').lower()

        # Merchant specific affiliate parameters
        if 'amazon.' in hostname or self.merchant.slug.startswith('amazon'):
            query['tag'] = 'coinweb-21'
            query['ascsubtag'] = str(click_id)
            query['linkCode'] = 'll1'
        elif 'flipkart.' in hostname or self.merchant.slug.startswith('flipkart'):
            query['affid'] = 'coinweb'
            query['affExtParam1'] = str(click_id)
            query['affExtParam2'] = str(user_id)
        elif 'meesho.' in hostname or self.merchant.slug.startswith('meesho'):
            query['cbk_click'] = str(click_id)
            query['cbk_sub'] = str(user_id)
            query['utm_source'] = 'coinweb_cashback'
            query['utm_campaign'] = 'deal_redirect'
        else:
            query['cbk_click'] = str(click_id)
            query['cbk_sub'] = str(user_id)

        parts = list(parsed)
        parts[4] = urlencode(query)
        return urlunparse(parts)

    def __str__(self):
        return f"{self.name} [{self.merchant.name}] - ₹{self.price} ({self.coins_earned} coins)"

from rest_framework import serializers
from .models import Product
from merchants.models import Merchant

class ProductMerchantSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['id', 'name', 'slug', 'category', 'logo_url', 'cbk_reward_rate']

class ProductPublicSerializer(serializers.ModelSerializer):
    merchant = ProductMerchantSummarySerializer(read_only=True)
    merchant_name = serializers.ReadOnlyField(source='merchant.name')
    merchant_slug = serializers.ReadOnlyField(source='merchant.slug')
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    effective_reward_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    coins_earned = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'external_id',
            'merchant',
            'merchant_name',
            'merchant_slug',
            'category',
            'category_display',
            'image_url',
            'target_url',
            'price',
            'original_price',
            'discount_percent',
            'rating',
            'review_count',
            'deal_badge',
            'effective_reward_rate',
            'coins_earned',
            'is_featured',
            'is_deal_of_the_day',
            'created_at',
        ]

class ProductAdminSerializer(serializers.ModelSerializer):
    effective_reward_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    coins_earned = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

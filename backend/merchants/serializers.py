from rest_framework import serializers
from .models import Merchant

class MerchantPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = [
            'id',
            'name',
            'slug',
            'logo_url',
            'description',
            'category',
            'website_url',
            'cbk_reward_rate',
            'reward_badge',
            'is_featured',
        ]

class MerchantAdminSerializer(serializers.ModelSerializer):
    clicks_count = serializers.SerializerMethodField()
    conversions_count = serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        fields = [
            'id',
            'name',
            'slug',
            'logo_url',
            'description',
            'category',
            'website_url',
            'affiliate_network',
            'affiliate_url_template',
            'commission_rate',
            'cbk_reward_rate',
            'reward_badge',
            'is_active',
            'is_featured',
            'display_order',
            'created_at',
            'updated_at',
            'clicks_count',
            'conversions_count',
        ]
        read_only_fields = ['created_at', 'updated_at', 'clicks_count', 'conversions_count']

    def get_clicks_count(self, obj):
        return obj.affiliate_clicks.count() if hasattr(obj, 'affiliate_clicks') else 0

    def get_conversions_count(self, obj):
        return obj.cashbacks.count() if hasattr(obj, 'cashbacks') else 0

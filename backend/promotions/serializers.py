from rest_framework import serializers
from .models import Promotion

class PromotionPublicSerializer(serializers.ModelSerializer):
    is_running = serializers.BooleanField(source='is_currently_running', read_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'bonus_coins',
            'cashback_multiplier',
            'start_date',
            'end_date',
            'banner_url',
            'is_running',
        ]

class PromotionAdminSerializer(serializers.ModelSerializer):
    is_running = serializers.BooleanField(source='is_currently_running', read_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'bonus_coins',
            'cashback_multiplier',
            'start_date',
            'end_date',
            'is_active',
            'usage_limit',
            'usage_count',
            'banner_url',
            'is_running',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_running']

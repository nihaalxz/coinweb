from rest_framework import serializers
from .models import Cashback, CashbackStatusHistory

class CashbackStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.SerializerMethodField()

    class Meta:
        model = CashbackStatusHistory
        fields = [
            'id',
            'previous_status',
            'new_status',
            'changed_by_email',
            'reason',
            'created_at',
        ]

    def get_changed_by_email(self, obj):
        return obj.changed_by.email if obj.changed_by else 'System'

class CashbackSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)
    merchant_slug = serializers.CharField(source='merchant.slug', read_only=True)
    status_history = CashbackStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Cashback
        fields = [
            'id',
            'user',
            'user_email',
            'merchant',
            'merchant_name',
            'merchant_slug',
            'affiliate_click',
            'order_id',
            'order_amount',
            'commission_amount',
            'cashback_inr',
            'cbk_coins',
            'status',
            'rejection_reason',
            'metadata',
            'approved_at',
            'created_at',
            'updated_at',
            'status_history',
        ]
        read_only_fields = [
            'id',
            'user',
            'cbk_coins',
            'approved_at',
            'created_at',
            'updated_at',
            'status_history',
        ]

class CashbackTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['APPROVED', 'REJECTED', 'REVERSED'])
    reason = serializers.CharField(required=False, allow_blank=True)

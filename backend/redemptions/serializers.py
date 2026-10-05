from rest_framework import serializers
from .models import Redemption, RedemptionStatusHistory

class RedemptionStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.SerializerMethodField()

    class Meta:
        model = RedemptionStatusHistory
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

class RedemptionListSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Redemption
        fields = [
            'redemption_id',
            'user',
            'user_email',
            'user_name',
            'coins_deducted',
            'inr_amount',
            'payout_method',
            'masked_identifier',
            'status',
            'utr_number',
            'requested_at',
            'processed_at',
            'completed_at',
        ]
        read_only_fields = '__all__'

class RedemptionDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    status_history = RedemptionStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Redemption
        fields = [
            'redemption_id',
            'user',
            'user_email',
            'user_name',
            'wallet',
            'coins_deducted',
            'inr_amount',
            'payout_method',
            'payout_identifier',
            'masked_identifier',
            'status',
            'utr_number',
            'admin_notes',
            'failure_reason',
            'requested_at',
            'processed_at',
            'completed_at',
            'status_history',
        ]
        read_only_fields = '__all__'

class RedemptionRequestSerializer(serializers.Serializer):
    coins_amount = serializers.IntegerField(min_value=1, required=True)
    payout_method = serializers.ChoiceField(choices=['UPI', 'BANK_TRANSFER'], default='UPI')
    payout_identifier = serializers.CharField(max_length=255, required=True)

class RedemptionTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED'])
    utr_number = serializers.CharField(required=False, allow_blank=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    admin_notes = serializers.CharField(required=False, allow_blank=True)

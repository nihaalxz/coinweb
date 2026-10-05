from rest_framework import serializers
from decimal import Decimal
from .models import Wallet, WalletTransaction
from .services import CoinService

class WalletSerializer(serializers.ModelSerializer):
    inr_value = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'coin_balance',
            'inr_value',
            'lifetime_earned',
            'lifetime_redeemed',
            'is_locked',
            'lock_reason',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'coin_balance', 'lifetime_earned', 'lifetime_redeemed', 'created_at', 'updated_at']

    def get_inr_value(self, obj):
        return CoinService.coins_to_inr(obj.coin_balance)

class WalletTransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='wallet.user.email', read_only=True)
    created_by_email = serializers.SerializerMethodField()

    class Meta:
        model = WalletTransaction
        fields = [
            'tx_id',
            'wallet',
            'user_email',
            'transaction_type',
            'amount_coins',
            'balance_before',
            'balance_after',
            'inr_equivalent',
            'status',
            'reference_type',
            'reference_id',
            'description',
            'metadata',
            'created_by',
            'created_by_email',
            'created_at',
        ]
        read_only_fields = '__all__'

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else 'System'

class ManualAdjustmentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    adjustment_type = serializers.ChoiceField(choices=['CREDIT', 'DEBIT'], required=True)
    amount_coins = serializers.IntegerField(min_value=1, required=True)
    reason = serializers.CharField(min_length=5, required=True)

    def validate_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError("A detailed audit reason is mandatory for manual adjustments.")
        return value.strip()

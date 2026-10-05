from rest_framework import serializers
from .models import Referral

class ReferralSerializer(serializers.ModelSerializer):
    referrer_email = serializers.CharField(source='referrer.email', read_only=True)
    referred_email = serializers.CharField(source='referred_user.email', read_only=True)
    referred_name = serializers.CharField(source='referred_user.full_name', read_only=True)

    class Meta:
        model = Referral
        fields = [
            'id',
            'referrer',
            'referrer_email',
            'referred_user',
            'referred_email',
            'referred_name',
            'referral_code_used',
            'status',
            'reward_coins',
            'qualified_at',
            'rewarded_at',
            'created_at',
        ]
        read_only_fields = '__all__'

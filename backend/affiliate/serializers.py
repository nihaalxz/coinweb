from rest_framework import serializers
from .models import AffiliateClick

class AffiliateClickSerializer(serializers.ModelSerializer):
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)
    merchant_slug = serializers.CharField(source='merchant.slug', read_only=True)
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = AffiliateClick
        fields = [
            'click_id',
            'user',
            'user_email',
            'merchant',
            'merchant_name',
            'merchant_slug',
            'source',
            'campaign',
            'sub_id',
            'ip_address',
            'user_agent',
            'status',
            'redirect_url',
            'created_at',
        ]
        read_only_fields = '__all__'

    def get_user_email(self, obj):
        return obj.user.email if obj.user else 'Guest User'

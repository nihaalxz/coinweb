from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'admin_user',
            'admin_email',
            'action',
            'entity',
            'entity_id',
            'previous_values',
            'new_values',
            'reason',
            'ip_address',
            'user_agent',
            'created_at',
        ]

    def get_admin_email(self, obj):
        return obj.admin_user.email if obj.admin_user else 'System'

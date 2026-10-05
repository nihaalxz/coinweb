from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=100, db_index=True)
    entity = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=100, db_index=True)
    previous_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    reason = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity', 'entity_id']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        admin_str = self.admin_user.email if self.admin_user else "System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {admin_str} -> {self.action} on {self.entity}#{self.entity_id}"

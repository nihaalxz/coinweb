from .models import AuditLog

def log_admin_action(
    admin_user,
    action: str,
    entity: str,
    entity_id: str,
    previous_values: dict = None,
    new_values: dict = None,
    reason: str = "",
    request=None
) -> AuditLog:
    """
    Centralized service function to create an immutable audit log entry.
    Audit logs cannot be modified through the application UI.
    """
    ip = None
    ua = ""
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')

    return AuditLog.objects.create(
        admin_user=admin_user if (admin_user and admin_user.is_authenticated) else None,
        action=action,
        entity=entity,
        entity_id=str(entity_id),
        previous_values=previous_values or {},
        new_values=new_values or {},
        reason=reason,
        ip_address=ip if ip else None,
        user_agent=ua[:500] if ua else "",
    )

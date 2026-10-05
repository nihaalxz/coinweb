from rest_framework import generics
from accounts.permissions import IsAdminRole
from core.pagination import StandardResultsSetPagination
from .models import AuditLog
from .serializers import AuditLogSerializer

class AdminAuditLogListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AuditLogSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = AuditLog.objects.all().select_related('admin_user')
        action = self.request.query_params.get('action', '').strip()
        entity = self.request.query_params.get('entity', '').strip()
        entity_id = self.request.query_params.get('entity_id', '').strip()
        search = self.request.query_params.get('search', '').strip()

        if action:
            qs = qs.filter(action__iexact=action)
        if entity:
            qs = qs.filter(entity__iexact=entity)
        if entity_id:
            qs = qs.filter(entity_id=entity_id)
        if search:
            qs = qs.filter(reason__icontains=search)

        return qs.order_by('-created_at')

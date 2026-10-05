from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from accounts.permissions import IsAdminRole, IsMarketingAdmin
from core.pagination import StandardResultsSetPagination
from audit.services import log_admin_action
from .models import Merchant
from .serializers import MerchantPublicSerializer, MerchantAdminSerializer

class MerchantPublicListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MerchantPublicSerializer

    def get_queryset(self):
        qs = Merchant.objects.filter(is_active=True)
        category = self.request.query_params.get('category', '').strip()
        search = self.request.query_params.get('search', '').strip()

        if category and category != 'all':
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))

        return qs.order_by('display_order', 'name')

class MerchantPublicDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MerchantPublicSerializer
    lookup_field = 'slug'
    queryset = Merchant.objects.filter(is_active=True)

class AdminMerchantListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = MerchantAdminSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Merchant.objects.all().prefetch_related('affiliate_clicks', 'cashbacks')
        search = self.request.query_params.get('search', '').strip()
        category = self.request.query_params.get('category', '').strip()
        is_active = self.request.query_params.get('is_active', '').strip()

        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(slug__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if is_active in ['true', '1']:
            qs = qs.filter(is_active=True)
        elif is_active in ['false', '0']:
            qs = qs.filter(is_active=False)

        return qs.order_by('display_order', 'name')

    def perform_create(self, serializer):
        merchant = serializer.save()
        log_admin_action(
            admin_user=self.request.user,
            action='MERCHANT_CREATED',
            entity='Merchant',
            entity_id=str(merchant.id),
            new_values={'name': merchant.name, 'commission_rate': str(merchant.commission_rate)},
            reason="Created new merchant.",
            request=self.request
        )

class AdminMerchantDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsMarketingAdmin]
    serializer_class = MerchantAdminSerializer
    queryset = Merchant.objects.all().prefetch_related('affiliate_clicks', 'cashbacks')

    def perform_update(self, serializer):
        instance = self.get_object()
        old_commission = str(instance.commission_rate)
        old_reward = str(instance.cbk_reward_rate)
        old_active = instance.is_active

        updated = serializer.save()

        # Audit log changes
        changes = {}
        if old_commission != str(updated.commission_rate):
            changes['commission_rate'] = {'old': old_commission, 'new': str(updated.commission_rate)}
        if old_reward != str(updated.cbk_reward_rate):
            changes['cbk_reward_rate'] = {'old': old_reward, 'new': str(updated.cbk_reward_rate)}
        if old_active != updated.is_active:
            changes['is_active'] = {'old': old_active, 'new': updated.is_active}

        if changes:
            log_admin_action(
                admin_user=self.request.user,
                action='MERCHANT_UPDATED',
                entity='Merchant',
                entity_id=str(updated.id),
                previous_values={k: v['old'] for k, v in changes.items()},
                new_values={k: v['new'] for k, v in changes.items()},
                reason=self.request.data.get('reason', 'Updated merchant configuration.'),
                request=self.request
            )

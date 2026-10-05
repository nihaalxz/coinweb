from rest_framework import generics, permissions
from django.utils import timezone
from accounts.permissions import IsAdminRole, IsMarketingAdmin
from core.pagination import StandardResultsSetPagination
from audit.services import log_admin_action
from .models import Promotion
from .serializers import PromotionPublicSerializer, PromotionAdminSerializer

class PromotionPublicListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PromotionPublicSerializer

    def get_queryset(self):
        now = timezone.now()
        return Promotion.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)

class AdminPromotionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsMarketingAdmin]
    serializer_class = PromotionAdminSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Promotion.objects.all()

    def perform_create(self, serializer):
        promo = serializer.save()
        log_admin_action(
            admin_user=self.request.user,
            action='PROMOTION_CREATED',
            entity='Promotion',
            entity_id=str(promo.id),
            new_values={'title': promo.title, 'bonus_coins': promo.bonus_coins},
            reason="Created campaign.",
            request=self.request
        )

class AdminPromotionDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsMarketingAdmin]
    serializer_class = PromotionAdminSerializer
    queryset = Promotion.objects.all()

    def perform_update(self, serializer):
        old_promo = self.get_object()
        old_active = old_promo.is_active
        updated = serializer.save()

        log_admin_action(
            admin_user=self.request.user,
            action='PROMOTION_UPDATED',
            entity='Promotion',
            entity_id=str(updated.id),
            previous_values={'is_active': old_active},
            new_values={'is_active': updated.is_active},
            reason="Updated promotion campaign.",
            request=self.request
        )

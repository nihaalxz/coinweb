from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from accounts.permissions import IsAdminRole, IsFinanceAdmin
from core.pagination import StandardResultsSetPagination
from .models import Redemption
from .serializers import (
    RedemptionListSerializer,
    RedemptionDetailSerializer,
    RedemptionRequestSerializer,
    RedemptionTransitionSerializer,
)
from .services import RedemptionService, RedemptionException
from wallets.services import InsufficientFundsException, WalletLockedException

class UserRedemptionListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        redemptions = Redemption.objects.filter(user=request.user).order_by('-requested_at')
        return Response(RedemptionListSerializer(redemptions, many=True).data)

    def post(self, request):
        serializer = RedemptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            redemption = RedemptionService.request_redemption(
                user=request.user,
                coins_amount=serializer.validated_data['coins_amount'],
                payout_method=serializer.validated_data['payout_method'],
                payout_identifier=serializer.validated_data['payout_identifier'],
                request=request
            )
            return Response(RedemptionDetailSerializer(redemption).data, status=status.HTTP_201_CREATED)
        except (RedemptionException, InsufficientFundsException, WalletLockedException) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Failed to submit redemption: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminRedemptionListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = RedemptionListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Redemption.objects.all().select_related('user', 'wallet')
        search = self.request.query_params.get('search', '').strip()
        status_val = self.request.query_params.get('status', '').strip()
        method_val = self.request.query_params.get('method', '').strip()

        if search:
            qs = qs.filter(
                Q(redemption_id__icontains=search) |
                Q(user__email__icontains=search) |
                Q(utr_number__icontains=search)
            )
        if status_val:
            qs = qs.filter(status=status_val)
        if method_val:
            qs = qs.filter(payout_method=method_val)

        return qs.order_by('-requested_at')

class AdminRedemptionDetailView(generics.RetrieveAPIView):
    permission_classes = [IsFinanceAdmin]
    serializer_class = RedemptionDetailSerializer
    lookup_field = 'redemption_id'
    queryset = Redemption.objects.all().select_related('user', 'wallet').prefetch_related('status_history')

class AdminRedemptionTransitionView(APIView):
    permission_classes = [IsFinanceAdmin]

    def post(self, request, redemption_id):
        serializer = RedemptionTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        utr_number = serializer.validated_data.get('utr_number', '')
        reason = serializer.validated_data.get('reason', '')
        admin_notes = serializer.validated_data.get('admin_notes', '')

        try:
            redemption = RedemptionService.transition_status(
                redemption_id=redemption_id,
                new_status=new_status,
                admin_user=request.user,
                utr_number=utr_number,
                reason=reason,
                admin_notes=admin_notes,
                request=request
            )
            return Response(RedemptionDetailSerializer(redemption).data, status=status.HTTP_200_OK)
        except RedemptionException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Failed to update redemption: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

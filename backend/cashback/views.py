from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from accounts.permissions import IsAdminRole, IsOperationsAdmin
from core.pagination import StandardResultsSetPagination
from .models import Cashback
from .serializers import CashbackSerializer, CashbackTransitionSerializer
from .services import CashbackService, CashbackTransitionException

class UserCashbackListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CashbackSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Cashback.objects.filter(user=self.request.user).select_related('merchant')
        status_val = self.request.query_params.get('status', '').strip()
        if status_val:
            qs = qs.filter(status=status_val)
        return qs.order_by('-created_at')

class AdminCashbackListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CashbackSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Cashback.objects.all().select_related('user', 'merchant').prefetch_related('status_history')
        search = self.request.query_params.get('search', '').strip()
        status_val = self.request.query_params.get('status', '').strip()
        merchant_id = self.request.query_params.get('merchant_id', '').strip()
        user_id = self.request.query_params.get('user_id', '').strip()

        if search:
            qs = qs.filter(
                Q(order_id__icontains=search) |
                Q(user__email__icontains=search) |
                Q(merchant__name__icontains=search)
            )
        if status_val:
            qs = qs.filter(status=status_val)
        if merchant_id:
            qs = qs.filter(merchant_id=merchant_id)
        if user_id:
            qs = qs.filter(user_id=user_id)

        return qs.order_by('-created_at')

class AdminCashbackDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CashbackSerializer
    queryset = Cashback.objects.all().select_related('user', 'merchant').prefetch_related('status_history')

class AdminCashbackTransitionView(APIView):
    permission_classes = [IsOperationsAdmin]

    def post(self, request, pk):
        serializer = CashbackTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason', '')

        try:
            cashback = CashbackService.transition_status(
                cashback_id=pk,
                new_status=new_status,
                admin_user=request.user,
                reason=reason,
                request=request
            )
            return Response(CashbackSerializer(cashback).data, status=status.HTTP_200_OK)
        except CashbackTransitionException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Failed to update status: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

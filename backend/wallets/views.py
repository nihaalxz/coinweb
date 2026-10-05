from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from accounts.models import User
from accounts.permissions import IsAdminRole, IsFinanceAdmin
from core.pagination import StandardResultsSetPagination
from .models import Wallet, WalletTransaction
from .serializers import (
    WalletSerializer,
    WalletTransactionSerializer,
    ManualAdjustmentSerializer,
)
from .services import (
    CoinService,
    InsufficientFundsException,
    WalletLockedException,
    DuplicateTransactionException,
)

class UserWalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)

class UserTransactionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletTransactionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        qs = WalletTransaction.objects.filter(wallet=wallet)
        tx_type = self.request.query_params.get('type', '').strip()
        if tx_type:
            qs = qs.filter(transaction_type=tx_type)
        return qs.order_by('-created_at')

# ==========================================
# ADMIN WALLET & TRANSACTION VIEWS
# ==========================================

class AdminWalletListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = WalletSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Wallet.objects.all().select_related('user')
        search = self.request.query_params.get('search', '').strip()
        is_locked = self.request.query_params.get('is_locked', '').strip()

        if search:
            qs = qs.filter(
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        if is_locked in ['true', '1']:
            qs = qs.filter(is_locked=True)
        elif is_locked in ['false', '0']:
            qs = qs.filter(is_locked=False)

        return qs.order_by('-coin_balance')

class AdminTransactionListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = WalletTransactionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = WalletTransaction.objects.all().select_related('wallet__user', 'created_by')
        search = self.request.query_params.get('search', '').strip()
        tx_type = self.request.query_params.get('type', '').strip()
        user_id = self.request.query_params.get('user_id', '').strip()
        status_val = self.request.query_params.get('status', '').strip()

        if search:
            qs = qs.filter(
                Q(wallet__user__email__icontains=search) |
                Q(reference_id__icontains=search) |
                Q(description__icontains=search)
            )
        if tx_type:
            qs = qs.filter(transaction_type=tx_type)
        if user_id:
            qs = qs.filter(wallet__user_id=user_id)
        if status_val:
            qs = qs.filter(status=status_val)

        return qs.order_by('-created_at')

class AdminTransactionDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = WalletTransactionSerializer
    lookup_field = 'tx_id'
    queryset = WalletTransaction.objects.all().select_related('wallet__user', 'created_by')

class AdminManualAdjustmentView(APIView):
    permission_classes = [IsFinanceAdmin]

    def post(self, request):
        serializer = ManualAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        adj_type = serializer.validated_data['adjustment_type']
        amount = serializer.validated_data['amount_coins']
        reason = serializer.validated_data['reason']

        target_user = get_object_or_404(User, pk=user_id)
        wallet, _ = Wallet.objects.get_or_create(user=target_user)

        try:
            if adj_type == 'CREDIT':
                tx = CoinService.credit_coins(
                    wallet_id=wallet.id,
                    amount_coins=amount,
                    tx_type=WalletTransaction.Type.MANUAL_CREDIT,
                    reference_type='AdminAdjustment',
                    reference_id=f"ADM-{request.user.id}",
                    description=f"Manual Admin Credit: {reason}",
                    created_by=request.user,
                    metadata={'admin_email': request.user.email, 'reason': reason},
                    allow_duplicate=True,
                    request=request
                )
            else:
                tx = CoinService.debit_coins(
                    wallet_id=wallet.id,
                    amount_coins=amount,
                    tx_type=WalletTransaction.Type.MANUAL_DEBIT,
                    reference_type='AdminAdjustment',
                    reference_id=f"ADM-{request.user.id}",
                    description=f"Manual Admin Debit: {reason}",
                    created_by=request.user,
                    metadata={'admin_email': request.user.email, 'reason': reason},
                    request=request
                )

            return Response({
                'message': f"Successfully {adj_type.lower()}ed {amount} coins.",
                'transaction': WalletTransactionSerializer(tx).data,
                'new_balance': wallet.coin_balance
            }, status=status.HTTP_200_OK)

        except InsufficientFundsException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except WalletLockedException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Failed to execute adjustment: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

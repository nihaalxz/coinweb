from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.db.models import Q
from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    AdminUserUpdateSerializer,
)
from .permissions import IsAdminRole, IsSuperAdmin, IsOperationsAdmin
from core.pagination import StandardResultsSetPagination

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Registration successful.',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        for field in ['first_name', 'last_name', 'phone_number']:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response(UserSerializer(user).data)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Incorrect current password.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated successfully.'})

# ==========================================
# ADMIN USER MANAGEMENT VIEWS
# ==========================================

class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = User.objects.all().select_related('wallet')
        search = self.request.query_params.get('search', '').strip()
        role = self.request.query_params.get('role', '').strip()
        is_suspended = self.request.query_params.get('is_suspended', '').strip()
        is_verified = self.request.query_params.get('is_verified', '').strip()

        if search:
            qs = qs.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(referral_code__icontains=search)
            )
        if role:
            qs = qs.filter(role=role)
        if is_suspended in ['true', '1']:
            qs = qs.filter(is_suspended=True)
        elif is_suspended in ['false', '0']:
            qs = qs.filter(is_suspended=False)
        if is_verified in ['true', '1']:
            qs = qs.filter(is_verified=True)

        return qs.order_by('-created_at')

class AdminUserDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, user_id):
        try:
            target_user = User.objects.select_related('wallet').get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = UserSerializer(target_user).data

        # Include summary statistics for admin
        from wallets.models import WalletTransaction
        from cashback.models import Cashback
        from redemptions.models import Redemption
        from affiliate.models import AffiliateClick
        from referrals.models import Referral

        data['stats'] = {
            'total_clicks': AffiliateClick.objects.filter(user=target_user).count(),
            'total_cashbacks': Cashback.objects.filter(user=target_user).count(),
            'total_redemptions': Redemption.objects.filter(user=target_user).count(),
            'total_referrals': Referral.objects.filter(referrer=target_user).count(),
        }

        # Include recent 10 transactions
        transactions = WalletTransaction.objects.filter(
            wallet__user=target_user
        ).order_by('-created_at')[:10]
        
        from wallets.serializers import WalletTransactionSerializer
        data['recent_transactions'] = WalletTransactionSerializer(transactions, many=True).data

        return Response(data)

    def patch(self, request, user_id):
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserUpdateSerializer(target_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Track old values for audit
        old_role = target_user.role
        old_suspended = target_user.is_suspended

        updated_user = serializer.save()

        # Audit log if role or suspension status changed
        from audit.services import log_admin_action
        if old_role != updated_user.role:
            log_admin_action(
                admin_user=request.user,
                action='ROLE_CHANGE',
                entity='User',
                entity_id=str(updated_user.id),
                previous_values={'role': old_role},
                new_values={'role': updated_user.role},
                reason=request.data.get('reason', 'Admin updated user role.'),
                request=request
            )
        if old_suspended != updated_user.is_suspended:
            action_name = 'USER_SUSPENSION' if updated_user.is_suspended else 'USER_REACTIVATION'
            log_admin_action(
                admin_user=request.user,
                action=action_name,
                entity='User',
                entity_id=str(updated_user.id),
                previous_values={'is_suspended': old_suspended},
                new_values={'is_suspended': updated_user.is_suspended, 'reason': updated_user.suspension_reason},
                reason=request.data.get('reason', updated_user.suspension_reason or 'Status change.'),
                request=request
            )

        return Response(UserSerializer(updated_user).data)

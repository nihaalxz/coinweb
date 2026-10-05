from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from accounts.permissions import IsAdminRole
from core.pagination import StandardResultsSetPagination
from .models import Referral
from .serializers import ReferralSerializer

class UserReferralSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        referrals = Referral.objects.filter(referrer=user)
        total_count = referrals.count()
        rewarded_count = referrals.filter(status=Referral.Status.REWARDED).count()
        total_coins_earned = sum(r.reward_coins for r in referrals.filter(status=Referral.Status.REWARDED))

        return Response({
            'referral_code': user.referral_code,
            'referral_link': f"https://cashbackkart.in/join?ref={user.referral_code}",
            'total_referrals': total_count,
            'successful_referrals': rewarded_count,
            'coins_earned': total_coins_earned,
            'history': ReferralSerializer(referrals[:20], many=True).data
        })

class AdminReferralListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = ReferralSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Referral.objects.all().select_related('referrer', 'referred_user')
        search = self.request.query_params.get('search', '').strip()
        status_val = self.request.query_params.get('status', '').strip()

        if search:
            qs = qs.filter(
                Q(referrer__email__icontains=search) |
                Q(referred_user__email__icontains=search) |
                Q(referral_code_used__icontains=search)
            )
        if status_val:
            qs = qs.filter(status=status_val)

        return qs.order_by('-created_at')

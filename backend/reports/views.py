import csv
from datetime import timedelta
from decimal import Decimal
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from accounts.models import User
from accounts.permissions import IsAdminRole, IsFinanceAdmin
from wallets.models import Wallet, WalletTransaction
from wallets.services import CoinService
from merchants.models import Merchant
from affiliate.models import AffiliateClick
from cashback.models import Cashback
from redemptions.models import Redemption
from referrals.models import Referral

class AdminDashboardMetricsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # 1. User Metrics
        total_users = User.objects.filter(role=User.Role.CUSTOMER).count()
        active_users = User.objects.filter(role=User.Role.CUSTOMER, is_active=True, is_suspended=False).count()
        new_users = User.objects.filter(role=User.Role.CUSTOMER, created_at__gte=thirty_days_ago).count()
        verified_users = User.objects.filter(role=User.Role.CUSTOMER, is_verified=True).count()

        # 2. Wallet Metrics
        wallet_aggs = Wallet.objects.aggregate(
            outstanding=Sum('coin_balance'),
            lifetime_earned=Sum('lifetime_earned'),
            lifetime_redeemed=Sum('lifetime_redeemed')
        )
        coins_outstanding = wallet_aggs['outstanding'] or 0
        coins_issued = wallet_aggs['lifetime_earned'] or 0
        coins_redeemed = wallet_aggs['lifetime_redeemed'] or 0
        inr_outstanding = CoinService.coins_to_inr(coins_outstanding)
        inr_issued = CoinService.coins_to_inr(coins_issued)
        inr_redeemed = CoinService.coins_to_inr(coins_redeemed)

        # 3. Cashback Metrics
        cb_pending = Cashback.objects.filter(status=Cashback.Status.PENDING).count()
        cb_approved = Cashback.objects.filter(status=Cashback.Status.APPROVED).count()
        cb_rejected = Cashback.objects.filter(status=Cashback.Status.REJECTED).count()
        cb_reversed = Cashback.objects.filter(status=Cashback.Status.REVERSED).count()
        cb_approved_inr = Cashback.objects.filter(
            status=Cashback.Status.APPROVED
        ).aggregate(total=Sum('cashback_inr'))['total'] or Decimal('0.00')

        # 4. Redemption Metrics
        red_requested = Redemption.objects.filter(status=Redemption.Status.REQUESTED).count()
        red_processing = Redemption.objects.filter(status=Redemption.Status.PROCESSING).count()
        red_completed = Redemption.objects.filter(status=Redemption.Status.COMPLETED).count()
        red_failed = Redemption.objects.filter(status=Redemption.Status.FAILED).count()
        total_payout_inr = Redemption.objects.filter(
            status=Redemption.Status.COMPLETED
        ).aggregate(total=Sum('inr_amount'))['total'] or Decimal('0.00')

        # 5. Affiliate Metrics
        total_clicks = AffiliateClick.objects.count()
        total_conversions = AffiliateClick.objects.filter(status=AffiliateClick.Status.CONVERTED).count()
        conversion_rate = round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0.0

        # 6. Merchant Metrics
        active_merchants = Merchant.objects.filter(is_active=True).count()
        top_merchants = Merchant.objects.annotate(
            conversions=Count('cashbacks')
        ).order_by('-conversions')[:5].values('id', 'name', 'category', 'cbk_reward_rate', 'conversions')

        # 7. Referral Metrics
        total_referrals = Referral.objects.count()
        successful_referrals = Referral.objects.filter(status=Referral.Status.REWARDED).count()

        # 8. Activity Chart Data (last 14 days)
        fourteen_days_ago = now - timedelta(days=14)
        daily_users = User.objects.filter(
            created_at__gte=fourteen_days_ago,
            role=User.Role.CUSTOMER
        ).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

        daily_clicks = AffiliateClick.objects.filter(
            created_at__gte=fourteen_days_ago
        ).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

        daily_cashback = Cashback.objects.filter(
            created_at__gte=fourteen_days_ago,
            status=Cashback.Status.APPROVED
        ).annotate(date=TruncDate('created_at')).values('date').annotate(
            coins=Sum('cbk_coins'), count=Count('id')
        ).order_by('date')

        return Response({
            'users': {
                'total': total_users,
                'active': active_users,
                'new_last_30_days': new_users,
                'verified': verified_users,
            },
            'wallet': {
                'coins_outstanding': coins_outstanding,
                'coins_issued': coins_issued,
                'coins_redeemed': coins_redeemed,
                'inr_outstanding': inr_outstanding,
                'inr_issued': inr_issued,
                'inr_redeemed': inr_redeemed,
            },
            'cashback': {
                'pending': cb_pending,
                'approved': cb_approved,
                'rejected': cb_rejected,
                'reversed': cb_reversed,
                'approved_inr': cb_approved_inr,
            },
            'redemptions': {
                'requested': red_requested,
                'processing': red_processing,
                'completed': red_completed,
                'failed': red_failed,
                'total_payout_inr': total_payout_inr,
            },
            'affiliate': {
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'conversion_rate_percent': conversion_rate,
            },
            'merchants': {
                'active_count': active_merchants,
                'top_performers': list(top_merchants),
            },
            'referrals': {
                'total': total_referrals,
                'successful': successful_referrals,
            },
            'charts': {
                'daily_registrations': list(daily_users),
                'daily_clicks': list(daily_clicks),
                'daily_cashback': list(daily_cashback),
            }
        })

# ==============================================================================
# CSV EXPORT REPORT ENDPOINTS
# ==============================================================================

class ExportUsersReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cbk_users_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['User ID', 'Email', 'Full Name', 'Phone', 'Role', 'Status', 'Verified', 'Coin Balance', 'Lifetime Earned', 'Created At'])

        users = User.objects.select_related('wallet').order_by('-created_at')
        for u in users:
            bal = u.wallet.coin_balance if hasattr(u, 'wallet') else 0
            earned = u.wallet.lifetime_earned if hasattr(u, 'wallet') else 0
            status_str = 'Suspended' if u.is_suspended else ('Active' if u.is_active else 'Inactive')
            writer.writerow([
                u.id, u.email, u.full_name, u.phone_number, u.role, status_str,
                u.is_verified, bal, earned, u.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

class ExportTransactionsReportView(APIView):
    permission_classes = [IsFinanceAdmin]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cbk_transactions_ledger.csv"'

        writer = csv.writer(response)
        writer.writerow(['Tx ID', 'User Email', 'Type', 'Amount Coins', 'INR Equivalent', 'Balance Before', 'Balance After', 'Status', 'Reference Type', 'Reference ID', 'Description', 'Timestamp'])

        txs = WalletTransaction.objects.select_related('wallet__user').order_by('-created_at')
        for t in txs:
            writer.writerow([
                str(t.tx_id), t.wallet.user.email, t.transaction_type, t.amount_coins,
                str(t.inr_equivalent), t.balance_before, t.balance_after, t.status,
                t.reference_type, t.reference_id, t.description, t.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

class ExportCashbackReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cbk_cashback_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'User Email', 'Merchant', 'Order ID', 'Order Amount INR', 'Cashback INR', 'CBK Coins', 'Status', 'Approved At', 'Created At'])

        cashbacks = Cashback.objects.select_related('user', 'merchant').order_by('-created_at')
        for cb in cashbacks:
            approved_str = cb.approved_at.strftime('%Y-%m-%d %H:%M:%S') if cb.approved_at else ''
            writer.writerow([
                cb.id, cb.user.email, cb.merchant.name, cb.order_id, str(cb.order_amount),
                str(cb.cashback_inr), cb.cbk_coins, cb.status, approved_str,
                cb.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

class ExportRedemptionsReportView(APIView):
    permission_classes = [IsFinanceAdmin]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cbk_redemptions_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Redemption ID', 'User Email', 'Method', 'Masked Account', 'Coins Deducted', 'INR Amount', 'Status', 'UTR Number', 'Requested At', 'Completed At'])

        reds = Redemption.objects.select_related('user').order_by('-requested_at')
        for r in reds:
            completed_str = r.completed_at.strftime('%Y-%m-%d %H:%M:%S') if r.completed_at else ''
            writer.writerow([
                str(r.redemption_id), r.user.email, r.payout_method, r.masked_identifier,
                r.coins_deducted, str(r.inr_amount), r.status, r.utr_number,
                r.requested_at.strftime('%Y-%m-%d %H:%M:%S'), completed_str
            ])

        return response

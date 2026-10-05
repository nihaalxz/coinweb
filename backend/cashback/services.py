from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Cashback, CashbackStatusHistory
from wallets.models import Wallet, WalletTransaction
from wallets.services import CoinService, InsufficientFundsException
from audit.services import log_admin_action

class CashbackTransitionException(Exception):
    pass

class CashbackService:
    @classmethod
    def transition_status(
        cls,
        cashback_id: int,
        new_status: str,
        admin_user=None,
        reason: str = "",
        request=None
    ) -> Cashback:
        with transaction.atomic():
            cashback = Cashback.objects.select_for_update().get(pk=cashback_id)
            previous_status = cashback.status

            if previous_status == new_status:
                return cashback  # Idempotent: no-op if already in desired state

            # Validate valid state machine transitions
            if previous_status == Cashback.Status.REVERSED:
                raise CashbackTransitionException("Cannot change status of a reversed cashback record.")

            wallet, _ = Wallet.objects.get_or_create(user=cashback.user)

            # 1. PENDING -> APPROVED
            if new_status == Cashback.Status.APPROVED:
                CoinService.credit_coins(
                    wallet_id=wallet.id,
                    amount_coins=cashback.cbk_coins,
                    tx_type=WalletTransaction.Type.CASHBACK,
                    reference_type='Cashback',
                    reference_id=str(cashback.id),
                    description=f"Approved Cashback from {cashback.merchant.name} (Order #{cashback.order_id})",
                    created_by=admin_user,
                    metadata={
                        'merchant': cashback.merchant.name,
                        'order_id': cashback.order_id,
                        'order_amount': str(cashback.order_amount),
                    },
                    allow_duplicate=False,
                    request=request
                )
                cashback.approved_at = timezone.now()
                if cashback.affiliate_click:
                    cashback.affiliate_click.status = 'CONVERTED'
                    cashback.affiliate_click.save(update_fields=['status'])

                # Check if this qualifies a referral
                try:
                    from referrals.services import ReferralService
                    ReferralService.check_and_qualify_referral(user=cashback.user, request=request)
                except Exception:
                    pass

            # 2. APPROVED -> REVERSED
            elif new_status == Cashback.Status.REVERSED:
                if previous_status == Cashback.Status.APPROVED:
                    # Deduct the previously credited coins
                    try:
                        CoinService.debit_coins(
                            wallet_id=wallet.id,
                            amount_coins=cashback.cbk_coins,
                            tx_type=WalletTransaction.Type.REVERSAL,
                            reference_type='CashbackReversal',
                            reference_id=str(cashback.id),
                            description=f"Cashback Reversal: {cashback.merchant.name} Order #{cashback.order_id}. Reason: {reason}",
                            created_by=admin_user,
                            metadata={'original_cashback_id': cashback.id, 'reason': reason},
                            request=request
                        )
                    except InsufficientFundsException:
                        # If user withdrew coins, debit whatever is available and lock or flag
                        available = wallet.coin_balance
                        if available > 0:
                            CoinService.debit_coins(
                                wallet_id=wallet.id,
                                amount_coins=available,
                                tx_type=WalletTransaction.Type.REVERSAL,
                                reference_type='CashbackReversalPartial',
                                reference_id=str(cashback.id),
                                description=f"Partial Cashback Reversal (Insufficient Coins): {reason}",
                                created_by=admin_user,
                                request=request
                            )

            # 3. PENDING -> REJECTED
            elif new_status == Cashback.Status.REJECTED:
                cashback.rejection_reason = reason

            cashback.status = new_status
            cashback.save()

            # Record Status History
            CashbackStatusHistory.objects.create(
                cashback=cashback,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=admin_user,
                reason=reason
            )

            # Record Audit Log
            log_admin_action(
                admin_user=admin_user,
                action='CASHBACK_STATUS_CHANGE',
                entity='Cashback',
                entity_id=str(cashback.id),
                previous_values={'status': previous_status},
                new_values={'status': new_status, 'coins': cashback.cbk_coins},
                reason=reason,
                request=request
            )

            return cashback

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from .models import Redemption, RedemptionStatusHistory
from wallets.models import Wallet, WalletTransaction
from wallets.services import CoinService, InsufficientFundsException, WalletLockedException
from audit.services import log_admin_action

MIN_REDEMPTION_COINS = getattr(settings, 'MIN_REDEMPTION_COINS', 500)

class RedemptionException(Exception):
    pass

class RedemptionService:
    @classmethod
    def request_redemption(
        cls,
        user,
        coins_amount: int,
        payout_method: str,
        payout_identifier: str,
        request=None
    ) -> Redemption:
        if coins_amount < MIN_REDEMPTION_COINS:
            min_inr = CoinService.coins_to_inr(MIN_REDEMPTION_COINS)
            raise RedemptionException(
                f"Minimum redemption amount is {MIN_REDEMPTION_COINS} CBK Coins (₹{min_inr})."
            )

        if not payout_identifier or not payout_identifier.strip():
            raise RedemptionException("Valid UPI ID or Bank details are required for redemption.")

        with transaction.atomic():
            wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
            if wallet.is_locked:
                raise WalletLockedException(f"Wallet is locked: {wallet.lock_reason or 'Contact support.'}")

            inr_val = CoinService.coins_to_inr(coins_amount)

            # Atomic coin deduction
            tx = CoinService.debit_coins(
                wallet_id=wallet.id,
                amount_coins=coins_amount,
                tx_type=WalletTransaction.Type.REDEMPTION,
                reference_type='Redemption',
                reference_id='PENDING',
                description=f"Redemption request: {coins_amount} Coins -> ₹{inr_val} via {payout_method}",
                created_by=user,
                metadata={'method': payout_method, 'coins': coins_amount, 'inr': str(inr_val)},
                request=request
            )

            redemption = Redemption.objects.create(
                user=user,
                wallet=wallet,
                coins_deducted=coins_amount,
                inr_amount=inr_val,
                payout_method=payout_method,
                payout_identifier=payout_identifier.strip(),
                status=Redemption.Status.REQUESTED
            )

            # Update tx reference with real redemption ID
            tx.reference_id = str(redemption.redemption_id)
            tx.save(update_fields=['reference_id'])

            RedemptionStatusHistory.objects.create(
                redemption=redemption,
                previous_status='NEW',
                new_status=Redemption.Status.REQUESTED,
                changed_by=user,
                reason="User initiated redemption."
            )

            return redemption

    @classmethod
    def transition_status(
        cls,
        redemption_id: str,
        new_status: str,
        admin_user,
        utr_number: str = "",
        reason: str = "",
        admin_notes: str = "",
        request=None
    ) -> Redemption:
        with transaction.atomic():
            redemption = Redemption.objects.select_for_update().get(redemption_id=redemption_id)
            previous_status = redemption.status

            if previous_status == new_status:
                return redemption  # Idempotent

            if previous_status in [Redemption.Status.COMPLETED, Redemption.Status.FAILED, Redemption.Status.CANCELLED]:
                raise RedemptionException(f"Cannot alter status of a terminal redemption (current: {previous_status}).")

            # 1. Transition to COMPLETED
            if new_status == Redemption.Status.COMPLETED:
                if not utr_number or not utr_number.strip():
                    raise RedemptionException("A UTR / Bank Reference number is required to complete a payout.")
                redemption.utr_number = utr_number.strip()
                redemption.completed_at = timezone.now()

            # 2. Transition to PROCESSING
            elif new_status == Redemption.Status.PROCESSING:
                redemption.processed_at = timezone.now()

            # 3. Transition to FAILED or CANCELLED (Must atomically refund coins!)
            elif new_status in [Redemption.Status.FAILED, Redemption.Status.CANCELLED]:
                if not reason.strip():
                    raise RedemptionException("A failure or cancellation reason is required.")
                redemption.failure_reason = reason.strip()

                # Atomically refund coins to wallet
                CoinService.credit_coins(
                    wallet_id=redemption.wallet.id,
                    amount_coins=redemption.coins_deducted,
                    tx_type=WalletTransaction.Type.REFUND,
                    reference_type='RedemptionRefund',
                    reference_id=str(redemption.redemption_id),
                    description=f"Redemption {new_status}: {redemption.coins_deducted} Coins refunded. Reason: {reason}",
                    created_by=admin_user,
                    metadata={'redemption_id': str(redemption.redemption_id), 'reason': reason},
                    allow_duplicate=False,
                    request=request
                )

                # Adjust lifetime_redeemed back
                wallet = redemption.wallet
                wallet.lifetime_redeemed = max(0, wallet.lifetime_redeemed - redemption.coins_deducted)
                wallet.save(update_fields=['lifetime_redeemed'])

            if admin_notes:
                redemption.admin_notes = admin_notes.strip()

            redemption.status = new_status
            redemption.save()

            RedemptionStatusHistory.objects.create(
                redemption=redemption,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=admin_user,
                reason=reason or admin_notes
            )

            log_admin_action(
                admin_user=admin_user,
                action='REDEMPTION_STATUS_CHANGE',
                entity='Redemption',
                entity_id=str(redemption.redemption_id),
                previous_values={'status': previous_status},
                new_values={'status': new_status, 'utr': utr_number, 'coins': redemption.coins_deducted},
                reason=reason or admin_notes,
                request=request
            )

            return redemption

from django.utils import timezone
from django.db import transaction
from .models import Referral
from wallets.models import Wallet, WalletTransaction
from wallets.services import CoinService

class ReferralService:
    @classmethod
    def check_and_qualify_referral(cls, user, request=None):
        """
        Triggered when a user completes a qualifying event (e.g. first approved cashback).
        Awards referral reward to the referrer.
        """
        try:
            referral = Referral.objects.select_related('referrer', 'referred_user').get(
                referred_user=user,
                status=Referral.Status.REGISTERED
            )
        except Referral.DoesNotExist:
            return None

        with transaction.atomic():
            referral.status = Referral.Status.QUALIFIED
            referral.qualified_at = timezone.now()

            # Credit Referrer
            referrer_wallet, _ = Wallet.objects.get_or_create(user=referral.referrer)
            CoinService.credit_coins(
                wallet_id=referrer_wallet.id,
                amount_coins=referral.reward_coins,
                tx_type=WalletTransaction.Type.REFERRAL_BONUS,
                reference_type='Referral',
                reference_id=str(referral.id),
                description=f"Referral Bonus for inviting {referral.referred_user.email}",
                metadata={'referred_user_id': referral.referred_user.id},
                allow_duplicate=False,
                request=request
            )

            referral.status = Referral.Status.REWARDED
            referral.rewarded_at = timezone.now()
            referral.save()

            return referral

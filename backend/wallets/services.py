from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Wallet, WalletTransaction
from audit.services import log_admin_action

# Single source of truth for CBK Coin conversion: 10 CBK Coins = 1 INR
COINS_PER_INR = getattr(settings, 'COINS_PER_INR', 10)

class WalletLockedException(Exception):
    pass

class InsufficientFundsException(Exception):
    pass

class DuplicateTransactionException(Exception):
    pass

class InvalidAmountException(Exception):
    pass

class CoinService:
    """
    Centralized financial and coin ledger service.
    All balance modifications MUST pass through this service to preserve
    strict monetary auditability and row-level locking.
    """
    COINS_PER_INR = COINS_PER_INR

    @classmethod
    def coins_to_inr(cls, coins: int) -> Decimal:
        """
        Converts CBK Coins to INR with exact Decimal precision.
        Formula: coins / 10 = ₹ INR
        """
        if coins is None:
            return Decimal('0.00')
        inr = Decimal(coins) / Decimal(cls.COINS_PER_INR)
        return inr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @classmethod
    def inr_to_coins(cls, inr: Decimal) -> int:
        """
        Converts INR to CBK Coins.
        Formula: ₹ INR * 10 = coins
        """
        if inr is None:
            return 0
        return int((Decimal(str(inr)) * Decimal(cls.COINS_PER_INR)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

    @classmethod
    def get_balance(cls, user) -> int:
        wallet, _ = Wallet.objects.get_or_create(user=user)
        return wallet.coin_balance

    @classmethod
    def credit_coins(
        cls,
        wallet_id: int,
        amount_coins: int,
        tx_type: str,
        reference_type: str = '',
        reference_id: str = '',
        description: str = '',
        created_by=None,
        metadata: dict = None,
        allow_duplicate: bool = False,
        request=None
    ) -> WalletTransaction:
        if amount_coins <= 0:
            raise InvalidAmountException("Credit amount must be greater than zero.")

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet_id)
            if wallet.is_locked:
                raise WalletLockedException(f"Wallet is locked: {wallet.lock_reason or 'Contact support.'}")

            # Idempotency / duplicate check for unique business events
            if not allow_duplicate and reference_type and reference_id:
                already_exists = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type=tx_type,
                    reference_type=reference_type,
                    reference_id=str(reference_id),
                    status=WalletTransaction.Status.COMPLETED
                ).exists()
                if already_exists:
                    raise DuplicateTransactionException(
                        f"Transaction already credited for {reference_type} #{reference_id}"
                    )

            balance_before = wallet.coin_balance
            balance_after = balance_before + amount_coins

            wallet.coin_balance = balance_after
            wallet.lifetime_earned += amount_coins
            wallet.save(update_fields=['coin_balance', 'lifetime_earned', 'updated_at'])

            inr_value = cls.coins_to_inr(amount_coins)

            tx = WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type=tx_type,
                amount_coins=amount_coins,
                balance_before=balance_before,
                balance_after=balance_after,
                inr_equivalent=inr_value,
                status=WalletTransaction.Status.COMPLETED,
                reference_type=reference_type,
                reference_id=str(reference_id),
                description=description,
                metadata=metadata or {},
                created_by=created_by
            )

            # Audit logging if manual administrative adjustment
            if tx_type in [WalletTransaction.Type.MANUAL_CREDIT, WalletTransaction.Type.ADMIN_ADJUSTMENT]:
                log_admin_action(
                    admin_user=created_by,
                    action='MANUAL_COIN_CREDIT',
                    entity='Wallet',
                    entity_id=str(wallet.id),
                    previous_values={'coin_balance': balance_before},
                    new_values={'coin_balance': balance_after, 'amount': amount_coins, 'tx_id': str(tx.tx_id)},
                    reason=description,
                    request=request
                )

            return tx

    @classmethod
    def debit_coins(
        cls,
        wallet_id: int,
        amount_coins: int,
        tx_type: str,
        reference_type: str = '',
        reference_id: str = '',
        description: str = '',
        created_by=None,
        metadata: dict = None,
        request=None
    ) -> WalletTransaction:
        if amount_coins <= 0:
            raise InvalidAmountException("Debit amount must be greater than zero.")

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet_id)
            if wallet.is_locked:
                raise WalletLockedException(f"Wallet is locked: {wallet.lock_reason or 'Contact support.'}")

            if wallet.coin_balance < amount_coins:
                raise InsufficientFundsException(
                    f"Insufficient coin balance. Available: {wallet.coin_balance}, Requested: {amount_coins}"
                )

            balance_before = wallet.coin_balance
            balance_after = balance_before - amount_coins

            wallet.coin_balance = balance_after
            if tx_type == WalletTransaction.Type.REDEMPTION:
                wallet.lifetime_redeemed += amount_coins
                wallet.save(update_fields=['coin_balance', 'lifetime_redeemed', 'updated_at'])
            else:
                wallet.save(update_fields=['coin_balance', 'updated_at'])

            inr_value = cls.coins_to_inr(amount_coins)

            tx = WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type=tx_type,
                amount_coins=amount_coins,
                balance_before=balance_before,
                balance_after=balance_after,
                inr_equivalent=inr_value,
                status=WalletTransaction.Status.COMPLETED,
                reference_type=reference_type,
                reference_id=str(reference_id),
                description=description,
                metadata=metadata or {},
                created_by=created_by
            )

            # Audit logging if manual administrative adjustment
            if tx_type in [WalletTransaction.Type.MANUAL_DEBIT, WalletTransaction.Type.ADMIN_ADJUSTMENT]:
                log_admin_action(
                    admin_user=created_by,
                    action='MANUAL_COIN_DEBIT',
                    entity='Wallet',
                    entity_id=str(wallet.id),
                    previous_values={'coin_balance': balance_before},
                    new_values={'coin_balance': balance_after, 'amount': amount_coins, 'tx_id': str(tx.tx_id)},
                    reason=description,
                    request=request
                )

            return tx

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from wallets.models import Wallet, WalletTransaction
from wallets.services import (
    CoinService,
    InsufficientFundsException,
    DuplicateTransactionException,
    InvalidAmountException,
)
from merchants.models import Merchant
from cashback.models import Cashback
from cashback.services import CashbackService
from redemptions.models import Redemption
from redemptions.services import RedemptionService, RedemptionException
from referrals.models import Referral
from referrals.services import ReferralService
from audit.models import AuditLog

User = get_user_model()

class CBKSystemTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Admin
        self.super_admin = User.objects.create_superuser(
            email='testadmin@cbk.com',
            password='AdminPassword123'
        )

        # Create Customer 1
        self.user1 = User.objects.create_user(
            email='customer1@cbk.com',
            password='UserPass123',
            first_name='Customer',
            last_name='One'
        )

        # Create Customer 2
        self.user2 = User.objects.create_user(
            email='customer2@cbk.com',
            password='UserPass123',
            first_name='Customer',
            last_name='Two'
        )

        # Create Merchant
        self.merchant = Merchant.objects.create(
            name='Test Merchant',
            slug='test-merchant',
            website_url='https://testmerchant.com',
            commission_rate=Decimal('10.00'),
            cbk_reward_rate=Decimal('8.00'),
            is_active=True
        )

    # 1. Accounts & Authentication Tests
    def test_user_registration(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'newuser@cbk.com',
            'password': 'SecureUserPassword123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '9988776655'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', resp.data)
        user = User.objects.get(email='newuser@cbk.com')
        self.assertTrue(user.referral_code)
        self.assertEqual(user.wallet.coin_balance, 0)

    def test_user_login(self):
        resp = self.client.post('/api/auth/login/', {
            'email': 'customer1@cbk.com',
            'password': 'UserPass123'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)

    def test_invalid_login(self):
        resp = self.client.post('/api/auth/login/', {
            'email': 'customer1@cbk.com',
            'password': 'WrongPassword'
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # 2. Wallet & Coin Conversion Tests
    def test_coin_conversion_accuracy(self):
        # 10 CBK Coins = 1 INR
        self.assertEqual(CoinService.coins_to_inr(10), Decimal('1.00'))
        self.assertEqual(CoinService.coins_to_inr(100), Decimal('10.00'))
        self.assertEqual(CoinService.coins_to_inr(1525), Decimal('152.50'))
        self.assertEqual(CoinService.inr_to_coins(Decimal('1.00')), 10)
        self.assertEqual(CoinService.inr_to_coins(Decimal('50.00')), 500)

    def test_atomic_credit_and_debit(self):
        wallet = self.user1.wallet
        # Credit 1,000 coins (= ₹100)
        tx = CoinService.credit_coins(
            wallet_id=wallet.id,
            amount_coins=1000,
            tx_type=WalletTransaction.Type.MANUAL_CREDIT,
            reference_type='Test',
            reference_id='T1',
            description='Test credit'
        )
        wallet.refresh_from_db()
        self.assertEqual(wallet.coin_balance, 1000)
        self.assertEqual(wallet.lifetime_earned, 1000)
        self.assertEqual(tx.balance_after, 1000)
        self.assertEqual(tx.inr_equivalent, Decimal('100.00'))

        # Debit 400 coins (= ₹40)
        tx_debit = CoinService.debit_coins(
            wallet_id=wallet.id,
            amount_coins=400,
            tx_type=WalletTransaction.Type.REDEMPTION,
            reference_type='Test',
            reference_id='T2',
            description='Test debit'
        )
        wallet.refresh_from_db()
        self.assertEqual(wallet.coin_balance, 600)
        self.assertEqual(wallet.lifetime_redeemed, 400)
        self.assertEqual(tx_debit.balance_after, 600)

    def test_insufficient_balance_rejection(self):
        wallet = self.user1.wallet
        with self.assertRaises(InsufficientFundsException):
            CoinService.debit_coins(
                wallet_id=wallet.id,
                amount_coins=500,
                tx_type=WalletTransaction.Type.REDEMPTION
            )

    def test_duplicate_transaction_prevention(self):
        wallet = self.user1.wallet
        # Credit first time
        CoinService.credit_coins(
            wallet_id=wallet.id,
            amount_coins=200,
            tx_type=WalletTransaction.Type.CASHBACK,
            reference_type='Cashback',
            reference_id='UNIQUE-101',
            description='Cashback'
        )
        # Attempt duplicate credit with same reference
        with self.assertRaises(DuplicateTransactionException):
            CoinService.credit_coins(
                wallet_id=wallet.id,
                amount_coins=200,
                tx_type=WalletTransaction.Type.CASHBACK,
                reference_type='Cashback',
                reference_id='UNIQUE-101',
                description='Duplicate cashback attempt'
            )

    # 3. Cashback Lifecycle Tests
    def test_cashback_approval_and_reversal(self):
        wallet = self.user1.wallet
        cashback = Cashback.objects.create(
            user=self.user1,
            merchant=self.merchant,
            order_id='ORD-999',
            order_amount=Decimal('1000.00'),
            cashback_inr=Decimal('80.00'),
            cbk_coins=800,  # 80 * 10
            status=Cashback.Status.PENDING
        )
        self.assertEqual(wallet.coin_balance, 0)

        # Transition to APPROVED
        CashbackService.transition_status(
            cashback_id=cashback.id,
            new_status=Cashback.Status.APPROVED,
            admin_user=self.super_admin,
            reason='Merchant verified'
        )
        cashback.refresh_from_db()
        wallet.refresh_from_db()
        self.assertEqual(cashback.status, Cashback.Status.APPROVED)
        self.assertEqual(wallet.coin_balance, 800)

        # Transition to REVERSED (User cancelled/returned order)
        CashbackService.transition_status(
            cashback_id=cashback.id,
            new_status=Cashback.Status.REVERSED,
            admin_user=self.super_admin,
            reason='User returned merchandise'
        )
        cashback.refresh_from_db()
        wallet.refresh_from_db()
        self.assertEqual(cashback.status, Cashback.Status.REVERSED)
        self.assertEqual(wallet.coin_balance, 0)

    # 4. Redemption Lifecycle Tests
    def test_redemption_flow_with_completion(self):
        wallet = self.user1.wallet
        # Credit 1000 coins first
        CoinService.credit_coins(
            wallet_id=wallet.id,
            amount_coins=1000,
            tx_type=WalletTransaction.Type.MANUAL_CREDIT
        )

        # Request 600 coins redemption (= ₹60)
        redemption = RedemptionService.request_redemption(
            user=self.user1,
            coins_amount=600,
            payout_method='UPI',
            payout_identifier='customer1@oksbi'
        )
        wallet.refresh_from_db()
        self.assertEqual(wallet.coin_balance, 400)
        self.assertEqual(redemption.status, Redemption.Status.REQUESTED)
        self.assertEqual(redemption.masked_identifier, 'cu*******@oksbi')

        # Admin completes redemption with UTR
        RedemptionService.transition_status(
            redemption_id=redemption.redemption_id,
            new_status=Redemption.Status.COMPLETED,
            admin_user=self.super_admin,
            utr_number='UTR123456789'
        )
        redemption.refresh_from_db()
        self.assertEqual(redemption.status, Redemption.Status.COMPLETED)
        self.assertEqual(redemption.utr_number, 'UTR123456789')

    def test_redemption_cancellation_refunds_coins(self):
        wallet = self.user1.wallet
        CoinService.credit_coins(
            wallet_id=wallet.id,
            amount_coins=1000,
            tx_type=WalletTransaction.Type.MANUAL_CREDIT
        )

        redemption = RedemptionService.request_redemption(
            user=self.user1,
            coins_amount=500,
            payout_method='UPI',
            payout_identifier='customer1@oksbi'
        )
        wallet.refresh_from_db()
        self.assertEqual(wallet.coin_balance, 500)

        # Admin rejects/cancels redemption -> coins must be automatically refunded!
        RedemptionService.transition_status(
            redemption_id=redemption.redemption_id,
            new_status=Redemption.Status.FAILED,
            admin_user=self.super_admin,
            reason='Invalid UPI VPA handle'
        )
        redemption.refresh_from_db()
        wallet.refresh_from_db()
        self.assertEqual(redemption.status, Redemption.Status.FAILED)
        self.assertEqual(wallet.coin_balance, 1000)

    # 5. Referral Tests
    def test_referral_qualification(self):
        # User 1 refers User 2
        ref = Referral.objects.create(
            referrer=self.user1,
            referred_user=self.user2,
            referral_code_used=self.user1.referral_code,
            reward_coins=100
        )
        self.assertEqual(self.user1.wallet.coin_balance, 0)

        # User 2 receives an approved cashback
        cashback = Cashback.objects.create(
            user=self.user2,
            merchant=self.merchant,
            order_id='REF-FIRST-01',
            order_amount=Decimal('500.00'),
            cashback_inr=Decimal('40.00'),
            cbk_coins=400,
            status=Cashback.Status.PENDING
        )
        CashbackService.transition_status(
            cashback_id=cashback.id,
            new_status=Cashback.Status.APPROVED,
            admin_user=self.super_admin
        )

        ref.refresh_from_db()
        self.user1.wallet.refresh_from_db()
        self.assertEqual(ref.status, Referral.Status.REWARDED)
        self.assertEqual(self.user1.wallet.coin_balance, 100)

    # 6. Audit Logging Tests
    def test_audit_log_created_on_manual_adjustment(self):
        wallet = self.user1.wallet
        CoinService.credit_coins(
            wallet_id=wallet.id,
            amount_coins=250,
            tx_type=WalletTransaction.Type.MANUAL_CREDIT,
            description='Customer appeasement credit',
            created_by=self.super_admin
        )
        audit_exists = AuditLog.objects.filter(
            action='MANUAL_COIN_CREDIT',
            entity='Wallet',
            entity_id=str(wallet.id)
        ).exists()
        self.assertTrue(audit_exists)

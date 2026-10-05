import os
import secrets
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from accounts.models import User
from wallets.models import Wallet, WalletTransaction
from wallets.services import CoinService
from merchants.models import Merchant
from affiliate.models import AffiliateClick
from cashback.models import Cashback, CashbackStatusHistory
from redemptions.models import Redemption, RedemptionStatusHistory
from referrals.models import Referral
from promotions.models import Promotion

class Command(BaseCommand):
    help = 'Seeds realistic development-only demo data for Cash Back Kart (CBK).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing CBK demo seed process..."))

        admin_email = os.environ.get('DEMO_ADMIN_EMAIL', 'admin@cashbackkart.in')
        admin_password = os.environ.get('DEMO_ADMIN_PASSWORD') or 'Admin@123CBKSecure'

        # 1. Create Administrative Users
        super_admin, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Super',
                'last_name': 'Administrator',
                'phone_number': '+91 98765 43210',
                'role': User.Role.SUPER_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        super_admin.set_password(admin_password)
        super_admin.save()
        self.stdout.write(self.style.SUCCESS(f"[OK] Super Admin ready: {admin_email} (Password: {admin_password})"))

        finance_admin, _ = User.objects.get_or_create(
            email='finance@cashbackkart.in',
            defaults={
                'first_name': 'Finance',
                'last_name': 'Controller',
                'phone_number': '+91 98765 43211',
                'role': User.Role.FINANCE_ADMIN,
                'is_staff': True,
                'is_verified': True,
            }
        )
        finance_admin.set_password(admin_password)
        finance_admin.save()

        ops_admin, _ = User.objects.get_or_create(
            email='ops@cashbackkart.in',
            defaults={
                'first_name': 'Operations',
                'last_name': 'Lead',
                'phone_number': '+91 98765 43212',
                'role': User.Role.OPERATIONS_ADMIN,
                'is_staff': True,
                'is_verified': True,
            }
        )
        ops_admin.set_password(admin_password)
        ops_admin.save()

        # 2. Seed Merchants
        merchants_data = [
            {
                'name': 'Amazon India',
                'slug': 'amazon-india',
                'category': 'marketplaces',
                'website_url': 'https://www.amazon.in',
                'commission_rate': Decimal('10.00'),
                'cbk_reward_rate': Decimal('8.50'),
                'reward_badge': 'TRENDING',
                'is_featured': True,
                'display_order': 1,
            },
            {
                'name': 'Flipkart',
                'slug': 'flipkart',
                'category': 'marketplaces',
                'website_url': 'https://www.flipkart.com',
                'commission_rate': Decimal('14.00'),
                'cbk_reward_rate': Decimal('12.00'),
                'reward_badge': 'POPULAR',
                'is_featured': True,
                'display_order': 2,
            },
            {
                'name': 'Meesho',
                'slug': 'meesho',
                'category': 'fashion',
                'website_url': 'https://www.meesho.com',
                'commission_rate': Decimal('18.00'),
                'cbk_reward_rate': Decimal('15.00'),
                'reward_badge': 'HIGHEST RATE',
                'is_featured': True,
                'display_order': 3,
            },
            {
                'name': 'Myntra',
                'slug': 'myntra',
                'category': 'fashion',
                'website_url': 'https://www.myntra.com',
                'commission_rate': Decimal('12.00'),
                'cbk_reward_rate': Decimal('9.50'),
                'reward_badge': 'FASHION',
                'is_featured': False,
                'display_order': 4,
            },
            {
                'name': 'AJIO',
                'slug': 'ajio',
                'category': 'fashion',
                'website_url': 'https://www.ajio.com',
                'commission_rate': Decimal('13.00'),
                'cbk_reward_rate': Decimal('11.00'),
                'reward_badge': 'EXCLUSIVE',
                'is_featured': False,
                'display_order': 5,
            },
            {
                'name': 'Nykaa',
                'slug': 'nykaa',
                'category': 'beauty',
                'website_url': 'https://www.nykaa.com',
                'commission_rate': Decimal('12.50'),
                'cbk_reward_rate': Decimal('10.50'),
                'reward_badge': 'BEAUTY',
                'is_featured': False,
                'display_order': 6,
            },
            {
                'name': 'Croma',
                'slug': 'croma',
                'category': 'electronics',
                'website_url': 'https://www.croma.com',
                'commission_rate': Decimal('8.00'),
                'cbk_reward_rate': Decimal('6.00'),
                'reward_badge': 'GADGETS',
                'is_featured': False,
                'display_order': 7,
            },
            {
                'name': 'MakeMyTrip',
                'slug': 'makemytrip',
                'category': 'travel',
                'website_url': 'https://www.makemytrip.com',
                'commission_rate': Decimal('10.00'),
                'cbk_reward_rate': Decimal('8.00'),
                'reward_badge': 'TRAVEL',
                'is_featured': False,
                'display_order': 8,
            },
        ]

        merchants = {}
        for m_data in merchants_data:
            merchant, _ = Merchant.objects.get_or_create(
                slug=m_data['slug'],
                defaults=m_data
            )
            merchants[m_data['slug']] = merchant

        self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(merchants)} merchants"))

        # 3. Seed Demo Customers
        customers_info = [
            ('rahul.sharma@example.com', 'Rahul', 'Sharma', '+91 98111 22334'),
            ('priya.patel@example.com', 'Priya', 'Patel', '+91 98222 33445'),
            ('arjun.verma@example.com', 'Arjun', 'Verma', '+91 98333 44556'),
            ('ananya.singh@example.com', 'Ananya', 'Singh', '+91 98444 55667'),
        ]

        customers = []
        for email, first, last, phone in customers_info:
            c, created_c = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'phone_number': phone,
                    'role': User.Role.CUSTOMER,
                    'is_verified': True,
                }
            )
            if created_c:
                c.set_password('DemoUser@123')
                c.save()
            customers.append(c)

        # 4. Referral relationship: Rahul referred Priya
        ref_record, _ = Referral.objects.get_or_create(
            referrer=customers[0],
            referred_user=customers[1],
            defaults={
                'referral_code_used': customers[0].referral_code,
                'status': Referral.Status.REWARDED,
                'reward_coins': 100,
                'qualified_at': timezone.now(),
                'rewarded_at': timezone.now()
            }
        )

        # Credit Rahul's wallet for referral
        rahul_wallet, _ = Wallet.objects.get_or_create(user=customers[0])
        if rahul_wallet.coin_balance == 0:
            CoinService.credit_coins(
                wallet_id=rahul_wallet.id,
                amount_coins=100,
                tx_type=WalletTransaction.Type.REFERRAL_BONUS,
                reference_type='Referral',
                reference_id=str(ref_record.id),
                description=f"Demo Referral Bonus for inviting {customers[1].email}",
                allow_duplicate=True
            )

        # 5. Create Sample Affiliate Clicks
        click1 = AffiliateClick.objects.create(
            user=customers[0],
            merchant=merchants['amazon-india'],
            source='web',
            campaign='festival_rewards',
            status=AffiliateClick.Status.CONVERTED,
            redirect_url='https://www.amazon.in/?cbk_click=demo1'
        )
        click2 = AffiliateClick.objects.create(
            user=customers[1],
            merchant=merchants['flipkart'],
            source='web',
            status=AffiliateClick.Status.CONVERTED,
            redirect_url='https://www.flipkart.com/?cbk_click=demo2'
        )

        # 6. Create Sample Cashbacks
        # Cashback 1: Approved for Rahul (Amazon)
        cb1, cb1_created = Cashback.objects.get_or_create(
            merchant=merchants['amazon-india'],
            order_id='AMZ-2026-9021',
            defaults={
                'user': customers[0],
                'affiliate_click': click1,
                'order_amount': Decimal('4500.00'),
                'commission_amount': Decimal('450.00'),
                'cashback_inr': Decimal('382.50'),
                'cbk_coins': 3825,  # 382.50 * 10
                'status': Cashback.Status.APPROVED,
                'approved_at': timezone.now()
            }
        )
        if cb1_created:
            CoinService.credit_coins(
                wallet_id=rahul_wallet.id,
                amount_coins=3825,
                tx_type=WalletTransaction.Type.CASHBACK,
                reference_type='Cashback',
                reference_id=str(cb1.id),
                description=f"Approved Cashback from Amazon India (Order #AMZ-2026-9021)",
                allow_duplicate=True
            )
            CashbackStatusHistory.objects.create(
                cashback=cb1,
                previous_status='PENDING',
                new_status='APPROVED',
                changed_by=ops_admin,
                reason="Auto-reconciliation network confirmation."
            )

        # Cashback 2: Pending for Priya (Flipkart)
        Cashback.objects.get_or_create(
            merchant=merchants['flipkart'],
            order_id='FLIP-89123',
            defaults={
                'user': customers[1],
                'affiliate_click': click2,
                'order_amount': Decimal('2200.00'),
                'commission_amount': Decimal('308.00'),
                'cashback_inr': Decimal('264.00'),
                'cbk_coins': 2640,
                'status': Cashback.Status.PENDING
            }
        )

        # 7. Create Sample Redemption for Rahul
        # Rahul has 3825 + 100 = 3925 coins.
        # Request a redemption of 1500 coins (= ₹150)
        red, red_created = Redemption.objects.get_or_create(
            user=customers[0],
            coins_deducted=1500,
            defaults={
                'wallet': rahul_wallet,
                'inr_amount': Decimal('150.00'),
                'payout_method': Redemption.PayoutMethod.UPI,
                'payout_identifier': 'rahul.sharma@oksbi',
                'masked_identifier': 'ra***@oksbi',
                'status': Redemption.Status.COMPLETED,
                'utr_number': 'UTR2026091299901',
                'admin_notes': 'Settled via HDFC Bulk UPI payout batch #104',
                'completed_at': timezone.now()
            }
        )
        if red_created:
            CoinService.debit_coins(
                wallet_id=rahul_wallet.id,
                amount_coins=1500,
                tx_type=WalletTransaction.Type.REDEMPTION,
                reference_type='Redemption',
                reference_id=str(red.redemption_id),
                description="Demo Completed UPI Redemption (₹150.00)"
            )
            RedemptionStatusHistory.objects.create(
                redemption=red,
                previous_status='REQUESTED',
                new_status='COMPLETED',
                changed_by=finance_admin,
                reason="UTR verified against nodal bank payout ledger."
            )

        # 8. Seed Sample Promotion
        now = timezone.now()
        Promotion.objects.get_or_create(
            slug='festive-double-cashback',
            defaults={
                'title': 'Diwali Super Saver Fest',
                'description': 'Enjoy 1.5x coin accrual on all fashion and marketplace orders.',
                'bonus_coins': 250,
                'cashback_multiplier': Decimal('1.50'),
                'start_date': now - timezone.timedelta(days=2),
                'end_date': now + timezone.timedelta(days=12),
                'is_active': True,
                'usage_limit': 10000,
            }
        )

        self.stdout.write(self.style.SUCCESS("[OK] Demo data successfully seeded for development!"))

# Cash Back Kart (CBK) — Platform Architecture & Operations Manual

**Cash Back Kart (CBK)** is an enterprise loyalty, digital rewards, and cashback ecosystem engineered for India's digital consumers. Users discover partner merchants (Amazon India, Flipkart, Myntra, Meesho, Nykaa, Croma, MakeMyTrip), shop via verified affiliate links, accumulate **CBK Coins**, and redeem their coins via instant UPI or zero-deduction bank payouts.

---

## Central Financial Rule & Conversion Standard

> **10 CBK Coins = ₹1.00 INR**

- **Coins per INR:** Strictly fixed at `COINS_PER_INR = 10`.
- **Enforcement Layer:** Single source of truth in `wallets.services.CoinService` (also mirrored in `settings.COINS_PER_INR`).
- **Precision:** Uses Python `Decimal` with rounding to 2 decimal places for INR values. Floating-point arithmetic is never used for money calculations.
- **Ledger Invariance:** Wallet balances are never altered ad-hoc. All credits, debits, reversals, and payouts create immutable ledger transactions under row-level database locks (`select_for_update()`).

---

## Workspace Structure

```
coinWEB/
├── backend/                 # Django 6.1.1 + Django REST Framework service
│   ├── config/              # Core project settings, DB engine router, URLs
│   ├── accounts/            # Custom User model, RBAC roles, Token authentication
│   ├── wallets/             # Wallet model, immutable ledger, CoinService
│   ├── merchants/           # Partner merchants, categories, commission & reward rates
│   ├── affiliate/           # Affiliate click telemetry, unique click ID, redirect resolver
│   ├── cashback/            # Cashback claim lifecycle (Pending, Approved, Rejected, Reversed)
│   ├── redemptions/         # UPI/Bank withdrawals, masked identifiers, UTR settlement
│   ├── referrals/           # Referral tracking, unique invite codes, qualification hooks
│   ├── promotions/          # Time-limited booster campaigns & multiplier rules
│   ├── audit/               # Immutable administrative audit logs with diffs & reasons
│   ├── reports/             # Aggregated metrics and live CSV report generation
│   ├── core/                # TimeStampedModel, pagination, seed_demo management command
│   ├── tests/               # Automated unit test suite covering critical financial flows
│   ├── .env.example         # Environment template
│   └── manage.py
│
├── admin/                   # Dedicated Operations Console (SvelteKit 2 + Svelte 5 + Tailwind CSS)
│   ├── src/
│   │   ├── lib/             # API client, auth state store, Lucide icons, reusable UI components
│   │   └── routes/admin/    # Dashboard, users, wallets, transactions, cashback, payouts, reports
│   └── package.json
│
├── frontend/                # Customer-Facing Landing Experience (SvelteKit 2 + Svelte 5)
│   ├── src/                 # Preserved editorial design system (Instrument Serif + Inter)
│   └── package.json
│
└── DESIGN/                  # Original HTML/CSS/JS prototype reference
```

---

## Installation & Environment Setup

### 1. Backend Setup

Activate the Python virtual environment and install dependencies:

```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt # (or python-dotenv pymysql djangorestframework django-cors-headers)
```

Copy `.env.example` to `.env`:

```powershell
cp .env.example .env
```

#### Database Configuration

CBK supports dynamic database abstraction through the `DATABASE_ENGINE` variable in `.env`:

- **Development (SQLite default):**
  ```env
  DATABASE_ENGINE=sqlite
  ```
- **Staging / Production (MySQL):**
  ```env
  DATABASE_ENGINE=mysql
  DB_NAME=cbk_db
  DB_USER=cbk_user
  DB_PASSWORD=your_secure_password
  DB_HOST=127.0.0.1
  DB_PORT=3306
  ```

Run migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Seed initial development data (creates Super Admin, merchants, sample users, transactions):

```powershell
python manage.py seed_demo
```

*Default Demo Credentials:*
- **Email:** `admin@cashbackkart.in`
- **Password:** `Admin@123CBKSecure` (or configured via `DEMO_ADMIN_PASSWORD` in `.env`)

Run Django dev server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

---

### 2. Admin Dashboard Setup (`admin/`)

The admin dashboard is a dedicated fintech operations console built with Svelte 5, SvelteKit, and Tailwind CSS.

```powershell
cd admin
npm install
npm run dev
```

Admin dashboard runs at `http://localhost:5174/admin/login`.

---

### 3. Customer Frontend (`frontend/`)

The customer-facing application runs independently:

```powershell
cd frontend
npm install
npm run dev
```

Customer storefront runs at `http://localhost:5173`.

---

## Running Automated Tests

Run the complete backend test suite:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py test tests
```

Tests verify:
1. User registration, referral code generation, and initial wallet setup.
2. Token authentication and invalid login rejection.
3. Strict 10:1 coin-to-INR conversions using Decimal precision.
4. Atomic wallet credits, debits, and balance integrity under row-level locks.
5. Insufficient funds prevention and duplicate credit prevention.
6. Cashback lifecycle: Pending → Approved (with automated coin crediting) → Reversal.
7. Redemption requests with atomic balance holds and cancellation with automatic coin refunds.
8. Referral tree attribution and bonus qualification on first approved purchase.
9. Audit log creation on manual adjustments with previous/new value diffs.

---

## REST API Overview

| Group | Method | Endpoint | Description |
|---|---|---|---|
| **Auth** | `POST` | `/api/auth/register/` | Register customer account |
| **Auth** | `POST` | `/api/auth/login/` | Authenticate & retrieve DRF token |
| **Auth** | `GET` | `/api/auth/me/` | Current user profile & balances |
| **Wallet** | `GET` | `/api/wallet/` | Current user wallet balance |
| **Wallet** | `GET` | `/api/wallet/transactions/` | Current user coin ledger |
| **Merchants** | `GET` | `/api/merchants/` | Public active merchants directory |
| **Affiliate** | `POST` | `/api/affiliate/click/<slug>/` | Track click & resolve target tracking link |
| **Cashback** | `GET` | `/api/cashback/` | Current user cashback claims |
| **Redemptions** | `GET, POST` | `/api/redemptions/` | List or request UPI/Bank withdrawal |
| **Referrals** | `GET` | `/api/referrals/` | User referral stats & invite link |
| **Promotions** | `GET` | `/api/promotions/` | Active seasonal booster campaigns |
| **Admin** | `GET` | `/api/admin/dashboard/metrics/` | Aggregated metrics & chart data |
| **Admin** | `POST` | `/api/admin/manual-adjustment/` | Finance Admin manual credit/debit |
| **Admin** | `POST` | `/api/admin/cashback/<id>/transition/` | Approve, reject, or reverse claim |
| **Admin** | `POST` | `/api/admin/redemptions/<id>/transition/` | Process, settle (UTR), or fail payout |
| **Admin** | `GET` | `/api/admin/reports/<entity>/csv/` | Live CSV data export downloads |
| **Admin** | `GET` | `/api/admin/audit-logs/` | Non-repudiable admin audit trail |

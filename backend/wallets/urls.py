from django.urls import path
from .views import (
    UserWalletView,
    UserTransactionListView,
    AdminWalletListView,
    AdminTransactionListView,
    AdminTransactionDetailView,
    AdminManualAdjustmentView,
)

urlpatterns = [
    # Customer APIs
    path('wallet/', UserWalletView.as_view(), name='user-wallet'),
    path('wallet/transactions/', UserTransactionListView.as_view(), name='user-transactions'),

    # Admin APIs
    path('admin/wallets/', AdminWalletListView.as_view(), name='admin-wallets-list'),
    path('admin/transactions/', AdminTransactionListView.as_view(), name='admin-transactions-list'),
    path('admin/transactions/<uuid:tx_id>/', AdminTransactionDetailView.as_view(), name='admin-transaction-detail'),
    path('admin/manual-adjustment/', AdminManualAdjustmentView.as_view(), name='admin-manual-adjustment'),
]

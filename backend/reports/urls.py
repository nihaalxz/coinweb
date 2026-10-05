from django.urls import path
from .views import (
    AdminDashboardMetricsView,
    ExportUsersReportView,
    ExportTransactionsReportView,
    ExportCashbackReportView,
    ExportRedemptionsReportView,
)

urlpatterns = [
    path('admin/dashboard/metrics/', AdminDashboardMetricsView.as_view(), name='admin-dashboard-metrics'),
    path('admin/reports/users/csv/', ExportUsersReportView.as_view(), name='export-users-csv'),
    path('admin/reports/transactions/csv/', ExportTransactionsReportView.as_view(), name='export-transactions-csv'),
    path('admin/reports/cashback/csv/', ExportCashbackReportView.as_view(), name='export-cashback-csv'),
    path('admin/reports/redemptions/csv/', ExportRedemptionsReportView.as_view(), name='export-redemptions-csv'),
]

from django.urls import path
from .views import (
    UserReferralSummaryView,
    AdminReferralListView,
)

urlpatterns = [
    # Customer API
    path('referrals/', UserReferralSummaryView.as_view(), name='user-referrals'),

    # Admin API
    path('admin/referrals/', AdminReferralListView.as_view(), name='admin-referrals-list'),
]

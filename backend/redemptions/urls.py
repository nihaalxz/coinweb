from django.urls import path
from .views import (
    UserRedemptionListCreateView,
    AdminRedemptionListView,
    AdminRedemptionDetailView,
    AdminRedemptionTransitionView,
)

urlpatterns = [
    # Customer APIs
    path('redemptions/', UserRedemptionListCreateView.as_view(), name='user-redemptions'),

    # Admin APIs
    path('admin/redemptions/', AdminRedemptionListView.as_view(), name='admin-redemptions-list'),
    path('admin/redemptions/<uuid:redemption_id>/', AdminRedemptionDetailView.as_view(), name='admin-redemptions-detail'),
    path('admin/redemptions/<uuid:redemption_id>/transition/', AdminRedemptionTransitionView.as_view(), name='admin-redemptions-transition'),
]

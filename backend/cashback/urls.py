from django.urls import path
from .views import (
    UserCashbackListView,
    AdminCashbackListView,
    AdminCashbackDetailView,
    AdminCashbackTransitionView,
)

urlpatterns = [
    # Customer API
    path('cashback/', UserCashbackListView.as_view(), name='user-cashback-list'),

    # Admin APIs
    path('admin/cashback/', AdminCashbackListView.as_view(), name='admin-cashback-list'),
    path('admin/cashback/<int:pk>/', AdminCashbackDetailView.as_view(), name='admin-cashback-detail'),
    path('admin/cashback/<int:pk>/transition/', AdminCashbackTransitionView.as_view(), name='admin-cashback-transition'),
]

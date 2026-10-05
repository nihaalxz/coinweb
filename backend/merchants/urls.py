from django.urls import path
from .views import (
    MerchantPublicListView,
    MerchantPublicDetailView,
    AdminMerchantListCreateView,
    AdminMerchantDetailUpdateView,
)

urlpatterns = [
    # Customer / Public APIs
    path('merchants/', MerchantPublicListView.as_view(), name='merchants-list'),
    path('merchants/<slug:slug>/', MerchantPublicDetailView.as_view(), name='merchants-detail'),

    # Admin APIs
    path('admin/merchants/', AdminMerchantListCreateView.as_view(), name='admin-merchants-list'),
    path('admin/merchants/<int:pk>/', AdminMerchantDetailUpdateView.as_view(), name='admin-merchants-detail'),
]

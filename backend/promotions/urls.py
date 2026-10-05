from django.urls import path
from .views import (
    PromotionPublicListView,
    AdminPromotionListCreateView,
    AdminPromotionDetailUpdateView,
)

urlpatterns = [
    # Customer API
    path('promotions/', PromotionPublicListView.as_view(), name='promotions-active'),

    # Admin APIs
    path('admin/promotions/', AdminPromotionListCreateView.as_view(), name='admin-promotions-list'),
    path('admin/promotions/<int:pk>/', AdminPromotionDetailUpdateView.as_view(), name='admin-promotions-detail'),
]

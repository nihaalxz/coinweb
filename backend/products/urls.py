from django.urls import path
from .views import (
    ProductPublicListView,
    ProductPublicDetailView,
    ProductClickTrackView,
    AdminProductListCreateView,
    AdminProductDetailUpdateView,
    LiveProductSearchView,
)

urlpatterns = [
    # ── Live SerpAPI product search (real-time Google Shopping) ──────────────
    path('products/live/', LiveProductSearchView.as_view(), name='products-live-search'),

    # ── Customer / Public APIs (DB-backed catalog) ────────────────────────────
    path('products/', ProductPublicListView.as_view(), name='products-list'),
    path('products/<int:id>/', ProductPublicDetailView.as_view(), name='products-detail'),
    path('products/<int:id>/click/', ProductClickTrackView.as_view(), name='products-click-track'),

    # ── Admin APIs ────────────────────────────────────────────────────────────
    path('admin/products/', AdminProductListCreateView.as_view(), name='admin-products-list'),
    path('admin/products/<int:pk>/', AdminProductDetailUpdateView.as_view(), name='admin-products-detail'),
]

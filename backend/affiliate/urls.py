from django.urls import path
from .views import (
    CreateClickAndRedirectView,
    ConvertLinkView,
    AdminAffiliateClickListView,
    AdminAffiliateClickDetailView,
)

urlpatterns = [
    # Customer / Redirect tracking
    path('affiliate/click/<slug:merchant_slug>/', CreateClickAndRedirectView.as_view(), name='affiliate-click'),
    path('affiliate/convert-link/', ConvertLinkView.as_view(), name='affiliate-convert-link'),

    # Admin APIs
    path('admin/affiliate-clicks/', AdminAffiliateClickListView.as_view(), name='admin-affiliate-clicks-list'),
    path('admin/affiliate-clicks/<uuid:click_id>/', AdminAffiliateClickDetailView.as_view(), name='admin-affiliate-clicks-detail'),
]

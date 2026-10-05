"""
URL configuration for Cash Back Kart (CBK) project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # REST APIs
    path('api/auth/', include('accounts.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('wallets.urls')),
    path('api/', include('merchants.urls')),
    path('api/', include('affiliate.urls')),
    path('api/', include('cashback.urls')),
    path('api/', include('redemptions.urls')),
    path('api/', include('referrals.urls')),
    path('api/', include('promotions.urls')),
    path('api/', include('products.urls')),
    path('api/', include('audit.urls')),
    path('api/', include('reports.urls')),
]
